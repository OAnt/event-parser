import json
import logging
from typing import Union

from llama_cpp import Llama
from llama_cpp.llama_chat_format import MTMDChatHandler

from evp import conf
from evp.core.models.content import Post, QualityEnum
from evp.core.models.events import Flyer
from evp.core.llm.common import (
    SYSTEM_PROMPT,
    get_user_message,
    SYSTEM_PROMPT_QUALITY,
    JSON_SCHEMA_QUALITY,
    get_user_message_quality
)

log = logging.getLogger(__name__)

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
            n_gpu_layers=-1,
        )
    return _llm

def describe_concert_flyer(post: Post) -> Flyer:
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

def rate_post(post: Post) -> QualityEnum:
    llm = get_llm()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_QUALITY},
        {
            "role": "user",
            "content": get_user_message_quality(post),
        }
    ]
    message = llm.create_chat_completion(
        messages,
        response_format={
            "type": "json_object",
            "schema": JSON_SCHEMA_QUALITY,
        }
    )
    try:
        rate = json.loads(message["choices"][0]["message"]["content"])
    except ValueError as e:
        log.error(f"JSON loading failed for {message['choices'][0]['message']['content']}")
        return QualityEnum.failed
    print(rate, post.media.url)
    if rate["relevant"]:
        if rate["high_quality"]:
            return QualityEnum.high_quality
        else:
            return QualityEnum.low_quality
    else:
        return QualityEnum.irrelevant
