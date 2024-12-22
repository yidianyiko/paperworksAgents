from camel.models import FishAudioModel
import os
def generate_speech(prompt, storage_path):
    """
    生成语音并保存到指定路径
    
    参数:
    prompt (str): 需要转换成语音的文本提示
    storage_path (str): 音频文件的保存路径
    
    返回:
    IPython.display.Audio: 音频对象,可用于播放
    """
    # 初始化FishAudio模型
    audio_models = FishAudioModel()
    
    # 设置API密钥
   
    
    # 将文本转换为语音并保存
    audio_models.text_to_speech(input=prompt, storage_path=storage_path)
    
    # 返回音频对象
    return Audio(storage_path, autoplay=False)