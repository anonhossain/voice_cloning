# module/text_summarizer.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class Summarizer:
    """Summarize input text using OpenAI GPT models."""

    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo"):
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
            f"""
            You are given a full transcript generated from a podcast speaker’s voice. 
            Your task is to transform this transcript into a shorter 5–10 minute narrative script while preserving the speaker’s natural tone, intent, and style.

            Follow these rules:

            1. Treat the input as the speaker’s own words. Keep the speaker’s original sentences and phrasing wherever possible.
            2. Remove unnecessary parts: filler words, repetition, long pauses, unrelated tangents, and any low-value conversations.
            3. Maintain the speaker’s flow and personality. It should feel like the speaker is still talking.
            4. When presenting important statements or ideas, introduce them naturally with:
            “The speaker said…” or “The speaker explained…”
            5. You may create short connecting lines between sections to ensure smooth flow, but they must sound natural and should never mention that they are added or generated.
            6. Do NOT produce a high-level summary. Instead, create a shorter narrative version of the actual content, preserving real wording and real meaning.
            7. Do NOT add new ideas, interpretations, or commentary that were not in the transcript.
            8. The final result should be a clean, continuous script suitable for text-to-speech voice generation.

            Here is the transcript to refine:

            {input_text}

            Now produce the refined narrative script.

        """
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()
