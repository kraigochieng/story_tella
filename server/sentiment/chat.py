import os
from flask import request
import google.generativeai as genai

# setup API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


context = "You are a speech specialist who is trying to gauge the sentiment of speech in novels. You offer the sentiments in the format of various human emotions like happiness, sadness, excitement, etc. When given a certain statement, try to gauge in which emotion is being exerted. Only capture speech. Ignore parts of sentences without quotation marks designated for beginning and end of speech. After deducing the format, present the speech captured and the sentiment. In you're responses add delimiters at the end of every response like \n\n"
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
        self.results = []

    def prompt(self,paragraph):
        print(paragraph)
        response = self.chat.send_message(paragraph)
        self.results.append(response.text)
        
    def get_results(self):
        return self.results
        


