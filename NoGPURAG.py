import requests
import json

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer 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",
        "HTTP-Referer": f"Dons No SQL page",  # Optional, for including your app on openrouter.ai rankings.
        "X-Title": f"NGPU RAG",  # Optional. Shows in rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "openai/gpt-3.5-turbo",  # Optional
        "messages": [
            {"role": "user", "content": "What is the meaning of life?"}
        ]
    })
)

# Print the status code (e.g., 200 for success)
print(f"Status Code: {response.status_code}")

# Print the entire response object (useful for debugging)
# print(response.json())

# Access and print the generated response from the API
if response.status_code == 200:
  # Assuming the response contains a "choices" key with a list of completions
  completions = response.json()["choices"][0]["message"]["content"]
  print(f"OpenAI Response: {completions}")
else:
  print(f"Error: API request failed with status code {response.status_code}")