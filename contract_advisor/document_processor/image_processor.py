import os
import shutil
from PIL import Image
from camel.loaders import ChunkrReader
import io

def get_image_files(directory):
    """
    获取指定目录下的所有图片文件
    
    参数:
    directory (str): 图片所在的目录路径
    
    返回:
    list: 图片文件路径列表
    """
    # 支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
    image_paths = []
    
    try:
        # 获取目录下所有文件
        files = os.listdir(directory)
        
        # 筛选图片文件
        for file in sorted(files):  # 使用sorted确保文件顺序一致
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(directory, file)
                image_paths.append(full_path)
                
        return image_paths
        
    except Exception as e:
        print(f"获取图片文件列表时发生错误: {str(e)}")
        return []

def merge_images(image_paths):
    """
    将多张图片垂直拼接成一张图片
    
    参数:
    image_paths (list): 图片文件路径列表
    
    返回:
    PIL.Image: 拼接后的图片
    """
    try:
        if not image_paths:
            raise ValueError("没有找到图片文件")
            
        # 打开所有图片
        images = [Image.open(path) for path in image_paths]
        
        # 计算拼接后的图片尺寸
        total_height = sum(img.size[1] for img in images)
        max_width = max(img.size[0] for img in images)
        
        # 创建新图片
        merged_image = Image.new('RGB', (max_width, total_height))
        
        # 垂直拼接图片
        y_offset = 0
        for img in images:
            # 如果图片宽度小于最大宽度，居中放置
            x_offset = (max_width - img.size[0]) // 2
            merged_image.paste(img, (x_offset, y_offset))
            y_offset += img.size[1]
            
        return merged_image
        
    except Exception as e:
        print(f"图片拼接过程中发生错误: {str(e)}")
        return None

def process_images_from_directory(directory, api_key):
    """
    处理指定目录下的所有图片并返回Chunkr的分析结果
    
    参数:
    directory (str): 图片所在的目录路径
    api_key (str): Chunkr API密钥
    
    返回:
    dict: Chunkr处理后的输出结果
    """
    try:
        # 设置API密钥
        os.environ["CHUNKR_API_KEY"] = api_key
        
        # 创建本地数据目录
        os.makedirs('local_data', exist_ok=True)
        
        # 获取目录下的所有图片
        image_paths = get_image_files(directory)
        if not image_paths:
            print("指定目录下没有找到图片文件")
            return None
            
        # 拼接图片
        merged_image = merge_images(image_paths)
        if merged_image is None:
            return None
            
        # 设置临时文件路径
        temp_image_path = "local_data/temp_merged_image.png"
        
        # 保存拼接后的图片
        merged_image.save(temp_image_path)
        
        # 初始化ChunkrReader
        chunkr_reader = ChunkrReader()
        
        # 提交图片处理任务
        task_id = chunkr_reader.submit_task(file_path=temp_image_path)
        
        # 获取处理结果
        chunkr_output = chunkr_reader.get_task_output(task_id, max_retries=10)
        
        # 清理临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            
        return chunkr_output
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return None

# 使用示例
# directory = 'path/to/your/images'
# api_key = 'your_api_key'
# result = process_images_from_directory(directory, api_key)