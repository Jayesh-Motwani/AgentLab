'''this is where we initialize our llms, in a real scenario we would have cheaper
and expensive models for say things like supervisors, agent councils or multimodal 
llms for vision tasks (like ColPali) etc.'''

import os
from langchain_openai import ChatOpenAI


OPENAI_MODEL_NAME = os.environ.get('OPENAI_MODEL_NAME')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL')

if not OPENAI_BASE_URL:
    raise NotImplementedError("OPENAI_BASE_URL is required")


def get_openai_llm():
    return ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0.7,
        timeout=20,
        max_retries=1,
    )
