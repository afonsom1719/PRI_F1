from .macros import TRANSLATION_ENDPOINT, TRANSLATION_KEY
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
import logging

# Create a logger
logger = logging.getLogger("globalLogger")


def translate_text(text_to_translate: str) -> str:
    """Uses Azure Translation to translate text to English.

    This function takes a text as input and uses the Azure Translation API to translate it to English.
    The function returns the translated text.

    Args:
        text (str): The text to translate.

    Returns:
        str: The translated text.

    Raises:
        ValueError: If the text is empty or invalid.
        AzureError: If there is an error while calling the Azure API.
    """
    credential = TranslatorCredential(TRANSLATION_KEY, "westeurope")
    text_translator = TextTranslationClient(
        endpoint=TRANSLATION_ENDPOINT, credential=credential
    )
    try:
        detected_language = text_translator.detect_language(
            text_to_translate
        ).primary_language.code
        if detected_language == "en":
            target_languages = ["pt-pt"]
        else:
            target_languages = ["en"]
        input_text_elements = [InputTextItem(text=text_to_translate)]

        response = text_translator.translate(
            content=input_text_elements,
            to=target_languages,
        )

        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                return translated_text.text
    except Exception as exception:
        logger.error(f"Error Code: {exception}")
