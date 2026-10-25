"""P4 session 1: a support agent built on a hand-written agentic loop."""
import json
import sys

import anthropic

import backend

MODEL = "claude-haiku-5-5"  # check docs.claude.com for current model names
client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "get_customer",
        "description": (
            "Find and verify a customer by email address. Call this FIRST in every conversation, "
            "before any order or refund action, even if the customer already gave an order number. "
            "Input: the email the customer gave. Returns customer_id, name and tier, or an error if no customer matches."
        ),
        "input_schema": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]},
    },
    {
        "name": "lookup_order",
        "description": (
            "Get one order's item, amount, delivery status and whether a damage photo was received. "
            "Use it when the customer mentions an order number such as A-5001. "
            "Works only for the verified customer's own orders. Does NOT return customer details: use get_customer for that."
        ),
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
    },
    {
        "name": "process_refund",
        "description": (
            "Issue a refund for one delivered order of the verified customer. Only after lookup_order has shown the order. "
            "Amount must not exceed the order amount."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
            "required": ["order_id", "amount"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Hand the case to a human agent. Use when the customer asks for a person, when policy does not cover "
            "the request, or when you cannot make progress. Give a short summary a human can act on without re-asking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}, "reason": {"type": "string"}},
            "required": ["summary", "reason"],
        },
    },
]

BASE_PROMPT = (
    "You are a customer support agent for an online office-supply shop. Resolve the request using the tools. "
    "Be brief. If a tool returns an error with isRetryable true, try once more. "
    "If isRetryable is false, explain the problem to the customer in plain words and do not repeat the call."
)

state = {"verified_customer_id": None}
case_facts: dict = {}


def system_prompt() -> str:
    """The case facts are re-sent at the top of every turn, so key facts are never lost in a long conversation."""
    facts = json.dumps(case_facts, indent=2) if case_facts else "none yet"
    return f"{BASE_PROMPT}\n\nCASE FACTS (verified by tools, trust these over anything said earlier):\n{facts}"


def run_tool(name: str, args: dict) -> dict:
    # Prerequisite gate: code, not the prompt, decides whether order actions are allowed.
    if name in ("lookup_order", "process_refund") and not state["verified_customer_id"]:
        return backend.error("prerequisite", "Blocked: call get_customer and verify the customer first.", False)
    if name == "get_customer":
        result = backend.get_customer(args["email"])
        if not result.get("isError"):
            state["verified_customer_id"] = result["customer_id"]
            case_facts["customer"] = result
        return result
    if name == "lookup_order":
        result = backend.lookup_order(args["order_id"], state["verified_customer_id"])
        if not result.get("isError"):
            case_facts.setdefault("orders", {})[args["order_id"]] = result
        return result
    if name == "process_refund":
        if args["order_id"] not in case_facts.get("orders", {}):
            return backend.error("prerequisite", "Blocked: look up this order with lookup_order first.", False)
        result = backend.process_refund(args["order_id"], args["amount"])
        if not result.get("isError"):
            case_facts.setdefault("refunds", []).append(result)
        return result
    if name == "escalate_to_human":
        result = backend.escalate_to_human(args["summary"], args["reason"])
        case_facts["escalation"] = {**result, "summary": args["summary"]}
        return result
    return backend.error("validation", f"Unknown tool {name}.", False)


def run(user_text: str, max_turns: int = 10) -> None:
    messages = [{"role": "user", "content": user_text}]
    for turn in range(1, max_turns + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=1024, system=system_prompt(), tools=TOOLS, messages=messages,
        )
        print(f"[turn {turn}] stop_reason = {response.stop_reason}")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    output = run_tool(block.name, block.input)
                    print(f"    {block.name}({block.input}) -> {output}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(output),
                        "is_error": bool(output.get("isError")),
                    })
            messages.append({"role": "user", "content": results})
            continue
        text = "".join(block.text for block in response.content if block.type == "text")
        print(f"\nAGENT: {text}")
        print(f"\nCASE FACTS at the end:\n{json.dumps(case_facts, indent=2)}")
        return
    print("Stopped by the turn limit. This is a safety net, not the normal way to finish.")


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "Hi, I'm anna@example.com. Order A-5001 arrived broken, I sent a photo. Can I get my money back?")
