from core.models.content import RemoteMedia

JSON_SCHEMA = {
    "title": "Flyer",
    "type": "object",
    "properties": {
        "concerts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "venue": {"type": "string"},
                    "date": {"type": "string"},
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

def get_user_message(media: RemoteMedia):
    return [
        {"type": "text", "text": "Describe the image"},
        {"type": "image_url", "image_url": {"url": str(media.url)}},
    ]
