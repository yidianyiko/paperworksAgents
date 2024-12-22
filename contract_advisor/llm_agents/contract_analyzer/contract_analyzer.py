# contract_advisor/llm_agents/contract_analyzer/contract_analyzer.py
from contract_advisor.document_processor.url_crawler import retrieve_information_from_urls
from contract_advisor.llm_agents.debate_agents.debate import analyze_contract_risk

# from contract_advisor.knowledge_base.nebula_graph.neo import knowledge_graph_builder
from camel.storages import Neo4jGraph
from camel.loaders import UnstructuredIO
from camel.agents import KnowledgeGraphAgent

def knowledge_graph_builder(text_input: str) -> None:
    r"""Build and store a knowledge graph from the provided text.

    This function processes the input text to create and extract nodes and relationships,
    which are then added to a Neo4j database as a knowledge graph.

    Args:
        text_input (str): The input text from which the knowledge graph is to be constructed.

    Returns:
        graph_elements: The generated graph element from knowlegde graph agent.
    """

    # Set Neo4j instance
    n4j = Neo4jGraph(
        url="neo4j+s://653e33c2.databases.neo4j.io",
        username="neo4j",
        password="ZQzOnxmr2mzWa-t5F9op-DwaNStb24KAt0EgFps0H7s",
    )
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    from camel.configs import MistralConfig

    # Set up model
    mistral_large_2 = ModelFactory.create(
        model_platform=ModelPlatformType.MISTRAL,
        model_type=ModelType.MISTRAL_LARGE,
        model_config_dict=MistralConfig(temperature=0.2).as_dict(),
    )  
    # Initialize instances
    uio = UnstructuredIO()
    kg_agent = KnowledgeGraphAgent(model=mistral_large_2)

    # Create an element from the provided text
    element_example = uio.create_element_from_text(text=text_input, element_id="001")

    # Extract nodes and relationships using the Knowledge Graph Agent
    graph_elements = kg_agent.run(element_example, parse_graph_elements=True)

    # Add the extracted graph elements to the Neo4j database
    n4j.add_graph_elements(graph_elements=[graph_elements])

    return graph_elements

import os
import sys
# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

from contract_advisor.document_processor.pdf_processor import process_pdf_document
from getpass import getpass
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig
from camel.agents import ChatAgent

class ContractAnalyzer:
    def __init__(self, chunkr_api_key, openai_api_key=None):
        """
        初始化合同分析器
        
        参数:
        chunkr_api_key (str): Chunkr API密钥
        openai_api_key (str, optional): OpenAI API密钥
        """
        self.chunkr_api_key = chunkr_api_key
        self.openai_api_key = openai_api_key
        self.sys_msg = """您是一位专业的劳动纠纷方向的律师专家。请仅使用此合同内容回答以下问题：

        1）这是什么类型的合同？
        2）合同的当事方及其角色是什么？它们在哪注册成立？请列出州和国家（使用 ISO 3166 国家名称）。
        3）协议日期是什么？
        4）生效日期是什么？

        5）对于以下每种合同条款类型，提取两条信息：
        a）一个是/否，指示您是否认为该条款存在于合同中；
        b）一个列出指示该条款类型存在的摘录的列表。
        合同条款类型：
        - 竞争限制例外
        - 竞业禁止条款
        - 排他性条款
        - 禁止招揽客户
        - 禁止招揽员工
        - 不得诋毁条款
        - 方便终止条款
        - 优先购买权条款
        - 控制权变更条款
        - 反转让条款
        - 不设上限的责任条款
        - 责任上限条款

        6）针对劳动合同解除相关内容，请额外分析：
        a）解除补偿相关：
            - 未结工资金额及构成
            - 经济补偿金额及计算依据
            - 支付方式和时间安排
            - 其他补偿项目

        b）义务约定相关：
            - 离职交接要求及责任
            - 保密义务具体内容
            - 违约责任设置

        7）合规性分析：
        a）支付安排是否符合法律规定
        b）是否存在显失公平条款
        c）是否存在可能引发争议的条款

        8）风险提示：
        a）付款安排中的风险点
        b）义务履行中的风险点
        c）其他需要特别注意的事项

        请将最终答案以 JSON 文档的形式提供，确保包含上述所有分析内容，并不会包含任何可以直接关联到个人的信息。"""

    def _initialize_openai(self):
        """初始化OpenAI设置"""
        if not self.openai_api_key:
            self.openai_api_key = getpass('请输入您的OpenAI API密钥: ')
        os.environ["OPENAI_API_KEY"] = self.openai_api_key

        # 创建模型实例
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O_MINI,
            model_config_dict=ChatGPTConfig().as_dict(),
        )
        qwen_model = ModelFactory.create(
            model_platform=ModelPlatformType.QWEN,
            model_type=ModelType.QWEN_TURBO,
            model_config_dict=QwenConfig(temperature=0.2).as_dict(),
        )
        # 创建聊天代理
        self.agent = ChatAgent(
            system_message=self.sys_msg,
            model=qwen_model,
            message_window_size=10,
            output_language='Chinese'
        )

    def analyze_contract(self, pdf_path):
        """
        分析合同文档
        
        参数:
        pdf_path (str): PDF文件路径
        
        返回:
        dict: 分析结果
        """
        try:
            # 处理PDF文档
            pdf_content = process_pdf_document(pdf_path, self.chunkr_api_key)
            
            if not pdf_content:
                return {"error": "PDF处理失败"}

            # 初始化OpenAI设置
            self._initialize_openai()

            # 构建用户消息
            usr_msg = f"请分析以下合同内容：\n{pdf_content}"

            # 发送消息给代理并获取响应
            response = self.agent.step(usr_msg)

            # 返回分析结果
            return {
                "raw_content": pdf_content,
                "analysis": response.msgs[0].content
            }

        except Exception as e:
            return {
                "error": f"分析过程中发生错误: {str(e)}"
            }


  
def create_risk_knowledge_report(input_data: str):
    """
    针对输入数据创建风险知识报告和知识图谱
    
    Args:
        input_data: 输入的结构化数据
        
    Returns:
        dict: 包含报告和知识图谱的结果
    """
    from typing import List
    from colorama import Fore
    from camel.agents.chat_agent import FunctionCallingRecord 
    from camel.societies import RolePlaying
    from camel.utils import print_text_animated
    from camel.retrievers import AutoRetriever
    from camel.toolkits import FunctionTool, SearchToolkit
    from camel.types import ModelPlatformType, ModelType, StorageType
    from camel.embeddings import MistralEmbedding

    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    from camel.configs import MistralConfig

# Set up model
    mistral_large_2 = ModelFactory.create(
        model_platform=ModelPlatformType.MISTRAL,
        model_type=ModelType.MISTRAL_LARGE,
        model_config_dict=MistralConfig(temperature=0.2).as_dict(),
    )  
    # 定义任务提示语
    task_prompt = "Analyze the input structured data to:"+str(input_data)+"""Research potential consequences based on the combinations of contract types and their associated risk factors
    Generate a comprehensive report, Create a knowledge graph representation of the report findings
    You should use search tool to get related URLs first, then use retrieval tool
    to get the retrieved content back by providing the list of URLs, finially 
    use tool to build the knowledge graph to finish the task.
    No more other actions needed"""

    # 定义工具函数
    retrieval_tool = FunctionTool(retrieve_information_from_urls)
    search_tool = FunctionTool(SearchToolkit().search_duckduckgo)
    knowledge_graph_tool = FunctionTool(knowledge_graph_builder)

    tool_list = [
        retrieval_tool,
        search_tool, 
        knowledge_graph_tool,
    ]

    # 配置助手模型
    assistant_model_config = MistralConfig(
        tools=tool_list,
        temperature=0.0,
    )
    
    # 这里可以添加调用模型生成报告和知识图谱的具体逻辑
    # Initialize the role-playing session
    role_play_session = RolePlaying(
        assistant_role_name="CAMEL Assistant",
        user_role_name="CAMEL User",
        assistant_agent_kwargs=dict(
            model=ModelFactory.create(
                model_platform=ModelPlatformType.MISTRAL,
                model_type=ModelType.MISTRAL_LARGE,
                model_config_dict=assistant_model_config.as_dict(),
            ),
            tools=tool_list,
        ),
        user_agent_kwargs=dict(model=mistral_large_2),
        task_prompt=task_prompt,
        with_task_specify=False,
    )
    # Print system and task messages
    print(
        Fore.GREEN
        + f"AI Assistant sys message:\n{role_play_session.assistant_sys_msg}\n"
    )
    print(Fore.BLUE + f"AI User sys message:\n{role_play_session.user_sys_msg}\n")

    print(Fore.YELLOW + f"Original task prompt:\n{task_prompt}\n")
    print(
        Fore.CYAN
        + "Specified task prompt:"
        + f"\n{role_play_session.specified_task_prompt}\n"
    )
    print(Fore.RED + f"Final task prompt:\n{role_play_session.task_prompt}\n")
    n = 0
    input_msg = role_play_session.init_chat()
    while n < 20: # Limit the chat to 20 turns
        n += 1
        assistant_response, user_response = role_play_session.step(input_msg)

        if assistant_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI Assistant terminated. Reason: "
                    f"{assistant_response.info['termination_reasons']}."
                )
            )
            break
        if user_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI User terminated. "
                    f"Reason: {user_response.info['termination_reasons']}."
                )
            )
            break
        # Print output from the user
        print_text_animated(
            Fore.BLUE + f"AI User:\n\n{user_response.msg.content}\n",
            0.01
        )

        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

        # Print output from the assistant, including any function
        # execution information
        print_text_animated(Fore.GREEN + "AI Assistant:", 0.01)
        tool_calls: List[FunctionCallingRecord] = [
            FunctionCallingRecord(**call.as_dict())
            for call in assistant_response.info['tool_calls']
        ]
        for func_record in tool_calls:
            print_text_animated(f"{func_record}", 0.01)
        print_text_animated(f"{assistant_response.msg.content}\n", 0.01)

        input_msg = assistant_response.msg
    return input_msg