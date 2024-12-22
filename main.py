# main.py
from contract_advisor.llm_agents.contract_analyzer.contract_analyzer import ContractAnalyzer,create_risk_knowledge_report
import os
from getpass import getpass
from contract_advisor.llm_agents.debate_agents.debate import analyze_contract_risk
from contract_advisor.output_handlers.speech_synthesis import generate_speech


# 使用示例
if __name__ == "__main__":
    # 初始化分析器（使用必要的API密钥）    
    chunkr_api_key = getpass('Enter your Chunkr API key: ')
    openai_api_key = getpass('Enter your OpenAI API key: ')
    firecrawl_api_key = getpass('Enter your Firecrawl API key: ')
    mistral_api_key = getpass('Enter your Mistral API key: ')
    google_api_key = getpass('Enter your Google API key: ')
    search_engine_id = getpass('Enter your Search Engine ID: ')

    analyzer = ContractAnalyzer(
        chunkr_api_key=chunkr_api_key,
        openai_api_key=openai_api_key
    )

    os.environ["FIRECRAWL_API_KEY"] = firecrawl_api_key
    os.environ["MISTRAL_API_KEY"] = mistral_api_key  
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["SEARCH_ENGINE_ID"] = search_engine_id
    qwen_api_key = getpass('Enter your API key: ')
    os.environ["QWEN_API_KEY"] = qwen_api_key
    fishaudio_api_key = getpass('Enter your API key: ')
    os.environ["FISHAUDIO_API_KEY"] = fishaudio_api_key
    # 分析合同
    result = analyzer.analyze_contract("./contract_advisor/examples/exa2.pdf")
    print("____________________________________________________________")
    # 打印结果
    output = create_risk_knowledge_report(result)
    print("____________________________________________________________")

    end = analyze_contract_risk(str(contract_data))
    print(end)
    generate_speech(end,"./greetings.mp3")
    