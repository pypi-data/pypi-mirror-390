import pyttsx3

def speak(text: str, rate: int = 175, female: bool = True):
    """
    Speak the provided text aloud with a female voice if available.
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    
    voices = engine.getProperty("voices")
    
    # Choose female voice if available
    if female:
        for v in voices:
            if "female" in v.name.lower() or "zira" in v.name.lower():  # common female voice
                engine.setProperty("voice", v.id)
                break
        else:
            engine.setProperty("voice", voices[0].id)  # fallback
    else:
        engine.setProperty("voice", voices[0].id)  # default male/fallback

    engine.say(text)
    engine.runAndWait()
