import os
from getpass import getpass

# Prompt for the API key securely
openai_api_key = getpass('Enter your API key: ')
os.environ["OPENAI_API_KEY"] = openai_api_key
sys_msg = "您是一位专业的律师。请仅使用此合同[Contract.pdf]中的信息回答以下问题：1）这是什么类型的合同？2）合同的当事方及其角色是什么？它们在哪注册成立？请列出州和国家（使用 ISO 3166 国家名称）。3）协议日期是什么？4）生效日期是什么？对于以下每种合同条款类型，提取两条信息：a）一个是/否，指示您是否认为该条款存在于合同中；b）一个列出指示该条款类型存在的摘录的列表。合同条款类型：竞争限制例外、竞业禁止条款、排他性条款、禁止招揽客户、禁止招揽员工、不得诋毁条款、方便终止条款、优先购买权条款、控制权变更条款、反转让条款、不设上限的责任条款、责任上限条款。请将最终答案以 JSON 文档的形式提供。"
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig

# Define the model, here in this case we use gpt-4o-mini
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type=ModelType.GPT_4O_MINI,
    model_config_dict=ChatGPTConfig().as_dict(), # [Optional] the config for model
)
from camel.agents import ChatAgent
agent = ChatAgent(
    system_message=sys_msg,
    model=model,
    message_window_size=10, # [Optional] the length for chat memory
    output_language = 'Chinese'
    )
# Define a user message
usr_msg = 'what is information in your mind?'

# Sending the message to the agent
response = agent.step(usr_msg)

# Check the response (just for illustrative purpose)
print(response.msgs[0].content)