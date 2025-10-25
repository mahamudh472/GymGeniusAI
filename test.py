import requests
from dotenv import load_dotenv
import os

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
model = "google/gemini-2.0-flash-exp:free"

def get_ai_response(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"
def generate_workout_plan(goal, duration_minutes, difficulty):
    prompt = (f"Generate a {duration_minutes}-minute workout plan for a {difficulty} level user "
              f"with the goal of {goal}. Provide exercises, sets, reps, and rest times.")
    return get_ai_response(prompt)

print(generate_workout_plan("build muscle", 45, "intermediate"))