import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text before parsing.
    """

    # remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)

    # remove multiple blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    # remove mailto:
    text = text.replace("mailto\\:", "")

    return text.strip()