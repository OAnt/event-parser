from core.models.content import RemoteMedia

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
"""

def get_user_message(media: RemoteMedia):
    return [
        {"type": "text", "text": "Describe the image"},
        {"type": "image_url", "image_url": {"url": str(media.url)}},
    ]
