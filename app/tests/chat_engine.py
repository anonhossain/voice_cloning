import os
import json
from dotenv import load_dotenv
from openai import OpenAI

class Chatbot:
    def __init__(self, api_key: str = None, history_dir: str = "chat_history"):
        """
        Initializes the Chatbot with API key and chat history directory.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OpenAI API key not found in environment or provided.")

        self.client = OpenAI(api_key=self.api_key)
        self.system_message = "You are a warm, caring AI loved one. Always reply affectionately and naturally."

        # Chat history directory
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)
        self.history_file = os.path.join(self.history_dir, "messages.json")

    def generate_prompt(self, user_input: str, chat_history: list):
        """Generates the conversational prompt."""
        prompt = f"""
        You are an AI assistant acting as the user's loved one.  
        Your goal is to have a warm, caring, and supportive conversation with the user.  

        **User input:** "{user_input}"

        ### Chat history:
        {json.dumps(chat_history, indent=2)}

        Respond briefly and warmly, like a one-to-one conversation.
        """
        return prompt

    def get_ai_response(self, messages: list):
        """Fetches AI response using the new OpenAI Python client."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or gpt-4-turbo
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            # The content is in: response.choices[0].message.content
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error getting response from AI: {e}")
            return None

    def update_chat_history(self, messages: list, ai_response_text: str):
        """Appends AI response to chat history and saves it."""
        messages.append({"role": "assistant", "content": ai_response_text})
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            print(f"✅ Chat history saved at: {self.history_file}")
        except Exception as e:
            print(f"❌ Error saving messages: {e}")

    def run_chat(self, user_input: str, chat_history: list):
        """Runs the chat, generates prompt, gets AI response, and updates chat history."""
        prompt = self.generate_prompt(user_input, chat_history)

        messages = [{"role": "system", "content": self.system_message}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": prompt})

        ai_response_text = self.get_ai_response(messages)
        if ai_response_text:
            print(f"AI says: {ai_response_text}")
            self.update_chat_history(messages, ai_response_text)
        else:
            print("❌ Could not get a response from the AI.")


# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    chat_history = [
    ]
    user_input = "How are you?"

    chatbot = Chatbot(history_dir=r"C:\files\voice-cloning\file\assets\output\chat_history")
    chatbot.run_chat(user_input, chat_history)
