"""P5 session 1: a coordinator that delegates TCS research to two subagents. Paper only, no trading."""
import asyncio
import sys

from claude_agent_sdk import (
    AgentDefinition, AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient,
    HookMatcher, ResultMessage, ToolUseBlock,
)

MODEL = "claude-haiku-5-5"  # check docs.claude.com for current model names
REPORT_FILE = "tcs-report.txt"
LAZY = "--lazy" in sys.argv  # P5.5: brief the subagents badly on purpose

FINDING_FORMAT = """Return ONLY a JSON list of findings, no other text. Each finding:
{"claim": "...", "evidence_excerpt": "short exact quote from the source",
 "source": "URL, or report page number", "source_date": "YYYY-MM-DD or unknown",
 "confidence_basis": "what the claim rests on, e.g. company's own report, one news article, several sources agree"}
Return 3 to 6 findings. If you find nothing, return [] and do not invent anything."""

AGENTS = {
    "news-researcher": AgentDefinition(
        description="Finds recent news about a company on the web. Use for events, analyst views and anything after the annual report.",
        prompt="You research recent news about one company. Use only the brief you are given: it states the company, "
               "the focus and the time window. Prefer named, dated sources. " + FINDING_FORMAT,
        tools=["WebSearch", "WebFetch"],
        model="inherit",
        background=False,
    ),
    "report-analyst": AgentDefinition(
        description="Reads the company's annual report text file. Use for the company's own figures, strategy and stated risks.",
        prompt="You analyse one annual report saved as a text file. The brief tells you the file name and the focus. "
               "Pages are marked '=== PAGE n ==='. The file is long: use Grep to find the focus topics first, then Read "
               "only around the matching lines (use offset and limit). Give the page number as the source. " + FINDING_FORMAT,
        tools=["Read", "Grep"],
        model="inherit",
        background=False,
    ),
}

GOOD_BRIEF = f"""Pass each subagent a complete brief in its prompt. Subagents do not see this conversation, so the brief must contain:
- the company (Tata Consultancy Services, TCS)
- the focus topics from the user's request, word for word
- the time window
- for report-analyst: the file name {REPORT_FILE}
- the finding format: they already know it, but remind them to return JSON only"""

LAZY_BRIEF = "Keep the subagent prompts very short. Pass each subagent only these three words: 'Research TCS please.'"

SYSTEM = f"""You coordinate research on one company for a personal paper-trading watchlist. Paper only: never suggest buying or selling.
You do not research yourself. You delegate to the subagents news-researcher and report-analyst with the Agent tool.
Run them in the foreground and wait for both results before you write anything.

{LAZY_BRIEF if LAZY else GOOD_BRIEF}

When both have answered, write a short summary: the findings grouped by topic, each with its source and date.
Then list what is missing: topics from the request that no finding covers."""


async def coordinator_only_delegates(input_data, tool_use_id, context):
    """PreToolUse hook: the coordinator (no agent_id) may only use the Agent tool. Subagents use their own tools."""
    if "agent_id" not in input_data and input_data["tool_name"] not in ("Agent", "Task"):
        print(f"\n[HOOK] blocked coordinator from using {input_data['tool_name']}")
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "The coordinator only delegates. Use the Agent tool to brief a subagent.",
        }}
    return {}


async def main(request: str):
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM,
        agents=AGENTS,
        tools=["Agent", "Read", "Grep", "WebSearch", "WebFetch"],
        allowed_tools=["Agent", "Read", "Grep", "WebSearch", "WebFetch"],
        hooks={"PreToolUse": [HookMatcher(hooks=[coordinator_only_delegates])]},
        max_turns=20,
        max_budget_usd=1.00,
        env={"CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1"},
    )
    print(f"[mode] {'LAZY brief' if LAZY else 'complete brief'}")
    async with ClaudeSDKClient(options=options) as client:
        await client.query(request)
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if not isinstance(block, ToolUseBlock):
                        continue
                    if msg.parent_tool_use_id is None and block.name in ("Agent", "Task"):
                        print(f"\n==> COORDINATOR briefs {block.input.get('subagent_type')}:\n{block.input.get('prompt')}\n")
                    elif msg.parent_tool_use_id is not None:
                        print(f"    [subagent] {block.name} {str(block.input)[:120]}")
            elif isinstance(msg, ResultMessage):
                print(f"\nCOORDINATOR SUMMARY:\n{msg.result}\n")
                print(f"[done] turns: {msg.num_turns}, cost: ${msg.total_cost_usd or 0:.3f}, result: {msg.subtype}")
                with open("run-lazy.md" if LAZY else "run.md", "w") as f:
                    f.write(msg.result or "")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--lazy"]
    asyncio.run(main(" ".join(args) or
        "Research TCS for my paper-trading watchlist. Focus: revenue growth, AI services, and headcount or attrition. "
        "Time window: the last 12 months."))
