from flask import Blueprint, render_template
from server.menu.obtainchapters import obtainchapterarray
from server.summarization.routes import summary_api
import requests
import re

menu = Blueprint("menu", __name__)

chapters = obtainchapterarray()
chapnos = 0
chapter = None

@menu.route("/<chapter>")
@menu.route("/<chapter>/summary", methods=["GET"])
async def main(chapter=None):
    if chapter is None:
        chapter = 1

    data = await summary_api(int(chapter))
    return render_template(
        "summary.html",
        chapter_number=int(chapter),
        final_summary=data["final_summary"],
        paragraphs=data["paragraphs"],
    )


@menu.route("/<chapter>/themes",methods=["GET"])
def chapter_themes(chapter=None):
    themes = ""
    chapnos= chapter
    chapter = chapters[int(chapter)-1]
    try:
        themes = requests.post("http://127.0.0.1:5000/",{"data":f"{chapter}"})
        themes = themes.text
    except Exception as e:
        themes = f"Error fetching sentiments: {str(e)}"

    return render_template("index.html", content=themes,chapter = chapnos)
    

@menu.route("/<chapter>/characters",methods=["GET"])
def chapter_characters(chapter=None):
    characters = ""
    chapnos= chapter
    chapter = chapters[int(chapter)-1]
    try:
        characters = requests.post("http://127.0.0.1:5000/",{"data":f"{chapter}"})
        characters = characters.text
    except Exception as e:
        characters = f"Error fetching sentiments: {str(e)}"
        
    return render_template("index.html", content=characters,chapter = chapnos)

@menu.route("/<chapter>/sentiments",methods=["GET"])
def chapter_sentiments(chapter=None):
    sentiments = ""
    chapnos= chapter
    chapter = chapters[int(chapter)-1]
    try:
        sentiments = requests.post("http://127.0.0.1:5000/sentiments/",{"data":f"{chapter}"})
        # sentiments = sentiments.text
        sentiments = sentiments.json().get("data", "No sentiment data available.")
        
        sentiments = clean_response(sentiments)
        
        

    except Exception as e:
       sentiments = f"Error fetching sentiments: {str(e)}"
        
    return render_template("sentiment.html", content=sentiments,chapter = chapnos)





def clean_response(response_data):
    # Replace newline sequences with a space
    cleaned_text = response_data.replace("\\n\\n\\n***\\n", "\n\n")
    
    cleaned_text = cleaned_text.replace("\n\n***\n", "\n\n")

    # Remove square brackets []
    cleaned_text = re.sub(r"[\[\]]", "", cleaned_text)

    return cleaned_text.strip()
