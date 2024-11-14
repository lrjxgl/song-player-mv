from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
import gradio as gr
import time
import re
import json
import os
import glob
def get_sorted_files(directory,ftype=".png"):
    # 使用os.listdir获取指定目录下的所有文件和目录名
    files = os.listdir(directory)
    
    # 定义一个用于排序的关键字函数，提取文件名中的数字部分并转为整数
    def sort_key(file_name):
        return int(file_name.split('.')[0])  # 提取文件名（去掉扩展名）并转为整数
    
    # 对mp4_files中的文件名按照数字大小进行排序
    sorted_files = sorted(files, key=sort_key)
     
    fileList=[]
    for i in range(len(sorted_files)):
        fileList.append(f"./output/{sorted_files[i]}")
    return fileList
def create_video_from_images(folder_path,music_path, output_video_path, fps=30):
    # 获取文件夹中的所有图片文件
    images = get_sorted_files(folder_path,".png")
    if not images:
        print("No images found in the specified folder.")
        return

    # 创建一个Clip对象列表
    clips = [ImageSequenceClip(images, fps=fps)]
    background_music = AudioFileClip(music_path)
    
    # 设置视频的音频轨道
    clips[0] = clips[0].set_audio(background_music)
    
    # 写入视频文件
    clips[0].write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    
def get_audio_duration(file_path):
    clip = AudioFileClip(file_path)
    duration = clip.duration
    return int(duration*100)
def parse_lyrics(lyric):
    # 拆分行
    lines = [line.strip() for line in lyric.split('\n') if line.strip()]
    
    # 定义正则表达式模式
    pattern = re.compile(r'\[(\d+)\](.*)')
    
    # 处理每一行
    parsed_lines = []
    for line in lines:
        match = pattern.match(line)
        if match:
            time, text = match.groups()
            parsed_lines.append({'time': int(time)*100, 'text': text})
    
    return parsed_lines


def drawPlayer(song,stime):    
    # 创建一个新的图像，这里使用RGB模式
    bgcolor=(23, 136, 222)
    color=(230, 230, 230)
    activeColor=(255, 255, 255)
    if song["skins"]==1:
         bgcolor=(133, 82,161)
    elif song["skins"]==2:
         bgcolor=(198,113,113)
    elif song["skins"]==2:
         bgcolor=(239,91,156)
    elif song["skins"]==3:
         bgcolor=(0,125,101)
    elif song["skins"]==4:
         bgcolor=(36,36,36)
    elif song["skins"]==5:
         bgcolor=(105,89,205)
    elif song["skins"]==6:
         bgcolor=(238,0,0)
    img = Image.new('RGBA', (512, 768), color = bgcolor + (255,))  # RGBA, 最后一个是Alpha通道
    try:
       img_with_logo = Image.open(song["logo"]).convert('RGBA')  # 确保logo也是RGBA模式
       # 创建一个与logo图像等大的透明图像
       mask = Image.new('L', img_with_logo.size, 0)
        
       draw = ImageDraw.Draw(mask)
       draw.ellipse((0, 0) + img_with_logo.size, fill=255)
        
       # 使用mask来将原始图像转换成圆形
       img_with_logo.putalpha(mask)
        
       # 旋转图像
       img_with_logo = img_with_logo.rotate(-5*stime/100, expand=True)
        
       # 缩放logo图像
       img_with_logo.thumbnail((200, 200))
        
       # 将logo图像粘贴到主图像上
       img.paste(img_with_logo, (img.width - img_with_logo.width-30, 60), img_with_logo)
    except FileNotFoundError:
        print("无法找到图像文件 demo.webp")
    # 加载字体文件，这里假设您的系统中安装了Arial字体
    font="font/Alibaba_PuHuiTi_2.0_55_Regular_55_Regular.ttf"
    f24 = ImageFont.truetype(font, 24)
    f20 = ImageFont.truetype(font, 20)
    f16 = ImageFont.truetype(font, 16)

    # 创建一个绘图对象
    d = ImageDraw.Draw(img)

    # 歌名
    
    d.text((30, 40), song["title"], font=f24, fill=color)

 
    d.text((30, 80), song["geshou"], font=f20, fill=color)

    ciqu="词 "+song["ci"]+"  曲 "+song["qu"] 
    d.text((30, 110), ciqu, font=f20, fill=color)

    #d.text((130, 660), " 如果你唱的打动我 \n 我把这首歌送给你", font=f24, fill=(255, 255, 255))
    
    maxLen=12
    startY=160
    arr=parse_lyrics(song["lyric"])
     
    minLine=0
    maxLine=0
    startIndex=0
    activeIndex=0
    arr_len=len(arr)
    for i in range(arr_len):        
        if arr_len>i+1: 
            if arr[i]["time"]<=stime  and arr[i+1]["time"]>stime:
                activeIndex=i
        elif arr_len-1==i:
            if arr[i]["time"]<=stime:
                activeIndex=i
        if arr[i]["time"]<=stime:
            minLine=minLine+1
    if minLine>=maxLen/2:
        startIndex=minLine-int(maxLen/2)
     
       
    endIndex=startIndex+maxLen
    if endIndex>arr_len:
        endIndex=arr_len
    if endIndex-startIndex<maxLen:
        startIndex=endIndex-maxLen
    for i in range(startIndex,endIndex):
        if i==activeIndex:
            d.text((30, startY), arr[i]["text"], font=f24, fill=activeColor)
            startY+=50
        else:
            d.text((30, startY), arr[i]["text"], font=f20, fill=color)
            startY+=35
        i=i+1
            
 
    img.save('output/'+str(stime)+'.png', "PNG")
def clear_files(del_dir):  
    files = os.listdir(del_dir)
    for filename in os.listdir(del_dir):
            file_path = os.path.join(del_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)



def song2mv(title,geshou,ci,qu,lyric,logo,skins,music):
    song={
        "title":title,
        "geshou":geshou,
        "ci":ci,
        "qu":qu,
        "lyric":lyric,
        "logo":logo,
        "skins":skins
    }
    t=get_audio_duration(music)
    print(t)
    fps=5    
    folder_path = 'output'  
    clear_files(folder_path)  
    for i in range(t):
        if i%(100/fps)==0:    
            drawPlayer(song,i)
    
    output_video_path = 'video/'+str(time.time())+'.mp4'  # 输出视频文件路径           
    create_video_from_images( folder_path,music, output_video_path,fps) 
    return output_video_path 

with gr.Blocks() as demo:
    gr.Markdown("""
    # 音乐MV生成器
    """)
    with gr.Row():
        with gr.Column():
            with gr.Row():
                title=gr.Textbox(label="歌名",value="")
                geshou=gr.Textbox(label="歌手",value="")
            with gr.Row():
                ci=gr.Textbox(label="词",value="")
                qu=gr.Textbox(label="曲",value="")
            lyric=gr.Textbox(label="歌词",value="",lines=8)
            
            skins=gr.Slider(minimum=0,maximum=6,step=1,label="风格",value=0)
            

            btn=gr.Button("生成MV")
            
        with gr.Column():
            with gr.Row():
                music=gr.Audio(label="音乐",type="filepath")
                logo=gr.Image(label="logo",type="filepath")
            video=gr.Video(label="MV")
    btn.click(fn=song2mv,inputs=[title,geshou,ci,qu,lyric,logo,skins,music],outputs=video)
    demo.launch(debug=True)