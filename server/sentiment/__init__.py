from flask import Blueprint,request
sentiment = Blueprint("sentiment", __name__)

from server.sentiment.chat import chat

@sentiment.route("/", methods=["POST"])
def get_sentiment():
    try:
        instance = chat()
        if request.method == 'POST':
            paragraphs = request.form['data']
            for paragraph in paragraphs:
                chat.prompt(paragraph)
        
        return {"data":f"{instance.get_results()}"}
    except Exception as e:
        return {"data":e}

