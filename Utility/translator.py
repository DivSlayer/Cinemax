from googletrans import Translator


async def translate_text(text, dest_language="fa"):
    """
    Asynchronously translates the input text into the specified destination language.

    Parameters:
        text (str): The text to translate.
        dest_language (str): The target language code (e.g., 'en' for English, 'fr' for French).

    Returns:
        str: The translated text.
    """
    translator = Translator()
    try:
        # Await the asynchronous translation call
        result = await translator.translate(text, dest=dest_language)
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None
