import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1
)

# Reducer Function
def merge_score_dicts(existing: dict, newupdate: dict) -> dict:
    if existing is None:
        return newupdate
    return {**existing, **newupdate}


# State
class AnalyzerState(TypedDict):
    raw_text: str
    safety_score: Annotated[dict[str, int], merge_score_dicts]


# Branch 1 - Toxicity
def toxicity_node(state: AnalyzerState) -> dict:
    print("\n🤬 [Branch 1] Analyzing Toxicity and Hate Speech...")

    prompt = (
        "Analyze the following text for profanity, aggression, hate speech, or toxicity.\n"
        "Provide a score from 0 to 100, where 0 means perfectly clean and 100 means highly toxic.\n"
        "Return ONLY the plain integer number, nothing else.\n\n"
        f"Text:\n{state['raw_text']}"
    )

    response = llm.invoke(prompt)

    try:
        score = int(response.content.strip())
    except ValueError:
        score = 0

    return {
        "safety_score": {
            "toxicity_level": score
        }
    }


# Branch 2 - Copyright
def copyright_node(state: AnalyzerState) -> dict:
    print("\n✍️ [Branch 2] Analyzing Copyright & Originality Risks...")

    prompt = (
        "Analyze the following text. Judge if it sounds heavily plagiarized, unoriginal, "
        "or presents a corporate trademark risk. Provide a score from 0 to 100, "
        "where 0 means entirely original and 100 means high risk. "
        "Return ONLY the plain integer number, nothing else.\n\n"
        f"Text:\n{state['raw_text']}"
    )

    response = llm.invoke(prompt)

    try:
        score = int(response.content.strip())
    except ValueError:
        score = 0

    return {
        "safety_score": {
            "copyright_risk": score
        }
    }


# Branch 3 - Culture
def culture_node(state: AnalyzerState) -> dict:
    print("\n🌍 [Branch 3] Analyzing Regional & Cultural Sensitivity...")

    prompt = (
        "Analyze the following text for cultural, regional, ethnic, religious, or national insensitivity. "
        "Check ONLY if the text insults or stereotypes a culture, religion, nationality, ethnicity, or region. "
        "Ignore general personal insults, profanity, or toxic language toward individuals. "
        "Provide a score from 0 to 100, where 0 means no cultural insensitivity and 100 means extremely culturally offensive. "
        "Return ONLY the plain integer number, nothing else.\n\n"
        f"Text:\n{state['raw_text']}"
    )

    response = llm.invoke(prompt)

    try:
        score = int(response.content.strip())
    except ValueError:
        score = 0

    return {
        "safety_score": {
            "cultural_insensitivity": score
        }
    }


# Graph
builder = StateGraph(AnalyzerState)

builder.add_node("toxicity_node", toxicity_node)
builder.add_node("copyright_check", copyright_node)
builder.add_node("culture_node", culture_node)

builder.add_edge(START, "toxicity_node")
builder.add_edge(START, "copyright_check")
builder.add_edge(START, "culture_node")

builder.add_edge("toxicity_node", END)
builder.add_edge("copyright_check", END)
builder.add_edge("culture_node", END)

app = builder.compile()


# Sample Input
sample_script = """
You are a complete idiot and a total loser.
Everything you do is pathetic and useless.
Nobody likes you because you ruin everything.
Your work is absolute garbage, and you always fail.
You should stop pretending you know anything because you're completely incompetent.
"""

initial_state = {
    "raw_text": sample_script,
    "safety_score": {}
}

final_state = app.invoke(initial_state)

print("\nFinal State:")
print(final_state)