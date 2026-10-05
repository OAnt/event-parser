from typing import Union

from llama_cpp import Llama
from llama_cpp.llama_chat_format import MTMDChatHandler

from evp import conf
from evp.core.models.content import RemoteMedia, LocalMedia
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

def describe_concert_flyer(media: Union[RemoteMedia, LocalMedia]):
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
            "schema": Flyer.model_json_schema(),
        }
    )
    return Flyer.model_validate_json(message["choices"][0]["message"]["content"])

SYSTEM_PROMPT_2_A = """
You are an assistant expert at describing event flyers
You should determine if the flyer relates to one ore many events
You locate patch of text. Particularly you are looking for
    - venue: where the event is taking place
    - date: when the event is taking place
    - performers: who is performing
    - price: how much we are going to pay (optional)
    - description: what is the nature of the event (optional)
You are to describe your thought and how you are reaching conclusions
"""

SYSTEM_PROMPT_2_B = """
You are an assistant, reviewing description of event flyers
You are to validate the precision and accuracy of elements
reported in the description
You are to report errors and misunderstandings
And generate a final report
"""

SYSTEM_PROMPT_2_C = """
You are an assistant, converting description of event flyers into a usable format
You extract semantic information and return it as directly usable json
The json schema should be:
{
    reasoning: "<describe your thoughts here before filling the rest>"
    concerts: [
        {
            venue: "<where the concert takes place>"
            date: "<when the concert takes place validate that this is a single day>"
            performers: ["<performer 1>", "<performer 2>", ..., "<performer 3>"]
        }, ...
    ],
}
You return always return a list, each item is a concert on the flyer
You return an empty object if the image is not a concert flyer or is unavailable
"""

def describe_concert_flyer_2(media: RemoteMedia):
    llm = get_llm()
    messages_a = [
        {"role": "system", "content": SYSTEM_PROMPT_2_A},
        {
            "role": "user",
            "content": get_user_message(media),
        }
    ]
    response_a = llm.create_chat_completion(
        messages_a,
    )
    messages_b = [
        {"role": "system", "content": SYSTEM_PROMPT_2_B},
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text": f"review this description: {response_a['choices'][0]['message']['content']}"
            }]
        }
    ]
    response_b = llm.create_chat_completion(
        messages_b,
    )
    messages_c = [
        {"role": "system", "content": SYSTEM_PROMPT_2_C},
        {
            "role": "user",
            "content": [{
                "type": "text",
                "text": f"{response_b['choices'][0]['message']['content']}",
            }],
        }
    ]
    message = llm.create_chat_completion(
        messages_c,
        response_format={
            "type": "json_object",
            "schema": JSON_SCHEMA,
        }
    )
    return message["choices"][0]["message"]["content"]

