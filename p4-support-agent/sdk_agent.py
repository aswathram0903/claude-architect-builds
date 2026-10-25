"""P4 session 2: the support agent on the Claude Agent SDK, with hooks and escalation rules."""
import asyncio
import json
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)

import backend

MODEL = "claude-haiku-5-5"  # check docs.claude.com for current model names
REFUND_LIMIT = 500

state = {"verified_customer_id": None, "looked_up": set()}

SYSTEM = """You are a customer support agent for an online office-supply shop. Resolve requests with the tools. Be brief.

Escalation rules:
- Escalate at once, without trying to resolve, if the customer asks for a human.
- Escalate if policy does not cover the request. Policy covers: refunds for delivered orders that arrived damaged, with a photo; order status questions.
- Escalate if a tool tells you to, or if you cannot make progress after one retry.
- Do NOT escalate a case the policy covers, even if the customer is upset or rude.

Examples:
- "My mug arrived cracked, photo attached, order A-1." -> verify, look up, refund. No escalation.
- "This is useless, get me a manager now." -> escalate at once, reason "customer asked for a human".
- "I changed my mind about the colour, refund please." -> change of mind is not covered -> escalate, reason "policy gap".

When you escalate, fill every field of escalate_to_human so the human never has to ask the customer again."""


def reply(result: dict) -> dict:
    """Wrap a backend result as an MCP tool result, marking failures as errors."""
    return {"content": [{"type": "text", "text": json.dumps(result)}], "is_error": bool(result.get("isError"))}


@tool("get_customer", "Find and verify a customer by email. Call this FIRST, before any order or refund action.", {"email": str})
async def get_customer(args):
    result = backend.get_customer(args["email"])
    if not result.get("isError"):
        state["verified_customer_id"] = result["customer_id"]
    return reply(result)


@tool("lookup_order", "Get one order's item, amount, status and whether a damage photo was received. Only for the verified customer's own orders.", {"order_id": str})
async def lookup_order(args):
    if not state["verified_customer_id"]:
        return reply(backend.error("prerequisite", "Blocked: verify the customer with get_customer first.", False))
    result = backend.lookup_order(args["order_id"], state["verified_customer_id"])
    if not result.get("isError"):
        state["looked_up"].add(args["order_id"])
    return reply(result)


@tool("process_refund", "Refund one delivered order of the verified customer, after lookup_order. Amount must not exceed the order amount.", {"order_id": str, "amount": float})
async def process_refund(args):
    if args["order_id"] not in state["looked_up"]:
        return reply(backend.error("prerequisite", "Blocked: look up this order first.", False))
    return reply(backend.process_refund(args["order_id"], args["amount"]))


@tool(
    "escalate_to_human",
    "Hand the case to a human agent. Fill every field so the human can act without asking the customer again.",
    {"customer_id": str, "order_id": str, "what_customer_wants": str, "what_was_checked": str, "reason": str, "recommended_action": str},
)
async def escalate_to_human(args):
    print("\n--- HANDOFF TO HUMAN ---")
    for key, value in args.items():
        print(f"  {key}: {value}")
    return reply(backend.escalate_to_human(args["what_customer_wants"], args["reason"]))


async def refund_limit(input_data, tool_use_id, context):
    """PreToolUse hook: runs in code before every refund, whatever Claude decided."""
    amount = input_data["tool_input"].get("amount", 0)
    if amount > REFUND_LIMIT:
        print(f"\n[HOOK PreToolUse] blocked a refund of {amount}: over the {REFUND_LIMIT} limit")
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Refunds over {REFUND_LIMIT} need a human. Do not retry. Call escalate_to_human with a full handoff.",
        }}
    return {}


async def audit(input_data, tool_use_id, context):
    """PostToolUse hook: runs after every tool and writes an audit line."""
    line = {"tool": input_data.get("tool_name"), "input": input_data.get("tool_input"), "output": input_data.get("tool_response")}
    with open("audit.jsonl", "a") as f:
        f.write(json.dumps(line, default=str) + "\n")
    return {}


async def main(prompt: str) -> None:
    server = create_sdk_mcp_server(
        name="shop", version="1.0.0", tools=[get_customer, lookup_order, process_refund, escalate_to_human]
    )
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM,
        max_turns=12,
        mcp_servers={"shop": server},
        allowed_tools=[
            "mcp__shop__get_customer",
            "mcp__shop__lookup_order",
            "mcp__shop__process_refund",
            "mcp__shop__escalate_to_human",
        ],
        disallowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch"],
        hooks={
            "PreToolUse": [HookMatcher(matcher="mcp__shop__process_refund", hooks=[refund_limit])],
            "PostToolUse": [HookMatcher(hooks=[audit])],
        },
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"\nAGENT: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  -> {block.name}({block.input})")
            elif isinstance(message, ResultMessage):
                print(f"\n[done] turns: {message.num_turns}, stop_reason: {message.stop_reason}, result: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "Hi, I'm anna@example.com. Order A-5001, the lamp arrived broken, photo sent. Refund please."))
