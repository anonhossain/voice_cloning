# module/text_summarizer.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class Summarizer:
    """Summarize input text using OpenAI GPT models."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the summarizer.
        :param api_key: OpenAI API key (optional, falls back to .env)
        :param model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OpenAI API key not found in environment or provided.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def summarize(self, input_text: str, max_tokens: int = 500, temperature: float = 1.0) -> str:
        """
        Summarize input text.
        :param input_text: Text to summarize
        :param max_tokens: Maximum tokens for response
        :param temperature: Creativity level for the summary.
        :return: Summarized text
        """
        prompt = (
            f"Summarize the following text clearly and concisely for a 5-7 minute speech. "
            f"Try to keep as many words from the input text as possible:\n\n{input_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()
