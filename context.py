MAX_HISTORY_TURNS = 5  # never let history grow unbounded

def build_context(user_query: str, history: list) -> list:
    """
    Constructs the messages array sent to Claude.
    Trims history to last N turns to control token usage.
    """
    # Only keep last MAX_HISTORY_TURNS exchanges
    trimmed_history = history[-(MAX_HISTORY_TURNS * 2):]
    
    return trimmed_history + [
        {"role": "user", "content": user_query}
    ]

def estimate_tokens(messages: list) -> int:
    """Rough token estimate: ~4 chars per token"""
    total_chars = sum(len(str(m)) for m in messages)
    return total_chars // 4

def log_token_usage(response) -> None:
    """Token economics — always log what you spend"""
    usage = response.usage
    input_cost  = (usage.input_tokens  / 1_000_000) * 3.00   # Sonnet pricing
    output_cost = (usage.output_tokens / 1_000_000) * 15.00
    print(f"Tokens: {usage.input_tokens} in / {usage.output_tokens} out")
    print(f"Cost this call: ${input_cost + output_cost:.5f}")