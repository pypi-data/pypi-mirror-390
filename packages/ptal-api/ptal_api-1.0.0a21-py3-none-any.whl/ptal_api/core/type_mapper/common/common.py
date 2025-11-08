import os
import re

from transliterate import translit

valid_character_pattern = re.compile("[^a-zA-Z 0-9]+")
space_pattern = re.compile("[ ]+")


def perform_transliteration(text_string: str, language_code: str = "ru", _reversed: bool = True) -> str:
    transliterated_text = translit(text_string, language_code=language_code, reversed=_reversed)
    return space_pattern.sub("_", valid_character_pattern.sub("", transliterated_text).strip()).lower()


def generate_file(input_data: bytes, file_path: str) -> None:
    directory_path = os.path.dirname(file_path)
    if directory_path and not os.path.exists(directory_path):
        os.makedirs(directory_path)

    with open(file_path, "wb") as file:
        file.write(input_data)
