import re, math, os
from moviepy.editor import *
import imghdr
from scipy.stats import uniform, norm
import numpy as np
import requests

def file_to_subtitles(filename):
    """ Converts a srt file into subtitles.

    The returned list is of the form ``[((ta,tb),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """
    
    def is_string(obj):
        try:
            return isinstance(obj, basestring)
        except NameError:
            return isinstance(obj, str)
    
    def cvsecs(time):
        """ Will convert any time into seconds. 

        If the type of `time` is not valid, 
        it's returned as is. 

        Here are the accepted formats::

        >>> cvsecs(15.4)   # seconds 
        15.4 
        >>> cvsecs((1, 21.5))   # (min,sec) 
        81.5 
        >>> cvsecs((1, 1, 2))   # (hr, min, sec)  
        3662  
        >>> cvsecs('01:01:33.045') 
        3693.045
        >>> cvsecs('01:01:33,5')    # coma works too
        3693.5
        >>> cvsecs('1:33,5')    # only minutes and secs
        99.5
        >>> cvsecs('33.5')      # only secs
        33.5
        """
        factors = (1, 60, 3600)

        if is_string(time):     
            time = [float(f.replace(',', '.')) for f in time.split(':')]

        if not isinstance(time, (tuple, list)):
            return time

        return sum(mult * part for mult, part in zip(factors, reversed(time)))

    times_texts = []
    current_times = None
    current_text = ""
    with open(filename,'r', encoding='utf-8') as f:
        for line in f:
            times = re.findall("([0-9]*:[0-9]*:[0-9]*,[0-9]*)", line)
            if times:
                current_times = [cvsecs(t) for t in times]
            elif line.strip() == '':
                if current_times:
                    times_texts.append((current_times, current_text.strip('\n')))
                current_times, current_text = None, " "
            elif current_times:
                current_text += line

    return times_texts

def subtitles_to_file(subtitles, save_dir):
    """
    The reverse of the function file_to_subtitles. This function will write the subtitles into a srt file.
    """
    def sec_to_time(total_secs):
        hr = math.floor(total_secs/3600)
        min = math.floor(math.floor(total_secs-hr*3600)/60)
        sec = math.floor(total_secs % 60)
        remains = round(total_secs % 1 * 1000)

        if hr < 10:
            hr_str = '0'+str(hr)
        else:
            hr_str = str(hr)
        if min < 10:
            min_str = '0'+str(min)
        else:
            min_str = str(min)
        if sec < 10:
            sec_str = '0'+str(sec)
        else:
            sec_str = str(sec)
        if remains < 10:
            remains_str = '00'+str(remains)
        elif remains < 100:
            remains_str = '0'+str(remains)
        else:
            remains_str = str(remains)

        return hr_str+':'+min_str+':'+sec_str+','+remains_str  
    
    with open(save_dir, 'w', encoding='utf-8') as f:
        for idx, subtitle in enumerate(subtitles):
            f.write(str(idx+1)+'\n')
            f.write(sec_to_time(subtitle[0][0])+' --> '+sec_to_time(subtitle[0][1])+'\n')
            f.write(subtitle[1])
            f.write('\n\n')
            
def make_empty_audio(filename, duration=3):
    make_frame = lambda t: 2*[ 0*t ]
    clip = AudioClip(make_frame, duration=duration, fps=44100)
    clip.write_audiofile(filename)
    

def color_clip(size, duration, fps=25, color=(0,0,0), output='color.mp4'):
    ColorClip(size, color, duration=duration).write_videofile(os.path.join(output_dir,output), fps=fps)
    
def get_img_video_files_list(directory):
    img_files = []
    video_files = []
    video_extensions = ['.mp4', '.avi', '.flv', '.rmvb']
    for file in os.listdir(directory):
        file_path = os.path.join(directory,file)
        if os.path.isfile(file_path):
            if imghdr.what(file_path):
                img_files.append(file_path)
            for ext in video_extensions:
                if file_path.endswith(ext):
                    video_files.append(file_path)
    return img_files, video_files
    
    
def gaussian_sampling_of_timepoints(clips_number, video_duration, clip_length, steps):
    
    """
    This function is to sample the starting timepoints from the same video for cutting clip in the way that the cut clips overlap as little     as possible
    """

    def gaussian_peak(scale):
        return (2*np.pi*scale**2)**(-0.5)

    def redistribute(dist,t_arr,scale):
        dist = dist/sum(dist)
        loc = np.random.choice(t_arr,p=dist)
        gaussian_mask = norm.pdf(t_arr,loc,scale)
        dist = dist*(1-gaussian_mask/gaussian_peak(scale))
        return loc,dist

    t_arr = np.linspace(0,video_duration-clip_length,steps)

    dist = uniform.pdf(t_arr,t_arr[0],t_arr[-1])
    dist = dist/sum(dist)

    timepoints_list = []

    for i in range(clips_number):
        timepoint,dist = redistribute(dist,t_arr,clip_length)
        dist[dist<0]=0
        dist = dist/sum(dist)
        timepoints_list.append(timepoint)
    
    return timepoints_list
    
    
#---------------------------------------------------------------------------
# Add margins

def get_suitable_margin(width, height):
    if float(width/height) < 16./9.:
        margin = int((16*height-9*width)/18)
        return {'left': margin, 'right':margin, 'top':0, 'bottom':0}
    elif float(width/height) > 16./9.:
        margin = int((9*width-16*height)/32)
        return {'left': 0, 'right': 0, 'top': margin, 'bottom': margin}
    else:
        return {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
    
def add_margin_to_clip(clip):
    width, height = clip.size[0], clip.size[1]
    margin_dict = get_suitable_margin(width, height)
    left, right, top, bottom = margin_dict['left'], margin_dict['right'], margin_dict['top'], margin_dict['bottom']
    return clip.margin(left=left, right=right, top=top, bottom=bottom)

def save_img_with_margin(img_path):
    clip = ImageClip(img_path, duration=1)
    clip = add_margin_to_clip(clip).resize(video_size_dict['1080p'])
    clip.save_frame(img_path)

#---------------------------------------------------------------------------------

def download_image(url, directory):
    img_data = requests.get(image_url).content
    with open(directory, 'wb') as handler:
        handler.write(img_data)
