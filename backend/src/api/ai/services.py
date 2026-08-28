''' this is where we will define the actual tools and functions for workflows/tasks we need to automate. 
Always remember the rule of file trees.'''

from api.ai.llms import get_openai_llm
from api.ai.schemas import EmailMessage


def generate_email_message(query: str) -> EmailMessage:
    llm = get_openai_llm().with_structured_output(EmailMessage)

    messages = [
        (
            "system",
            "You are a helpful assistant for research and composing plaintext emails. Do not use markdown in your responses, only plaintext."
        ),
        ("human", f"{query}, do not use markdown in your response only plain text")
    ]

    return llm.invoke(messages)
