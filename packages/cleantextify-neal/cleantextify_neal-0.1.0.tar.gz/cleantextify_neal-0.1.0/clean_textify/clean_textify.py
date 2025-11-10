import re
import html
import string

class CleanText:
    """A lightweight text cleaning utility."""

    def __init__(self, lowercase=True, remove_punct=True):
        self.lowercase = lowercase
        self.remove_punct = remove_punct

    def clean(self, text: str) -> str:
        """Clean a text string by removing unwanted characters and noise."""
        text = html.unescape(text)
        text = re.sub(r"http\S+", "", text)                 # Remove URLs
        text = re.sub(r"@\w+", "", text)                    # Remove mentions
        text = re.sub(r"#\w+", "", text)                    # Remove hashtags
        text = re.sub(r"\d+", "", text)                     # Remove digits
        text = re.sub(r"\s+", " ", text).strip()            # Normalize spaces

        if self.lowercase:
            text = text.lower()
        if self.remove_punct:
            text = text.translate(str.maketrans("", "", string.punctuation))

        return text

# Quick helper
def clean_text(text: str) -> str:
    """Shortcut function"""
    return CleanText().clean(text)
