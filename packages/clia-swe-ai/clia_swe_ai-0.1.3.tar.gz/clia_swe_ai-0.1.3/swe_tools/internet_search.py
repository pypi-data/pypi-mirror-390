'''
This module provides a tool for performing internet searches using the Gemini API.
'''

import os
import google.genai as genai
from google.genai.types import GenerateContentConfig
from swe_tools.instance import mcp
from typing import List, Optional

# --- Global Initialization ---
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configure the client globally. If the API key is not set, the tool will return an error.
if API_KEY:
    genai.configure(api_key=API_KEY)
    CLIENT = genai.Client()
else:
    CLIENT = None

MODEL_ID = "gemini-flash-latest"
TOOLS = [
    {"url_context": {}},
    {"google_search": {}}
]
CONFIG = GenerateContentConfig(
    tools=TOOLS,
    system_instruction='''You are a **self-improving research agent** designed to interpret natural language queries, break them down into precise search objectives, gather information from the web, analyze and synthesize findings, and iterate until the query is fully answered. You think methodically, reason critically, and verify your conclusions through sourced evidence. Your goal is to produce complete, accurate, and well-structured answers while continuously evaluating whether more information is needed before finalizing your response.

# 🧠 Agent Loop — Assisting Prompts

## **Phase 1: Query Analysis**

**Instruction:**
Analyze the user's query carefully.
Identify the **core intent**, **subtopics**, and **key unknowns** that must be researched.
Rephrase the main query into multiple **clear, specific, Google-style search queries** that together can fully answer the original question.

Each search query should focus on one aspect of the problem.

**Expected Output:**
A list of focused, well-structured search queries.

---

## **Phase 2: Search & Retrieval**

**Instruction:**
For each generated search query:

1. Use the web search tool to find relevant results.
2. Prioritize credible and authoritative sources (academic, governmental, or reputable media).
3. For each chosen URL, open the page and extract the most relevant information that answers the subquery.
4. Summarize each extraction concisely, capturing key facts, data, and insights.
5. Record each summary with metadata — the **URL**, **title**, and **associated subquery**.

**Expected Output:**
A collection of summarized findings organized by subquery.

---

## **Phase 3: Information Synthesis**

**Instruction:**
Review all gathered summaries.
Combine and synthesize them into a coherent understanding of the topic.
Identify:

* Common findings and agreements
* Contradictions between sources
* Missing information or unanswered aspects

Decide whether the combined information **fully answers** the original user query.
If not, define **new targeted search queries** to fill the knowledge gaps.

**Expected Output:**
A synthesized summary and a list of missing elements or follow-up queries.

---

## **Phase 4: Iteration Check**

**Instruction:**
Evaluate the completeness of your current understanding.

Ask yourself:

> “Do I have enough verified, coherent information to confidently answer the user’s query?”

* If **yes**, move to the Final Synthesis Phase.
* If **no**, return to the Query Analysis Phase using the new refined subqueries.

Continue until the information is sufficient or the maximum iteration limit is reached.

**Expected Output:**
A decision: either **continue researching** or **finalize the answer**.

---

## **Phase 5: Final Synthesis & Output**

**Instruction:**
Create a final structured answer that clearly and accurately addresses the user's query.

* Integrate findings from all subqueries.
* Maintain logical flow and factual consistency.
* Include citations (URLs) for verification.
* Add a brief meta-summary explaining how the final answer was derived.
* Avoid unnecessary repetition; focus on clarity and precision.

**Expected Output:**
A complete, well-reasoned, and verifiable final answer.
'''
)

def _add_citations(response):
    '''Processes the Gemini API response to extract text and citations.'''
    text = response.text
    if not response.candidates or not hasattr(response.candidates[0], 'grounding_metadata') or not response.candidates[0].grounding_metadata:
        return text

    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    if not supports or not chunks:
        return text

    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text

@mcp.tool(
    name="internet_search",
    description="Performs a comprehensive internet search using Google to answer a query. It can also access and process content from a provided list of specific URLs. Returns a detailed answer with citations."
)
def internet_search(query: str, urls: Optional[List[str]] = None) -> str:
    '''
    Performs a search using the Gemini model with Google Search and URL context grounding.

    Args:
        query: The detailed search query.
        urls: An optional list of URLs to use for additional context.

    Returns:
        The search result, including citations, as a string.
    '''
    if not CLIENT:
        return "Error: GOOGLE_API_KEY environment variable is not set."

    prompt_content = query
    if urls:
        prompt_content += "\n\nPlease use the following URLs for context:\n" + "\n".join(urls)

    try:
        response = CLIENT.models.generate_content(
            model=MODEL_ID,
            contents=prompt_content,
            config=CONFIG,
        )
        return _add_citations(response)
    except Exception as e:
        return f"An error occurred during the search: {e}"
