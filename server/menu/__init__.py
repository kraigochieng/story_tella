from flask import Blueprint, render_template

menu = Blueprint("menu", __name__)


@menu.route("/", methods=["GET"])
@menu.route("/<chapter>")
def main(chapter=None):
    return render_template("index.html", chap=chapter)


@menu.route("/<chapter>/summary")
def chapter_summary(summary=None):
    return render_template("index.html", sum=summary)
