from scrape_wiki import *
from moviepy.editor import *
from tools import *
import gtts
import shutil
import os
from download_images import *

tmp_dir = r'.\tmp'
output_dir = r'.\輸出'
media_source_dir = r'.\片源'
bgm_dir = r'.\音樂'
media_dir = r'.\media'

subtitles_path = os.path.join(output_dir, 'subtitles.srt')
narration_path = os.path.join(output_dir, 'text.mp3')

new_para_interval = 1.5

def get_subtitles_from_section(section):
    return get_subtitles_from_textfile(s2t(section['content'].strip('\n')))

def generate_audio_files(section, new_para_interval=new_para_interval, lang="zh-tw"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    text = get_subtitles_from_section(section)
    if text == []:
        return 0
    
    if not section['title']:
        audio_filename = 'summary'
    else:
        audio_filename = section['title']
    
    processed_sentences = [sentence.strip("\n").strip(" ") for sentence in text]
    subtitles = []
    clips = []
    time_pt = 0

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    audio_filename = os.path.join(output_dir, audio_filename + ".mp3")

    for idx, sentence in enumerate(processed_sentences):
        if len(sentence)!=0:
            tts=gtts.gTTS(sentence, lang=lang)
            filename=os.path.join(tmp_dir,"audio"+str(idx)+".mp3")
            tts.save(filename)
            audioclip = AudioFileClip(filename)
            clips.append(audioclip)
            duration = audioclip.duration
            time_range = [round(time_pt,3), round(time_pt+duration,3)]
            time_pt += duration
            subtitles.append((time_range, sentence))
        else:
            filename=os.path.join(tmp_dir,"audio"+str(idx)+".mp3")
            make_empty_audio(filename, duration=new_para_interval)
            audioclip = AudioFileClip(filename)
            clips.append(audioclip)
            time_range = [round(time_pt,3), round(time_pt+new_para_interval,3)]
            time_pt += new_para_interval
            subtitles.append((time_range, " "))
        if idx == len(processed_sentences)-1:
            filename=os.path.join(tmp_dir,"audio"+str(idx+1)+".mp3")
            make_empty_audio(filename, duration=new_para_interval)
            audioclip = AudioFileClip(filename)
            clips.append(audioclip)
            time_range = [round(time_pt,3), round(time_pt+new_para_interval,3)]
            time_pt += new_para_interval
            subtitles.append((time_range, " ")) 

    concat_clip = concatenate_audioclips(clips)
    concat_clip.write_audiofile(audio_filename)

    audiofile_no = len(processed_sentences)
    shutil.rmtree(tmp_dir)
    subtitles_to_file(subtitles,os.path.join(output_dir,audio_filename + '.srt'))
    
def get_title_image_dict(sections):
    title_image_dict = dict()
    for section in sections:
        title_image_dict[section['title']] = []
        if 'images' in section:
            for image in section['images']:
                if not section['title']:
                    try:
                        title_image_dict[section['title']].append((section['main_image_url'], 'main image'))
                    except:
                        print("No main image.")
                title_image_dict[section['title']].append((image['url'],image['metadata'][-1]))
        return title_image_dict
    
def download_main_image(sections, title_image_dict, main_title):
    if 'main_image_url' in sections[0]:
        url = sections[0]['main_image_url']
        download_image(url, os.path.join(output_dir, 'main_image.jpg'))
    else:
        download_image_from_word(main_title,output_dir)
    if not os.path.isfile(os.path.join(output_dir,'main_image.jpg')):
        print("No main image!")
        
video_size_dict = {'144p':(256,144), 
                   '240p':(426,240), 
                   '360p':(640,360),
                   '480p':(852,480),
                   '720p':(1280,720), 
                   '1080p':(1920,1080)}

def make_transition_clip(title):
    clip_duration = 3
    fontsize = 100
    font = 'DFKai-SB'
    txt_color = 'black'
    bg_file = r'.\media\mao.jpg'
    audio_file = r'.\media\transition.wav'

    image_clip = ImageClip(bg_file, duration=clip_duration)
    image_video_clip = CompositeVideoClip([image_clip]).set_duration(clip_duration)

    text_clip = TextClip(title, fontsize=fontsize, font=font, color=txt_color).set_position('center')
    im_width, im_height = text_clip.size
    color_clip = ColorClip(size=(int(im_width*1.1), int(im_height*1.4)),
                           color=(255, 0, 255))
    color_clip = color_clip.set_opacity(.5)
    clip_to_overlay = CompositeVideoClip([color_clip, text_clip])
    clip_to_overlay = clip_to_overlay.set_position('center')

    new_video_clip = CompositeVideoClip([image_video_clip, clip_to_overlay]).set_duration(clip_duration)
    new_video_clip.audio = AudioFileClip(audio_file)
    new_video_clip.write_videofile(title+'_transition.mp4',fps=30)


def download_main_image(sections, title_image_dict, main_title):
    img_path = os.path.join(output_dir, 'main_image.jpg')
    if 'main_image_url' in sections[0]:
        url = sections[0]['main_image_url']
        download_image(url, img_path)
    else:
        download_image_from_word(main_title,output_dir)
    if not os.path.isfile(img_path):
        print("No main image!")
    else:
        save_img_with_margin(img_path)
        
        
def download_section_images(section, title_image_dict):
    urls = list(zip(*title_image_dict[section['title']]))[0]
    if not section['title']:
        title = 'summary'
    else:
        title = section['title']
    print(title + ': Total images: ' + str(len(urls)))
    for idx,url in enumerate(urls):
        img_path = os.path.join(output_dir,title+'_'+str(idx+1)+'.jpg')
        try:
            download_image(url,img_path)
            save_img_with_margin(img_path)
        except Exception as e:
            print("Downloading image " + str(idx+1) + " failed.")
    # Resize
    

def make_section_clip(section, title_image_dict, main_image_url):
    if section['level'] == 1:
        make_transition_clip(section['title'])
    if not section['title']:
        title = 'summary'
    else:
        title = section['title']
    imgfiles_list = []
    for file in os.listdir(output_dir):
        if file.endswith('.jpg'):
            if file.split('_')[0] == title:
                imgfiles_list.append(os.path.join(output_dir, file))
    img_num = len(imgfiles_list)
    img_clips = []
            
    audiofile_dir = os.path.join(output_dir,title + '.mp3')
    outputfile_dir = os.path.join(output_dir,title + '.mp4')
    if os.path.isfile(audiofile_dir):
        audio_clip = AudioFileClip(audiofile_dir)
        duration = audio_clip.duration
        img_duration = duration/img_num
        fps = 1./img_duration
        combined_clip = ImageSequenceClip(imgfiles_list, fps=fps)
        combined_clip.audio = audio_clip
        combined_clip.write_videofile(outputfile_dir,fps=30)
    else:
        return 0