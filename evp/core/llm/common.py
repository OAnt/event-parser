from typing import Union
from evp.core.models.content import Post, QualityEnum

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "concerts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "venue": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                    "performers": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
    },
}

SYSTEM_PROMPT = """
You are an assistant expert at describing concert flyers
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
The organizer may have added a description for the event.
It is commonly accepted that an event takes place after it is published...
"""

def get_user_message(post: Post):
    base_message = []
    if post.description:
        base_message.append(
            {"type": "text", "text": f"Additional description: {post.description}\n"}
        )
    if post.timestamp:
        base_message.append(
            {"type": "text", "text": f"Published: {post.timestamp.date().isoformat()}\n"}
        )
    base_message.extend([
        {"type": "text", "text": "Describe the image\n"},
        {"type": "image_url", "image_url": {"url": str(post.media.url)}},
    ])
    return base_message

JSON_SCHEMA_QUALITY = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "relevant": {"type": "boolean"},
        "high_quality": {"type": "boolean"},
    },
}

SYSTEM_PROMPT_QUALITY = """
You are an assistant expert at classifying posts for concert flyers.
You tell if a post relates to a concert.
You tell if the post description matches the flyer.
    - It mentions the place (It may be inferred from the account)
    - The date
    - The artists
You return the result as directly usable json.
The schema is
{
    reasoning: "<describe your thoughts here before filling the rest NO MULTI LINE STRINGS>"
    relevant: "<True / False, is it a concert flyer or not>"
    high_quality: "<True / False, the post has a description and it contains the same information as the flyer>"
}

Only report high_quality if both the description and the image agree on:
    - the same place
    - the same date
    - the same artists 
(custom font may make the name harder to compare, I tolerate small spelling mistake)
"""

def get_user_message_quality(post: Post):
    base_message = []
    if post.description:
        base_message.append(
            {"type": "text", "text": f"description: {post.description}\n"}
        )
    base_message.extend([
        {"type": "text", "text": "Rate this post\n"},
        {"type": "image_url", "image_url": {"url": str(post.media.url)}},
    ])
    return base_message
