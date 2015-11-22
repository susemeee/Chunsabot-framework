from chunsabot.botlogic import brain

@brain.route("@image")
def add_image_description(msg, extras):
    attachment = extras['attachment']
    if not attachment:
        return None

    return "asdf"
