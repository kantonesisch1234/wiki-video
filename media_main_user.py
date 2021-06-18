from text_preprocessing import *
from make_media import *
from math import ceil, floor
import os
import winsound

is_bgm_str = input("\n是否需要背景音樂？(是則輸入y，否則輸入n): ")
is_bgm = bool(is_bgm_str)
bgm_vol = float(input("\n輸入聲量：(0.00為靜音，1.00為最大)"))

height = None
width = None
is_sorted = False
avg_duration = 15
img_duration = 10

time_spread = 5
decay_factor = 0.85
filter_factor = 0.6

fps = 30

# Alarm
duration = 3000  # milliseconds
freq = 920  # Hz

narration_lang = "zh-tw"

video_size_list = [(256,144), (426, 240), (640, 360), (852, 480), (1280, 720), (1920, 1080)]

print("選擇影片質素：")
print("1. 144p")
print("2. 240p")
print("3. 360p")
print("4. 480p")
print("5. 720p")
print("6. 1080p")
video_size_choice = input("輸入數字(1-6)： ")
video_size = video_size_list[int(video_size_choice)-1]

shuffle = False
random_timeframe = False

words_per_line = 20

print("\n背景音樂：")
bgm_list = []
for file in os.listdir(bgm_dir):
    if file.endswith('.mp3'):
	    bgm_list.append(file)

for idx,file in enumerate(bgm_list):
    print(idx+1, ": ", file)
bgm_idx = input("輸入背景音樂號碼：")

bgm_file = bgm_list[int(bgm_idx)-1]

print('\n')
if __name__ == '__main__':
    sentences = get_subtitles_from_textfile('text.txt', lang=narration_lang, words_per_line=words_per_line)
    subtitles = generate_audio_files(sentences, lang=narration_lang)
    narration = AudioFileClip(os.path.join(output_dir,'text.mp3'))
    duration = narration.duration
    input_clip = input_clip = make_clip_by_keyword(subtitles, media_source_dir, output_dir, img_duration=img_duration, steps=2000,
                         time_spread=time_spread, decay_factor=decay_factor, filter_factor=filter_factor, size=video_size, 
                         height=height, width=width,fps=30, is_sorted = is_sorted, avg_duration=avg_duration, 
                         duration_uniformity = 100, gaussian_steps = 10000)
    insert_audio_and_subtitles(input_clip,'output.mp4','text.mp3',subtitles, is_bgm=is_bgm, bgm_vol=bgm_vol, bgm_file=bgm_file)
    winsound.Beep(int(freq), int(duration))