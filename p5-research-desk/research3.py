"""P5 session 3: a subagent fails, the error reaches the coordinator in a useful form, and nothing can trade. Paper only."""
import asyncio
import json
import sys
import time

from claude_agent_sdk import (
    AgentDefinition, AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient,
    HookMatcher, ResultMessage, ToolUseBlock, create_sdk_mcp_server, tool,
)

MODEL = "claude-haiku-5-5"  # check docs.claude.com for current model names
TIMEOUT = "--timeout" in sys.argv  # P5.17: the news search "times out" every time
SWALLOW = "--swallow" in sys.argv  # P5.18: the bad design, failure hidden as an empty success

FINDING_FORMAT = """Return ONLY a JSON list of findings, no other text. Each finding:
{"claim": "...", "evidence_excerpt": "short exact quote from the source",
 "source": "URL, or file name and page number", "source_date": "YYYY-MM-DD or unknown",
 "confidence_basis": "what the claim rests on, e.g. company's own report, one news article, several sources agree"}
Return 3 to 6 findings. If you find nothing, return [] and do not invent anything."""

GOOD_ERRORS = """If your tools fail, do not return []. Return ONLY this JSON object:
{"status": "error", "error_type": "timeout | no_access | other", "attempted_queries": ["..."],
 "partial_results": [findings you got before the failure, or []], "suggested_alternatives": ["..."]}"""

SWALLOWED_ERRORS = "If your tools fail, return [] and say nothing about the failure."

AGENTS = {
    "news-researcher": AgentDefinition(
        description="Finds recent news about a company on the web. Use for events, analyst views and anything after the annual report.",
        prompt="You research recent news about one company. Use only the brief you are given: it states the company, "
               "the focus and the time window. Prefer named, dated sources. Retry a failed search at most once. "
               + FINDING_FORMAT + "\n" + (SWALLOWED_ERRORS if SWALLOW else GOOD_ERRORS),
        tools=["WebSearch", "WebFetch"],
        model="inherit",
        background=False,
    ),
    "report-analyst": AgentDefinition(
        description="Reads local documents: the company's annual report text file and any broker notes.",
        prompt="You analyse local documents named in your brief. In tcs-report.txt, pages are marked '=== PAGE n ==='. "
               "The report is long: use Grep to find the focus topics first, then Read only around the matching lines "
               "(use offset and limit). Give the file name and page number as the source. " + FINDING_FORMAT,
        tools=["Read", "Grep"],
        model="inherit",
        background=False,
    ),
    "synthesiser": AgentDefinition(
        description="Combines findings from the other subagents into one cited report. Has no tools.",
        prompt="""You write one research report from the findings and errors in your brief. You have no tools.
Rules:
- Every statement carries its source and date in brackets. No source, no statement.
- When two findings disagree, put both under "Conflicts", side by side with sources and dates. Do not pick, average or drop.
- End with "Coverage gaps": every topic from the request that no finding covers, AND every subagent error, with its
  type, what was attempted and what could be tried next. A reader must be able to see what this report does NOT rest on.
- Paper-trading research only: no buy or sell advice.""",
        tools=[],
        model="inherit",
        background=False,
    ),
}

SYSTEM = """You coordinate research on one company for a personal paper-trading watchlist. Paper only.
You do not research or write the report yourself. You delegate with the Agent tool, in the foreground, and wait for results.

Steps:
1. Start news-researcher and report-analyst in the SAME response. Brief each one completely: the company (TCS), the focus
   topics word for word, the time window, and for report-analyst the files tcs-report.txt and broker-note.txt.
2. If a subagent returns an error object, do not stop the whole job and do not hide it. Decide: retry once with a changed
   brief if the error suggests that could help, otherwise carry on with what you have.
3. Start synthesiser with the user's request, both results in full exactly as returned (findings AND any error objects).
4. Your final answer is the synthesiser's report, unchanged.
You cannot place orders. If asked to trade, say this desk is research only."""


@tool("place_order", "Place a buy or sell order with the broker.", {"ticker": str, "side": str, "quantity": int})
async def place_order(args):
    # Never reached: the paper_only hook denies every call before it runs.
    return {"content": [{"type": "text", "text": "ORDER SENT"}]}


async def guard(input_data, tool_use_id, context):
    """PreToolUse hook, three rules, all in code: no trading, roles stay separate, and (in --timeout) news search fails."""
    tool_name = input_data["tool_name"]
    agent = input_data.get("agent_type", "coordinator") if "agent_id" in input_data else "coordinator"
    reason = None
    if tool_name == "mcp__desk__place_order":
        reason = "Paper only. This desk never places orders. Tell the user it is research only."
    elif agent == "coordinator" and tool_name not in ("Agent", "Task"):
        reason = "The coordinator only delegates. Use the Agent tool to brief a subagent."
    elif agent == "synthesiser":
        reason = "The synthesiser has no tools. Write the report from your brief only."
    elif TIMEOUT and agent == "news-researcher" and tool_name in ("WebSearch", "WebFetch"):
        reason = "TIMEOUT: the search service did not respond within 30 seconds."
    if reason:
        print(f"\n[HOOK] blocked {agent} from using {tool_name}: {reason.split('.')[0]}")
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
    return {}


async def main(request: str):
    desk = create_sdk_mcp_server(name="desk", version="1.0.0", tools=[place_order])
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM,
        agents=AGENTS,
        mcp_servers={"desk": desk},
        tools=["Agent", "Read", "Grep", "WebSearch", "WebFetch"],
        allowed_tools=["Agent", "Read", "Grep", "WebSearch", "WebFetch", "mcp__desk__place_order"],
        hooks={"PreToolUse": [HookMatcher(hooks=[guard])]},
        max_turns=25,
        max_budget_usd=1.50,
        env={"CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1"},  # wait for subagents instead of sending them to the background
    )
    mode = "TIMEOUT + SWALLOW" if TIMEOUT and SWALLOW else "TIMEOUT" if TIMEOUT else "NORMAL"
    print(f"[mode] {mode}")
    start = time.monotonic()
    async with ClaudeSDKClient(options=options) as client:
        await client.query(request)
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if not isinstance(block, ToolUseBlock):
                        continue
                    if msg.parent_tool_use_id is None:
                        if block.name in ("Agent", "Task"):
                            brief = block.input.get("prompt", "")
                            print(f"\n==> [{time.monotonic() - start:.0f}s] briefs {block.input.get('subagent_type')} "
                                  f"({len(brief)} characters)")
                            if '"status": "error"' in brief or "error_type" in brief:
                                print("    (this brief passes on an error object)")
                        else:
                            print(f"\n==> coordinator tries {block.name} {json.dumps(block.input)[:100]}")
                    else:
                        print(f"    [subagent] {block.name} {str(block.input)[:100]}")
            elif isinstance(msg, ResultMessage):
                print(f"\nREPORT:\n{msg.result}\n")
                print(f"[done] {mode} · {time.monotonic() - start:.0f} seconds · turns: {msg.num_turns} · "
                      f"cost: ${msg.total_cost_usd or 0:.3f} · result: {msg.subtype}")
                name = {"TIMEOUT": "report-timeout.md", "TIMEOUT + SWALLOW": "report-swallow.md"}.get(mode, "report-s3.md")
                with open(name, "w") as f:
                    f.write(msg.result or "")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a not in ("--timeout", "--swallow")]
    asyncio.run(main(" ".join(args) or
        "Research TCS for my paper-trading watchlist. Focus: revenue growth, AI services, and headcount or attrition. "
        "Time window: the last 12 months."))
