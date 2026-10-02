from llama_cpp import Llama
from llama_cpp.llama_chat_format import MTMDChatHandler

from core.models.content import RemoteMedia
from core.llm.common import SYSTEM_PROMPT, JSON_SCHEMA, get_user_message

_llm = None

def get_llm() -> Llama:
    global _llm
    if _llm is None:
        # chat_handler = MTMDChatHandler.from_pretrained(
            # repo_id="mistralai/Ministral-3-3B-Instruct-2512-GGUF",
            # filename="Ministral-3-3B-Instruct-2512-BF16-mmproj.gguf",
        # )
        chat_handler = MTMDChatHandler(
            clip_model_path="data/models/bartowski/mmproj-mistralai_Ministral-3-3B-Instruct-2512-bf16.gguf",
        )
        _llm = Llama(
            model_path="data/models/bartowski/mistralai_Ministral-3-3B-Instruct-2512-Q8_0.gguf",
            verbose=False,
            chat_handler=chat_handler,
            chat_format="mtmd",
            n_ctx=4096,
        )
        # _llm = Llama.from_pretrained(
            # repo_id="mistralai/Ministral-3-3B-Instruct-2512-GGUF",
            # # filename="*Q8_0.gguf",
            # filename="*Q5_K_M.gguf",
            # verbose=False,
            # chat_handler=chat_handler,
            # n_ctx=4096,
        # )
    return _llm

def describe_concert_flyer(media: RemoteMedia):
    llm = get_llm()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": get_user_message(media),
        }
    ]
    message = llm.create_chat_completion(
        messages,
        response_format={
            "type": "json_object",
            "schema": JSON_SCHEMA,
        }
    )
    print(message)
    return message["choices"][0]["message"]["content"]
