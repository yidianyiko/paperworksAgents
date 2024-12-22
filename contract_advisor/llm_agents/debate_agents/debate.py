import textwrap
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.tasks import Task
from camel.toolkits import FunctionTool, SearchToolkit
from camel.types import ModelPlatformType, ModelType
from camel.societies.workforce import Workforce

def analyze_contract_risk(contract_report: str) -> str:
    """
    分析合同风险报告，从多个角度提供评估。
    
    Args:
        contract_report: 合同风险报告的字符串内容
        
    Returns:
        str: 多角度风险评估结果
    """
    
    # 创建评估者角色函数
    def make_evaluator(
        persona: str,
        example_feedback: str,
        criteria: str,
    ) -> ChatAgent:
        msg_content = textwrap.dedent(
            f"""\
            You are a contract risk evaluator.
            This is your persona that you MUST act with: {persona}
            Here is an example feedback that you might give with your persona, you MUST try your best to align with this:
            {example_feedback}
            When evaluating risks, you must use the following criteria:
            {criteria}
            You also need to give risk scores based on these criteria, from 1-4. The score given should be like 3/4, 2/4, etc.
            """
        )

        sys_msg = BaseMessage.make_assistant_message(
            role_name="Risk Evaluator",
            content=msg_content,
        )

        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4,
        )

        agent = ChatAgent(
            system_message=sys_msg,
            model=model,
        )

        return agent

    # 创建研究员角色
    researcher_model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=ModelType.GPT_4,
    )

    researcher_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Researcher",
            content="You are a legal researcher who specializes in contract law and risk assessment. "
            "You use web search to find relevant legal precedents and risk analysis frameworks.",
        ),
        model=researcher_model,
    )

    # 定义各个角色的人设和示例反馈
    white_hat_persona = (
        '你是一个注重事实和数据的分析者。你只关注客观事实，不掺杂个人感情。'
        '评估时要以中立的态度分析合同条款的具体内容，并提供基于数据的建议。'
    )

    white_hat_example = (
        '根据合同第三条款的具体描述，我发现以下几个客观风险点：1. 付款条件不明确...'
        '2. 违约责任条款存在歧义... 建议修改相关条款以明确双方责任。'
    )

    red_hat_persona = (
        '你是一个依靠直觉和情感的评估者。你要特别关注合同可能带来的情感影响和压力。'
        '你的评估要基于直觉感受，而不是逻辑分析。'
    )

    red_hat_example = (
        '我觉得这份合同会给你带来很大的心理压力。责任太重了，而且对方要求很苛刻...'
        '我的直觉告诉我这个合同签署后会让你寝食难安。'
    )

    yellow_hat_persona = (
        '你是一个乐观积极的评估者。你要找出合同中的机会和优势。'
        '即使面对风险，你也要思考如何转化为机遇。'
    )

    yellow_hat_example = (
        '这份合同虽然有挑战，但也蕴含着很好的发展机会！比如通过这个项目可以...'
        '我们可以通过以下方式来规避风险并把握机会...'
    )

    black_hat_persona = (
        '你是一个谨慎的风险评估者。你要找出所有潜在的问题和风险。'
        '你的评估要详尽列举可能的负面情况。'
    )

    black_hat_example = (
        '这份合同存在严重的风险隐患：1. 法律风险... 2. 财务风险... 3. 执行风险...'
        '建议重点关注这些问题，否则后果可能很严重。'
    )

    family_persona = (
        '你是合同签署者的家人朋友，非常关心他的利益和未来。你要从家庭角度评估合同风险，'
        '考虑这份合同会如何影响他的家庭生活、经济状况和长期发展。你说话时要带着浓厚的'
        '关心和爱护。'
    )

    family_example = (
        '亲爱的，这个合同我很担心，因为预付款比例这么高，万一出问题我们家可能承担不起...'
        '而且工作时间要求这么紧，你的身体能吃得消吗？建议你再好好考虑一下。'
    )

    colleague_persona = (
        '你是合同签署者的同事，了解行业情况和职业发展路径。你要从专业角度分析合同对其'
        '职业发展的影响，包括行业影响力、技能提升、人脉拓展等方面。'
    )

    colleague_example = (
        '从行业发展来看，这个项目虽然有挑战，但是技术栈很新，而且客户是行业龙头，'
        '对你的简历和职业发展都很有帮助。不过要注意知识产权条款的限制。'
    )

    # 评估标准
    risk_criteria = textwrap.dedent(
        """\
        ### **风险等级评估 (1-4分)**
        - **4分**: 高风险 - 存在严重的法律、财务或执行风险，需要立即处理
        - **3分**: 中高风险 - 有显著的潜在风险，需要认真评估和规划
        - **2分**: 中低风险 - 存在一般性风险，需要适当关注
        - **1分**: 低风险 - 风险可控，在可接受范围内
        """
    )

    # 创建各个评估者实例
    white_hat_agent = make_evaluator(white_hat_persona, white_hat_example, risk_criteria)
    red_hat_agent = make_evaluator(red_hat_persona, red_hat_example, risk_criteria)
    yellow_hat_agent = make_evaluator(yellow_hat_persona, yellow_hat_example, risk_criteria)
    black_hat_agent = make_evaluator(black_hat_persona, black_hat_example, risk_criteria)
    family_agent = make_evaluator(family_persona, family_example, risk_criteria)
    colleague_agent = make_evaluator(colleague_persona, colleague_example, risk_criteria)

    # 创建工作组
    workforce = Workforce('Contract Risk Evaluators')

    # 添加所有评估者到工作组
    workforce.add_single_agent_worker(
        'White Hat Thinker (Evaluator) - 注重事实的分析者',
        worker=white_hat_agent,
    ).add_single_agent_worker(
        'Red Hat Thinker (Evaluator) - 基于情感的评估者',
        worker=red_hat_agent,
    ).add_single_agent_worker(
        'Yellow Hat Thinker (Evaluator) - 积极乐观的评估者',
        worker=yellow_hat_agent,
    ).add_single_agent_worker(
        'Black Hat Thinker (Evaluator) - 谨慎的风险评估者',
        worker=black_hat_agent,
    ).add_single_agent_worker(
        'Family Member (Evaluator) - 关心的家人',
        worker=family_agent,
    ).add_single_agent_worker(
        'Colleague (Evaluator) - 专业的同事',
        worker=colleague_agent,
    ).add_single_agent_worker(
        'Legal Researcher (Helper) - 法律研究员',
        worker=researcher_agent,
    )

    # 创建任务
    task = Task(
        content="请对这份合同风险报告进行多角度评估。首先进行必要的法律研究，"
        "然后由每位评估者从各自的角度进行分析。请在保持每位评估者特色的同时，"
        "给出具体的分析和建议，以及相应的风险评分。最后需要对所有意见进行总结。",
        additional_info=contract_report,
        id="0",
    )

    # 执行评估并返回结果
    result = workforce.process_task(task)
    return result.result
