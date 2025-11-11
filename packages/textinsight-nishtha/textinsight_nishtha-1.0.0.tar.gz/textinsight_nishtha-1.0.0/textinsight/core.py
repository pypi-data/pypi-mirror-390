import re
import string

class TextInsight:
    """
    A simple NLP utility for cleaning, analyzing, and transforming text.
    """

    def __init__(self, text):
        self.original = text
        self.cleaned = self.clean_text(text)

    def clean_text(self, text):
        """Remove emojis, URLs, and special characters."""
        text = re.sub(r"http\S+|www\S+|https\S+", "", text)
        text = re.sub(r"[^\w\s.,!?']", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def word_count(self):
        """Return total word count."""
        return len(self.cleaned.split())

    def sentence_count(self):
        """Return total sentence count."""
        return len(re.findall(r"[.!?]", self.cleaned)) or 1

    def avg_sentence_length(self):
        """Average number of words per sentence."""
        return round(self.word_count() / self.sentence_count(), 2)

    def sentiment(self):
        """Basic sentiment detection using keyword matching."""
        positive_words = ["good", "great", "happy", "love", "excellent", "awesome"]
        negative_words = ["bad", "sad", "terrible", "hate", "awful", "poor"]

        pos = sum(word in self.cleaned.lower() for word in positive_words)
        neg = sum(word in self.cleaned.lower() for word in negative_words)

        if pos > neg:
            return "Positive 😊"
        elif neg > pos:
            return "Negative 😞"
        else:
            return "Neutral 😐"

    def to_title_case(self):
        return self.cleaned.title()

    def to_sentence_case(self):
        return self.cleaned.capitalize()

    def summary(self):
        """Return a mini insight summary of the text."""
        return {
            "original": self.original,
            "cleaned": self.cleaned,
            "word_count": self.word_count(),
            "sentence_count": self.sentence_count(),
            "avg_sentence_length": self.avg_sentence_length(),
            "sentiment": self.sentiment(),
        }
