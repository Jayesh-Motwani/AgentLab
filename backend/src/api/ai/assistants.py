from api.ai.llms import get_openai_llm
from api.ai.tools import send_me_email, search_and_save_images, get_unread_emails
import re
import ast
from api.ai.prompts import SYSTEM_PROMPT

EMAIL_TOOLS = {
    "search_and_save_images": search_and_save_images,
    "send_me_email": send_me_email,
    "get_unread_emails": get_unread_emails
}


def email_assistant(query: str):
    llm = get_openai_llm().bind_tools(
        list(EMAIL_TOOLS.values()), tool_choice="required")

    messages = [
        (
            "system", SYSTEM_PROMPT
        ),
        ("human", f"{query}")
    ]

    response = llm.invoke(messages)
    messages.append(response)

    """
		This block below is used to iterate over tool_calls key in response llm gives
		and extract tool_name which is used to map it to the function that needs to 
		be called and arguments it needs. We then invoke this function with args
		and results are appended to the messages list which is passed to the LLM.
	"""

    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_func = EMAIL_TOOLS.get(tool_name)
            tool_args = tool_call.get("args")
            if not tool_func:
                continue
            tool_result = tool_func.invoke(tool_args)
            messages.append(tool_result)
        final_response = llm.invoke(messages)
        return final_response
    return response
