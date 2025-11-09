# goal/goal_planner.py
from typing import List, Dict, Any
from spider_core.llm.openai_gpt_client import OpenAIGPTClient

GOAL_SYSTEM = (
  "You are a goal-driven web research planner. "
  "Given a user GOAL and a PAGE CHUNK, you will: "
  "1) estimate if the GOAL is fully answered by this page content (0-1), "
  "2) extract a concise answer delta (new facts that progress the goal), "
  "3) propose next links (subset of candidates) most likely to progress the goal."
)

def build_user_prompt(goal: str, chunk_text: str, link_candidates: List[Dict[str, str]]) -> str:
    return (
        f"GOAL:\n{goal}\n\n"
        f"PAGE CHUNK:\n{chunk_text[:4000]}\n\n"
        f"LINK CANDIDATES (href + text):\n{[{'href': l['href'], 'text': l.get('text','')} for l in link_candidates]}\n\n"
        "Return JSON: {"
        '"goal_satisfaction_estimate": 0..1, '
        '"answer_delta": "short text", '
        '"next_link_scores": [{"href":"...","score":0..1}]'
        "}"
    )

class GoalPlanner:
    def __init__(self, llm: OpenAIGPTClient):
        self.llm = llm

    async def evaluate_chunk(self, goal: str, chunk_text: str, link_candidates: List[Dict[str, Any]]):
        prompt = build_user_prompt(goal, chunk_text, link_candidates)
        out = await self.llm.complete_json(GOAL_SYSTEM, prompt)
        # normalize
        est = float(out.get("goal_satisfaction_estimate", 0.0))
        delta = out.get("answer_delta", "").strip()
        next_scores = out.get("next_link_scores", [])
        scored = {x["href"]: float(x.get("score", 0.0)) for x in next_scores if "href" in x}
        return est, delta, scored
