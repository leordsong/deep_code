# config.py
import os
from dotenv import load_dotenv

load_dotenv() # 从 .env 文件加载环境变量 (如果需要API Key等)
# 或者其他Qwen 2.5系列模型
FINETUNED_MODEL_PATH = "models/qwen_finetuned"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # 或者其他中英文embedding模型

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"   

REASONING_MODELS = {
    'DeepSeek R1': {
        'api_key': DEEPSEEK_API_KEY,
        'base_url': DEEPSEEK_BASE_URL,
        'model': 'deepseek-reasoner',
        'temperature': 0.5,
    },
    'Qwen2.5 QwQ': {
        'api_key': DASHSCOPE_API_KEY,
        'base_url': DASHSCOPE_BASE_URL,
        'model': 'qwq-plus',
        'temperature': 0.5,
    }
}

CHAT_MODELS = {
    'Qwen2.5 Coder 72B': {
        'api_key': DASHSCOPE_API_KEY,
        'base_url': DASHSCOPE_BASE_URL,
        'model': 'qwen-coder-plus',
        'temperature': 0.5,
    }
}

LOCAL_MODELS = {
    'Qwen2.5 Coder 7B': "Qwen/Qwen2.5-Coder-7B-Instruct",
    'Qwen2.5 Coder 1.5B': "Qwen/Qwen2.5-Coder-1.5B-Instruct"
}

EMBEDDING_MODELS = {
    'CodeT5+ 110M': 'Salesforce/codet5p-110m-embedding',
    # 'Sentence-Transformers': 'sentence-transformers/all-MiniLM-L6-v2',
}


# 数据存储
DATA_DIR = "cache"

# 其他配置
MAX_CONTEXT_LENGTH = 4096 # 根据Qwen模型调整