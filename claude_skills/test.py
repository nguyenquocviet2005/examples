"""
⚠️  CRITICAL SECURITY WARNING ⚠️
The API key you exposed needs to be REVOKED IMMEDIATELY at:
https://platform.openai.com/api-keys

Never commit API keys to code or share them publicly!
"""

# Option 1: Install OpenAI package and use it properly
# Run: pip install openai
# Then uncomment below:

# import os
# from openai import OpenAI
# 
# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY")  # Use env var!
# )
# 
# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     max_tokens=1024,
#     messages=[{"role": "user", "content": "Hello, GPT"}]
# )
# print(response.choices[0].message.content)


# Option 2: Use Anthropic client with Anthropic API
import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")  # Use env var!
)

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}]
)
print(message.content)


print("\n⚠️  REMEMBER: Revoke your exposed OpenAI key immediately!")