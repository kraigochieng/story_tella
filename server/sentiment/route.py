import os
from server.sentiment import sentiment
from flask import request
import google.generativeai as genai

# setup API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


context = "You are a speech specialist who is trying to gauge the sentiment of speech in novels. You offer the sentiments in the format of various human emotions like happiness, sadness, excitement, etc. When given a certain statement, try to gauge in which emotion is being exerted. Only capture speech. Ignore parts of sentences without quotation marks designated for beginning and end of speech. After deducing the format, present the speech captured and the sentiment."
# setup model
model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=context)


class chat:
    def __init__(self, model):
        self.chat = model.start_chat(
            history=[
                {"role": "user", "parts": "Hello"},
                {
                    "role": "model",
                    "parts": "Great to meet you. What would you like to know?",
                },
            ]
        )
        self.results = {}

    def prompt(self):
        question = "The cat was in the air. 'Catch it please.' The boy remarked. The cat fell into the hands of the firefighter.'You did it!' The boy screamt."
        response = self.chat.send_message(question)
        print(response.text)
        self.results[f"{question}"] = response.text
        print("\n\n")
        for row in self.results:
            print(row)

