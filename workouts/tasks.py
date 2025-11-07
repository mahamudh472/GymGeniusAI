# # tasks.py
# from celery import shared_task
# import requests
# from .utils import save_generated_workouts

# @shared_task
# def fetch_external_api(goal, duration_minutes, difficulty, user_id=None):
#     print("Fetching data from external API...")
#     save_generated_workouts(goal, duration_minutes, difficulty, user=user_id)
#     print("Fetched data from external API")
#     return "done"
