from flask import render_template
from langgraph.graph import END, START, StateGraph

from . import summary
from .chapters import chapters
from .helper_functions import create_documents_from_paragraphs
from .nodes import (
    collapse_summaries,
    collect_summaries,
    generate_final_summary,
    generate_summary,
    map_summaries,
    should_collapse,
)
from .states import OverallState


@summary.get("/api/chapter/<int:chapter_number>")
async def summary_api(chapter_number):
    chapter = chapters[chapter_number - 1]

    documents = create_documents_from_paragraphs(chapter)

    # Nodes:
    graph = StateGraph(OverallState)
    graph.add_node("generate_summary", generate_summary)  # same as before
    graph.add_node("collect_summaries", collect_summaries)
    graph.add_node("collapse_summaries", collapse_summaries)
    graph.add_node("generate_final_summary", generate_final_summary)

    # Edges:
    graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
    graph.add_edge("generate_summary", "collect_summaries")
    graph.add_conditional_edges("collect_summaries", should_collapse)
    graph.add_conditional_edges("collapse_summaries", should_collapse)
    graph.add_edge("generate_final_summary", END)

    app = graph.compile()

    async for step in app.astream(
        {"contents": [doc.page_content for doc in documents]},
        {"recursion_limit": 20},
    ):
        # pass
        print(list(step.keys()))

        # Optionally print state variables for debugging
        if "contents" in step:
            print(f"Contents: {step['contents'][:2]}...")  # Show first 2 entries
        if "summaries" in step:
            print(f"Summaries: {step['summaries']}")
        if "collapsed_summaries" in step:
            print(f"Collapsed Summaries: {step['collapsed_summaries']}")
        if "final_summary" in step:
            print(f"Final Summary: {step['final_summary']}")

        print("-" * 50)  # Separator for readability

    return {
        "final_summary": step["generate_final_summary"]["final_summary"],
        "paragraphs": step["generate_final_summary"]["paragraphs"],
    }


@summary.get("/chapter/<int:chapter_number>")
async def index(chapter_number):
    data = await summary_api(chapter_number)
    return render_template(
        "index.html",
        chapter_number=chapter_number,
        final_summary=data["final_summary"],
        paragraphs=data["paragraphs"],
    )
