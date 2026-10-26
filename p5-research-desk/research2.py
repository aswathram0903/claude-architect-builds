"""P5 session 2: research in parallel, then a synthesiser that keeps every claim tied to its source. Paper only."""
import asyncio
import sys
import time

from claude_agent_sdk import (
    AgentDefinition, AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient,
    HookMatcher, ResultMessage, ToolUseBlock,
)

MODEL = "claude-haiku-5-5"  # check docs.claude.com for current model names
SEQUENTIAL = "--sequential" in sys.argv  # P5.10: one subagent after the other, to compare the time

FINDING_FORMAT = """Return ONLY a JSON list of findings, no other text. Each finding:
{"claim": "...", "evidence_excerpt": "short exact quote from the source",
 "source": "URL, or file name and page number", "source_date": "YYYY-MM-DD or unknown",
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
        description="Reads local documents: the company's annual report text file and any broker notes. Use for the company's own figures and third-party estimates on file.",
        prompt="You analyse local documents named in your brief. In tcs-report.txt, pages are marked '=== PAGE n ==='. "
               "The report is long: use Grep to find the focus topics first, then Read only around the matching lines "
               "(use offset and limit). Give the file name and page number as the source. " + FINDING_FORMAT,
        tools=["Read", "Grep"],
        model="inherit",
        background=False,
    ),
    "synthesiser": AgentDefinition(
        description="Combines findings from the other subagents into one cited report. Has no tools: everything it needs must be in its brief.",
        prompt="""You write one research report from the findings in your brief. You have no tools and see nothing except the brief.
Rules:
- Every statement in the report carries its source and date in brackets, taken from the findings. No source, no statement.
- When two findings disagree (for example two different figures for the same thing), put both under the heading "Conflicts",
  side by side with their sources and dates. Do not pick one, average them or drop one. Say what might explain the
  difference: different dates, different definitions, or a company source versus a third party.
- End with "Coverage gaps": topics from the request that no finding covers.
- Paper-trading research only: no buy or sell advice.""",
        tools=[],
        model="inherit",
        background=False,
    ),
}

ORDER = ("Start news-researcher. Wait for its result. Only then start report-analyst."
         if SEQUENTIAL else
         "Start news-researcher and report-analyst in the SAME response: two Agent calls in one message, so they run in parallel.")

SYSTEM = f"""You coordinate research on one company for a personal paper-trading watchlist. Paper only: never suggest buying or selling.
You do not research or write the report yourself. You delegate with the Agent tool, in the foreground, and wait for results.

Steps:
1. {ORDER}
   Brief each one completely: subagents do not see this conversation. Include the company (TCS), the focus topics word for word,
   the time window, and for report-analyst the files tcs-report.txt and broker-note.txt.
2. When both have answered, start synthesiser. Its brief must contain the user's request and BOTH findings lists in full,
   pasted exactly as returned (JSON). Do not shorten, merge or re-word them: the sources must survive.
3. Your final answer is the synthesiser's report, unchanged."""


async def scope_tools(input_data, tool_use_id, context):
    """PreToolUse hook: the coordinator may only delegate, and the synthesiser may use no tools at all."""
    tool = input_data["tool_name"]
    reason = None
    if "agent_id" not in input_data and tool not in ("Agent", "Task"):
        reason = "The coordinator only delegates. Use the Agent tool to brief a subagent."
    elif input_data.get("agent_type") == "synthesiser":
        reason = "The synthesiser has no tools. Write the report from the findings in your brief only."
    if reason:
        print(f"\n[HOOK] blocked {input_data.get('agent_type', 'coordinator')} from using {tool}")
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
    return {}


async def main(request: str):
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM,
        agents=AGENTS,
        tools=["Agent", "Read", "Grep", "WebSearch", "WebFetch"],
        allowed_tools=["Agent", "Read", "Grep", "WebSearch", "WebFetch"],
        hooks={"PreToolUse": [HookMatcher(hooks=[scope_tools])]},
        max_turns=25,
        max_budget_usd=1.50,
        env={"CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1"},  # wait for subagents instead of sending them to the background
    )
    print(f"[mode] {'SEQUENTIAL' if SEQUENTIAL else 'PARALLEL'}")
    start = time.monotonic()
    coordinator_message = 0
    async with ClaudeSDKClient(options=options) as client:
        await client.query(request)
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                if msg.parent_tool_use_id is None:
                    coordinator_message += 1
                for block in msg.content:
                    if not isinstance(block, ToolUseBlock):
                        continue
                    if msg.parent_tool_use_id is None and block.name in ("Agent", "Task"):
                        brief = block.input.get("prompt", "")
                        print(f"\n==> [coordinator message {coordinator_message} · {time.monotonic() - start:.0f}s] "
                              f"briefs {block.input.get('subagent_type')} ({len(brief)} characters):\n{brief[:600]}"
                              f"{' …' if len(brief) > 600 else ''}\n")
                    elif msg.parent_tool_use_id is not None:
                        print(f"    [subagent] {block.name} {str(block.input)[:120]}")
            elif isinstance(msg, ResultMessage):
                elapsed = time.monotonic() - start
                print(f"\nREPORT:\n{msg.result}\n")
                print(f"[done] {'SEQUENTIAL' if SEQUENTIAL else 'PARALLEL'} · {elapsed:.0f} seconds · "
                      f"turns: {msg.num_turns} · cost: ${msg.total_cost_usd or 0:.3f} · result: {msg.subtype}")
                with open("report-sequential.md" if SEQUENTIAL else "report.md", "w") as f:
                    f.write(msg.result or "")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--sequential"]
    asyncio.run(main(" ".join(args) or
        "Research TCS for my paper-trading watchlist. Focus: revenue growth, AI services, and headcount or attrition. "
        "Time window: the last 12 months."))
