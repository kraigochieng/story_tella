from flask import Blueprint, render_template
from server.menu.obtainchapters import obtainchapterarray
import requests

menu = Blueprint("menu", __name__)

chapters = obtainchapterarray()
chapnos = 0
chapter = None

@menu.route("/<chapter>")
@menu.route("/<chapter>/summary", methods=["GET"])
def main(chapter=None):
    summary = ""
    chapnos= chapter
    chapter = chapters[int(chapter)-1]
    try:
        summary = requests.post("http://127.0.0.1:5000/",{"data":f"{chapter}"})
        summary = summary.text
    except Exception as e:
        summary = f"Error fetching sentiments: {str(e)}"

    return render_template("index.html", content=summary,chapter = chapnos)

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
        
        

    except Exception as e:
       sentiments = f"Error fetching sentiments: {str(e)}"
        
    return render_template("sentiment.html", content=sentiments,chapter = chapnos)
