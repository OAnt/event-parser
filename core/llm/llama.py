from llama_cpp import Llama
from llama_cpp.llama_chat_format import MTMDChatHandler

from core.models.content import RemoteMedia

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

SYSTEM_PROMPT = """
You are an assistant expert at describing concert flyers
You extract semantic information and return it as directly usable json
The json schema should be:
[
    {
        venue: "<where the concert takes place>"
        date: "<when the concert takes place>"
        performers: ["<performer 1>", "<performer 2>", ..., "<performer 3>"]
    }, ...
]
You return always return a list, each item is a concert on the flyer
You return an empty object if the image is not a concert flyer or is unavailable
"""

def describe_concert_flyer(media: RemoteMedia):
    llm = get_llm()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the image"},
                {"type": "image_url", "image_url": {"url": str(media.url)}},
            ],
        }
    ]
    message = llm.create_chat_completion(
        messages,
    )
    return message["choices"][0]["message"]["content"]
