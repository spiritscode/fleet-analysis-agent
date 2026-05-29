import anthropic
from prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES
from tools import TOOLS, execute_tool
from context import build_context, log_token_usage

client = anthropic.Anthropic()
conversation_history = []

def run_agent(user_query: str) -> str:
    # Build context (manages history trimming)
    messages = build_context(user_query, 
                             FEW_SHOT_EXAMPLES + conversation_history)
    
    # Agent loop — keeps running until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )
        
        log_token_usage(response)  # always track cost
        
        # If Claude is done — no more tool calls
        if response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            # Add to history for next turn
            conversation_history.append({"role": "user", "content": user_query})
            conversation_history.append({"role": "assistant", "content": final_answer})
            return final_answer
        
        # Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response to messages
            messages.append({"role": "assistant", "content": response.content})
            
            # Execute every tool Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n→ Claude calling: {block.name}({block.input})")
                    result = execute_tool(block.name, block.input)
                    print(f"← Result: {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Feed results back — loop continues
            messages.append({"role": "user", "content": tool_results})

# Run it
if __name__ == "__main__":
    print("Fleet Intelligence Agent ready\n")
    while True:
        query = input("You: ").strip()
        if query.lower() == "quit":
            break
        answer = run_agent(query)
        print(f"\nAgent: {answer}\n")