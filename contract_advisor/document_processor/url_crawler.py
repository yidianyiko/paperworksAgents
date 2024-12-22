from camel.loaders import Firecrawl
from camel.retrievers import AutoRetriever
from camel.toolkits import FunctionTool, SearchToolkit
from camel.types import ModelPlatformType, ModelType, StorageType
from camel.embeddings import MistralEmbedding

def scrape_url_content(url):
    """
    从指定URL抓取并清理内容
    
    参数:
        url (str): 要抓取的网页URL
    
    返回:
        str: 清理后的markdown格式内容
        如果发生错误则返回None
    """
    try:
        # 初始化Firecrawl实例
        firecrawl = Firecrawl()
        
        # 抓取并清理内容
        response = firecrawl.scrape(url=url)
        
        # 返回markdown格式的内容
        return response["markdown"]
        
    except Exception as e:
        print(f"抓取内容时发生错误: {str(e)}")
        return None
def retrieve_information_from_urls(urls: list[str], query: str) -> str:
    """从URL列表中检索相关信息
    
    即使某些URL抓取失败,函数也会继续处理其他URL
    
    Args:
        urls (list[str]): 要抓取内容的URL列表
        query (str): 搜索相关信息的查询字符串
    
    Returns:
        str: 基于查询检索到的最相关信息,如果所有URL都失败则返回空字符串
    """
    # 设置Mistral API的token限制和安全阈值(80%)
    MAX_TOKENS = 16384
    SAFE_TOKEN_LIMIT = int(MAX_TOKENS * 0.1)  # 13107 tokens
    CHAR_PER_TOKEN = 4  
    SAFE_CHAR_LIMIT = SAFE_TOKEN_LIMIT * CHAR_PER_TOKEN
    
    aggregated_content = ''
    total_chars = 0
    success = False

    # 抓取并聚合每个URL的内容
    for url in urls:
        try:
            scraped_content = Firecrawl().scrape(url)
            if scraped_content and "markdown" in scraped_content:
                content = scraped_content["markdown"]
                if content:  # 确保内容不为空
                    content_length = len(content)
                    
                    # 检查是否超过安全阈值
                    if total_chars + content_length > SAFE_CHAR_LIMIT:
                        print(f"达到安全阈值 (50% = {SAFE_CHAR_LIMIT} 字符), 停止内容收集")
                        break
                        
                    aggregated_content += content
                    total_chars += content_length
                    success = True  # 至少有一个URL成功抓取
                    
                    # 打印当前使用情况
                    usage_percentage = (total_chars / SAFE_CHAR_LIMIT) * 100
                    print(f"当前使用量: {total_chars}/{SAFE_CHAR_LIMIT} 字符 ({usage_percentage:.2f}%)")
                
        except Exception as e:
            print(f"抓取 {url} 的内容时出错: {str(e)}")
            continue

    # 如果没有成功抓取任何内容,返回空字符串
    if not success or not aggregated_content.strip():
        print("警告: 未能从任何URL成功抓取内容")
        return ""

    try:
        # 设置向量检索器
        auto_retriever = AutoRetriever(
            vector_storage_local_path="local_data",
            storage_type=StorageType.QDRANT,
            embedding_model=MistralEmbedding(),
        )

        # 基于查询检索最相关的信息
        retrieved_info = auto_retriever.run_vector_retriever(
            query=query,
            contents=aggregated_content,
            top_k=3,
            similarity_threshold=0.5,
        )
        
        return retrieved_info if retrieved_info else ""

    except Exception as e:
        print(f"检索过程中出错: {str(e)}")
        return ""
    r"""Retrieves relevant information from a list of URLs based on a given
    query.

    This function uses the `Firecrawl` tool to scrape content from the
    provided URLs and then uses the `AutoRetriever` from CAMEL to retrieve the
    most relevant information based on the query from the scraped content.

    Args:
        urls (list[str]): A list of URLs to scrape content from.
        query (str): The query string to search for relevant information.

    Returns:
        str: The most relevant information retrieved based on the query.

    Example:
        >>> urls = ["https://example.com/article1", "https://example.com/
        article2"]
        >>> query = "latest advancements in AI"
        >>> result = retrieve_information_from_urls(urls, query)
    """
    # 设置Mistral API的token限制和安全阈值(80%)
    MAX_TOKENS = 16384
    SAFE_TOKEN_LIMIT = int(MAX_TOKENS * 0.7)  # 13107 tokens
    CHAR_PER_TOKEN = 4  # 假设平均每个token对应4个字符
    SAFE_CHAR_LIMIT = SAFE_TOKEN_LIMIT * CHAR_PER_TOKEN
    
    aggregated_content = ''
    total_chars = 0

    # Scrape and aggregate content from each URL
    for url in urls:
        try:
            scraped_content = Firecrawl().scrape(url)
            content = scraped_content["markdown"]
            content_length = len(content)
            
            # 检查是否会超过安全阈值
            if total_chars + content_length > SAFE_CHAR_LIMIT:
                print(f"Reached safety threshold (70% = {SAFE_CHAR_LIMIT} chars), stopping content collection")
                break
                
            aggregated_content += content
            total_chars += content_length
            
            # 打印当前使用情况
            usage_percentage = (total_chars / SAFE_CHAR_LIMIT) * 100
            print(f"Current usage: {total_chars}/{SAFE_CHAR_LIMIT} chars ({usage_percentage:.2f}%)")
            
        except Exception as e:
            print(f"Error scraping content from {url}: {str(e)}")
            continue

    # Set up a vector retriever with local storage and embedding model from Mistral AI
    auto_retriever = AutoRetriever(
        vector_storage_local_path="local_data",
        storage_type=StorageType.QDRANT,
        embedding_model=MistralEmbedding(),
    )

    # Retrieve the most relevant information based on the query
    # You can adjust the top_k and similarity_threshold value based on your needs
    retrieved_info = auto_retriever.run_vector_retriever(
        query=query,
        contents=aggregated_content,
        top_k=3,
        similarity_threshold=0.5,
    )

    return retrieved_info