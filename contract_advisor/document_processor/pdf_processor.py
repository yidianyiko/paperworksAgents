import os
import shutil
from camel.loaders import ChunkrReader

def process_pdf_document(source_pdf_path, api_key):
    """
    处理PDF文档并返回Chunkr的分析结果
    
    参数:
    source_pdf_path (str): 源PDF文件的路径
    api_key (str): Chunkr API密钥
    
    返回:
    dict: Chunkr处理后的输出结果
    """
    try:
        # 设置API密钥
        os.environ["CHUNKR_API_KEY"] = api_key
        
        # 创建本地数据目录
        os.makedirs('local_data', exist_ok=True)
        
        # 设置目标文件路径
        destination_path = "local_data/temp_document.pdf"
        
        # 复制文件到本地数据目录
        shutil.copy2(source_pdf_path, destination_path)
        
        # 初始化ChunkrReader
        chunkr_reader = ChunkrReader()
        
        # 提交文档处理任务
        task_id = chunkr_reader.submit_task(file_path=destination_path)
        
        # 获取处理结果
        chunkr_output = chunkr_reader.get_task_output(task_id, max_retries=10)
        
        # 清理临时文件
        if os.path.exists(destination_path):
            os.remove(destination_path)
            
        return chunkr_output
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return None
