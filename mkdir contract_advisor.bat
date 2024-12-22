mkdir contract_advisor
cd contract_advisor

:: 创建主要目录结构
mkdir frontend\api frontend\web
mkdir document_processor
mkdir llm_agents\contract_analyzer llm_agents\debate_agents\six_hats llm_agents\debate_agents\life_coach
mkdir knowledge_base\nebula_graph knowledge_base\vector_store
mkdir output_handlers
mkdir model_training\expert_model model_training\data
mkdir utils
mkdir tests

:: 创建主要的Python文件
type nul > document_processor\pdf_processor.py
type nul > document_processor\image_processor.py
type nul > document_processor\url_crawler.py

type nul > output_handlers\text_formatter.py
type nul > output_handlers\speech_synthesis.py

type nul > utils\config.py
type nul > utils\logger.py

:: 创建基本的 __init__.py 文件以使目录成为Python包
type nul > frontend\__init__.py
type nul > document_processor\__init__.py
type nul > llm_agents\__init__.py
type nul > knowledge_base\__init__.py
type nul > output_handlers\__init__.py
type nul > model_training\__init__.py
type nul > utils\__init__.py
type nul > tests\__init__.py