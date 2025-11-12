"""
Test script for Workout Progress Tracking API

This script demonstrates how to use the workout progress tracking endpoint.
You'll need to replace the token and IDs with actual values from your system.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "your_auth_token_here"  # Replace with actual token

# Headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_mark_exercise_complete():
    """Test marking an exercise as completed"""
    url = f"{BASE_URL}/api/workouts/track-progress/"
    
    # Example 1: Simple completion without extra details
    data = {
        "user_workout_id": 1,
        "user_exercise_id": 5
    }
    
    print("Testing: Mark exercise as completed (simple)")
    print(f"Request: POST {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 80)
    
    # Example 2: Completion with detailed tracking
    data_detailed = {
        "user_workout_id": 1,
        "user_exercise_id": 6,
        "actual_sets": 3,
        "actual_reps": 12,
        "actual_duration": 180,
        "notes": "Felt strong today, increased weight by 5kg"
    }
    
    print("\nTesting: Mark exercise as completed (with details)")
    print(f"Request: POST {url}")
    print(f"Data: {json.dumps(data_detailed, indent=2)}")
    
    response = requests.post(url, headers=headers, json=data_detailed)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 80)

def test_get_progress():
    """Test getting current workout progress"""
    workout_id = 1
    url = f"{BASE_URL}/api/workouts/track-progress/?user_workout_id={workout_id}"
    
    print("\nTesting: Get current workout progress")
    print(f"Request: GET {url}")
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 80)

def test_complete_all_exercises():
    """Test completing all exercises to trigger Activity creation"""
    url = f"{BASE_URL}/api/workouts/track-progress/"
    
    # Assume workout has exercises with IDs 5, 6, 7, 8, 9
    exercise_ids = [5, 6, 7, 8, 9]
    
    print("\nTesting: Complete all exercises to create Activity")
    
    for exercise_id in exercise_ids:
        data = {
            "user_workout_id": 1,
            "user_exercise_id": exercise_id
        }
        
        print(f"\nMarking exercise {exercise_id} as complete...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Progress: {result['completion_percentage']}%")
            print(f"  Completed: {result['completed_exercises']}/{result['total_exercises']}")
            
            if result['all_completed']:
                print("\n✓ ALL EXERCISES COMPLETED!")
                print(f"  Activity Created: {result['activity_created']}")
                if result['activity']:
                    print(f"  Activity Details:")
                    print(f"    - Name: {result['activity']['name']}")
                    print(f"    - Duration: {result['activity']['duration']} minutes")
                    print(f"    - Calories: {result['activity']['calories']} kcal")
        else:
            print(f"  Error: {response.status_code}")
            print(f"  Response: {response.json()}")
    
    print("-" * 80)

if __name__ == "__main__":
    print("=" * 80)
    print("WORKOUT PROGRESS TRACKING API TEST")
    print("=" * 80)
    
    # Uncomment the tests you want to run:
    
    # test_get_progress()
    # test_mark_exercise_complete()
    # test_complete_all_exercises()
    
    print("\n" + "=" * 80)
    print("Note: Update TOKEN and IDs with actual values before running!")
    print("=" * 80)
