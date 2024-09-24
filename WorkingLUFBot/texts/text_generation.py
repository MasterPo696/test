import random 

random.randint(0, 8)

unknown_text_list = ["<b>Oops! It seems my digital circuits are tangled... Try again or press /help!</b>",
"<b>Hmm, my microchips are confused. Looks like it's encrypted! But I haven't figured it out yet. /help?</b>",
"<b>Uh-oh! My virtual brain froze on this command. Let's try something else? /help</b>",
"<b>Looks like I broke... or I just don't understand what you want. Try explaining differently or press /help!</b>",
"<b>Is this command for some kind of super bot? I seem to be out of the loop... Let's start with /help?</b>",
"<b>Uh, what? I just lost touch with reality. Let's hit /help instead!</b>",
"<b>It seems I've just discovered a new universe... but didn't understand what you're asking for. Let's check /help?</b>",
"<b>Whoops! Something went wrong. Maybe my antenna isn't tuned properly? Press /help!</b>",
]

welcome_text_list = [
    "<b>Booting up... Ready to dive in? If you're lost, hit /help!</b>",
    "<b>System online! Welcome! Need guidance? Try /help!</b>",
    "<b>Powering up... Hello! Hit /help for guidance!</b>",
    "<b>Beep boop! I'm awake! Need a hint? Just type /help!</b>",
    "<b>Greetings, explorer! Ready to start? /help has your back!</b>",
    "<b>Online and ready! Need a refresher? /help is the key!</b>",
    "<b>System rebooted! Ready for the next task? /help can assist!</b>",
    "<b>Initialization complete! Ready for orders. Type /help if needed!</b>",
    "<b>All systems go! Feeling lost? Use /help to get on track!</b>",
    "<b>Activated and ready! Unsure? Type /help and I'll guide you!</b>",
]




# Списки сообщений для каждого типа контента
sticker_responses = [ "<b>Oops! I don't know what to do with this sticker... Try something else or press /help!</b>",
    "<b>Hmm, my digital brain doesn't understand stickers... Press /help?</b>",
    "<b>Uh-oh! I can't process stickers. Try something different? /help</b>"]
photo_responses = [ "<b>Oops! Photos are too complex for me... Try again or press /help!</b>",
    "<b>Hmm, looks like you're sending something beautiful, but I can't see it... /help?</b>",
    "<b>Uh-oh! My virtual brain can't handle photos. Let's try text? /help</b>"]
video_responses = [ "<b>Oops! Videos make my circuits overheat... Try something else or press /help!</b>",
    "<b>Hmm, I can't handle moving images yet. Press /help for assistance!</b>",
    "<b>Uh-oh! Videos are a bit too much for me... Let's keep it simple? /help</b>"]
document_responses = ["<b>Oops! I don't know how to handle documents... Try again or press /help!</b>",
    "<b>Hmm, this document looks interesting, but I can't read it... /help?</b>",
    "<b>Uh-oh! I can't open documents... Let's try text? /help</b>"]

def unknown_text_reply():
    return unknown_text_list[random.randint(0, 7)]

def greetings_reply():
    return welcome_text_list[random.randint(0, 9)]


def get_response_by_content_type(content_type):
    if content_type == 'sticker':
        return random.choice(sticker_responses)
    elif content_type == 'photo':
        return random.choice(photo_responses)
    elif content_type == 'video':
        return random.choice(video_responses)
    elif content_type == 'document':
        return random.choice(document_responses)
    else:
        return "<b>Oops! My circuits don't know how to process this type of file. Try again or press /help!</b>"



say_hi = [
    "hello",
    "hi",
    "hey",
    "greetings",
    "howdy",
    "what's up"
]