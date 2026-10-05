from typing import Union

from llama_cpp import Llama
from llama_cpp.llama_chat_format import MTMDChatHandler

from evp import conf
from evp.core.models.content import Post
from evp.core.models.events import Flyer
from evp.core.llm.common import SYSTEM_PROMPT, get_user_message

_llm = None

def get_llm() -> Llama:
    global _llm
    if _llm is None:
        chat_handler = MTMDChatHandler(
            clip_model_path=conf.MMPROJ,
        )
        _llm = Llama(
            model_path=conf.MODEL,
            verbose=False,
            chat_handler=chat_handler,
            chat_format="mtmd",
            n_ctx=4096,
        )
    return _llm

def describe_concert_flyer(post: Post):
    llm = get_llm()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": get_user_message(post),
        }
    ]
    message = llm.create_chat_completion(
        messages,
        response_format={
            "type": "json_object",
            "schema": Flyer.model_json_schema(),
        }
    )
    return Flyer.model_validate_json(message["choices"][0]["message"]["content"])
