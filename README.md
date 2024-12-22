# 现实问题：
今年以来，类似集度汽车“一夜解散”的事情屡见不鲜，数千人要求在数天乃至数小时内完成协商解除劳动协议的合同，相同的情况还发生在入离职合同，房屋租售的合同上。但是合同审查是一项劳动密集型的工作，通常需要律师助理和初级律师仔细识别合同中的关键信息。我们个人甚至律师都难以在这么短的时间内完成合同的审阅及风险判断，我们作为非专业人士也难以对专业属于“咬文嚼字”，作为弱势方，遇到这样的场景，往往容易陷入手足无措的境地，身边没有法律资源，或者负担不起法律资源的问题客观的存在着。市面上针对合同审查的 AI 工具往往都是面向甲方和公司的，不能很好站在弱势方。
因此通过 agent ，帮助用户在短时间内识别出合同中的风险，并借助多智能体系统模拟理性思维（思考帽）和感性思维（亲友和同事的角度），帮助用户推理这个风险项在未来可能造成的结果，帮助用户在短时间内做出合乎理性以及情感的决策。

# 技术架构设计
![image](https://github.com/user-attachments/assets/9a85ba0f-6da2-4ef7-80b7-fe137b551d0f)

This content is only supported in a Feishu Docs
整体分为三大模块：关键信息及风险性提取 agent，role-playing 合同风险项及可能结果知识图谱构建 以及 workforce 多智能体的群体辅助决策三部分
# 主要流程
1. 用户上传 pdf
2. 通过 chunkr 识别成 markdown 格式的文本
3. 通过 Qwen 文本大模型，通过专家提供的 agent 生成结构化的合同数据，并进行脱敏，生成 json 格式的数据
4. 将 json 格式的数据输入给 role-playing 模块，通过 RAG 在互联网上搜索相关案例及文书，最后生成 report 和neo4j 的知识图谱
5. 最后将获得的报告和知识图谱输入给 workforce，workforce 内部实现了 7 个 agent，模拟现实中的五顶思考帽的方式帮助用户理性决策，并增加了社会关系，让亲友和同事的角度对风险项的可能结果和风险指数进行了分析，并给出最后的分析报告
6. 通过 fish 将报告有感情的返回给用户
   
## 程序目录说明
1. 模块化设计：
  - 每个主要功能都独立成模块，便于维护和扩展
  - 符合单一职责原则，每个模块专注于特定功能
2. frontend分离：
  - 将前端相关代码独立，支持多种接入方式
  - 便于前后端分离开发
3. document_processor模块：
  - 分别处理不同类型的输入文档
  - 统一文档处理接口
4. llm_agents模块：
  - 将合同分析和辩论智能体分开
  - 支持多种智能体类型和扩展
5. knowledge_base模块：
  - 整合图数据库和向量存储
  - 统一知识管理接口
6. output_handlers模块：
  - 处理多种输出格式
  - 预留语音输出扩展
7. 可选模块预留：
  - model_training为可选的模型训练
  - 保持架构的扩展性
8. 工具和测试支持：
  - utils提供通用功能
  - tests确保代码质量
## 部署教程
进入主目录后执行 setup.py
然后执行 main.py
输入所需的 API key：Qwen，OPENAI，chunkr，fish，MISTRAL
最长需要等待半小时左右可以得到结果。
