from flask import Blueprint,request,jsonify
sentiment = Blueprint("sentiment", __name__)

from server.sentiment.chat import chat,model

@sentiment.route("/", methods=["POST"])
def get_sentiment():
    try:
        instance = chat(model)
        if request.method == 'POST':
            paragraphs = request.form['data']
            chunk_size = 2000
            paragraphs = [paragraphs[i:i + chunk_size] for i in range(0, len(paragraphs), chunk_size)]
            for row in paragraphs:
                instance.prompt(row)
            
            
            data= instance.get_results()
        
            return {"data":f"{instance.get_results()}"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

