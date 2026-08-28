'''this is where we initialize our llms, in a real scenario we would have cheaper
and expensive models for say things like supervisors, agent councils or multimodal 
llms for vision tasks (like ColPali) etc.'''

import os
from langchain_openai import ChatOpenAI


OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL') or None
OPENAI_MODEL_NAME = os.environ.get('OPENAI_MODEL_NAME')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise NotImplementedError("API-Key is required")


def get_openai_llm():
    openai_params = {
        "model": OPENAI_MODEL_NAME,
        "api_key": OPENAI_API_KEY,
    }

    if OPENAI_BASE_URL:
        openai_params['base_url'] = OPENAI_BASE_URL

    return ChatOpenAI(**openai_params)
