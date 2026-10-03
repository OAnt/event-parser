from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from evp.core.models.content import RemoteMedia
from evp.core.llm.common import SYSTEM_PROMPT, JSON_SCHEMA, get_user_message

class Concert(BaseModel):
    venue: str
    date: str
    performers: List[str]

class Flyer(BaseModel):
    concerts: List[Concert]

def describe_concert_flyer(media: RemoteMedia):
    llm = ChatOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="not-needed",
        model="local",
        max_tokens=4096,
    )
    structured_llm = llm.with_structured_output(JSON_SCHEMA, method="json_mode")
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=get_user_message(media)),
    ]
    response = structured_llm.invoke(messages)
    print(response)
    return response["data"]
