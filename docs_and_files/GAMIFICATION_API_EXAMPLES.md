# Gamification API Examples

This document provides real API request/response examples for the gamification system.

## Authentication
All endpoints require authentication. Include JWT token in headers:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Get Current User's Rank

**Request:**
```http
GET /api/gamification/user-ranks/me/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "current_rank": {
      "id": 1,
      "name": "BRONZE",
      "name_display": "Bronze",
      "level": 1,
      "promotion_threshold": 30.0,
      "demotion_threshold": 0.0,
      "min_points_required": 0,
      "icon": "🥉",
      "color_code": "#CD7F32"
    },
    "total_points": 350,
    "weekly_points": 120,
    "highest_rank_achieved": {
      "id": 2,
      "name": "SILVER",
      "name_display": "Silver",
      "level": 2
    },
    "rank_updated_at": "2025-11-20T10:30:00Z",
    "created_at": "2025-10-01T08:00:00Z"
  }
}
```

---

## 2. Get Leaderboard (Same Rank Only)

**Request:**
```http
GET /api/gamification/leaderboard/?limit=50
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "rank": "Bronze",
    "rank_level": 1,
    "rank_color": "#CD7F32",
    "user_position": 15,
    "total_users_in_rank": 234,
    "week_start": "2025-11-18",
    "leaderboard": [
      {
        "position": 1,
        "user_id": 42,
        "username": "fitness_pro",
        "weekly_points": 450,
        "total_points": 1200,
        "is_current_user": false
      },
      {
        "position": 2,
        "user_id": 87,
        "username": "gym_warrior",
        "weekly_points": 380,
        "total_points": 980,
        "is_current_user": false
      },
      {
        "position": 15,
        "user_id": 23,
        "username": "john_doe",
        "weekly_points": 120,
        "total_points": 350,
        "is_current_user": true
      }
    ]
  }
}
```

---

## 3. Get User Statistics

**Request:**
```http
GET /api/gamification/stats/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 23,
      "username": "john_doe"
    },
    "rank": {
      "name": "Bronze",
      "level": 1,
      "color": "#CD7F32",
      "icon": "🥉"
    },
    "points": {
      "total": 350,
      "weekly": 120
    },
    "position": {
      "in_rank": 15,
      "total_in_rank": 234,
      "percentile": 93.59
    },
    "streak": {
      "current": 7,
      "longest": 14,
      "total_checkins": 45,
      "last_checkin": "2025-11-21"
    },
    "highest_rank": {
      "name": "Silver",
      "level": 2
    },
    "recent_transactions": [
      {
        "id": 156,
        "points": 50,
        "description": "Complete Workout",
        "activity": "Complete Workout",
        "created_at": "2025-11-21T09:30:00Z"
      },
      {
        "id": 155,
        "points": 15,
        "description": "Log Meal",
        "activity": "Log Meal",
        "created_at": "2025-11-21T08:15:00Z"
      }
    ],
    "rank_history": [
      {
        "old_rank": "Silver",
        "new_rank": "Bronze",
        "reason": "Demoted (Bottom 20%)",
        "changed_at": "2025-11-18T00:00:00Z"
      }
    ]
  }
}
```

---

## 4. Daily Check-in

**Request:**
```http
POST /api/gamification/checkin/
Authorization: Bearer <token>
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Checked in! Current streak: 8 days. Earned 10 points!",
  "points_awarded": 10,
  "current_streak": 8,
  "total_check_ins": 46
}
```

**Response (Already Checked In):**
```json
{
  "success": false,
  "message": "Already checked in today",
  "points_awarded": 0,
  "current_streak": 8,
  "total_check_ins": 46
}
```

**Response (Streak Milestone - 7 days):**
```json
{
  "success": true,
  "message": "Checked in! Current streak: 7 days. Earned 60 points!",
  "points_awarded": 60,
  "current_streak": 7,
  "total_check_ins": 40
}
```

---

## 5. Award Points for Activity

**Request:**
```http
POST /api/gamification/award-points/
Authorization: Bearer <token>
Content-Type: application/json

{
  "activity_code": "COMPLETE_WORKOUT",
  "metadata": {
    "workout_id": 123,
    "duration": 45,
    "exercises": 8
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Awarded 50 points for Complete Workout",
  "points_awarded": 50
}
```

**Response (Daily Limit Reached):**
```json
{
  "success": false,
  "message": "Daily limit reached for Complete Workout",
  "points_awarded": 0
}
```

**Request (Custom Points):**
```http
POST /api/gamification/award-points/
Authorization: Bearer <token>
Content-Type: application/json

{
  "activity_code": "SPECIAL_EVENT",
  "custom_points": 200,
  "metadata": {
    "event": "Monthly Challenge Winner"
  }
}
```

---

## 6. Get All Ranks

**Request:**
```http
GET /api/gamification/ranks/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "Bronze",
      "level": 1,
      "color": "#CD7F32",
      "icon": "🥉",
      "promotion_threshold": 30.0,
      "demotion_threshold": 0.0,
      "min_points_required": 0
    },
    {
      "name": "Silver",
      "level": 2,
      "color": "#C0C0C0",
      "icon": "🥈",
      "promotion_threshold": 25.0,
      "demotion_threshold": 20.0,
      "min_points_required": 100
    },
    {
      "name": "Gold",
      "level": 3,
      "color": "#FFD700",
      "icon": "🥇",
      "promotion_threshold": 20.0,
      "demotion_threshold": 20.0,
      "min_points_required": 500
    }
  ]
}
```

---

## 7. Get All Activities

**Request:**
```http
GET /api/gamification/activities/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "code": "DAILY_CHECKIN",
      "name": "Daily Check-in",
      "points": 10,
      "description": "Log in to the app daily",
      "max_per_day": 1
    },
    {
      "code": "COMPLETE_WORKOUT",
      "name": "Complete Workout",
      "points": 50,
      "description": "Complete a workout session",
      "max_per_day": 3
    },
    {
      "code": "LOG_MEAL",
      "name": "Log Meal",
      "points": 15,
      "description": "Log a meal with nutrition info",
      "max_per_day": 5
    }
  ]
}
```

---

## 8. Get Point Transactions

**Request:**
```http
GET /api/gamification/transactions/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 156,
  "next": "/api/gamification/transactions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 456,
      "username": "john_doe",
      "activity_type": 3,
      "activity_name": "Complete Workout",
      "points": 50,
      "description": "Complete Workout",
      "metadata": {
        "workout_id": 123,
        "duration": 45
      },
      "created_at": "2025-11-21T09:30:00Z",
      "week_start": "2025-11-18"
    },
    {
      "id": 455,
      "username": "john_doe",
      "activity_type": 1,
      "activity_name": "Daily Check-in",
      "points": 10,
      "description": "Daily Check-in",
      "metadata": {
        "streak": 8
      },
      "created_at": "2025-11-21T07:00:00Z",
      "week_start": "2025-11-18"
    }
  ]
}
```

---

## 9. Get Streak Information

**Request:**
```http
GET /api/gamification/streak/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "current_streak": 8,
    "longest_streak": 21,
    "last_check_in": "2025-11-21",
    "total_check_ins": 67
  }
}
```

---

## 10. Get Rank History

**Request:**
```http
GET /api/gamification/rank-history/?limit=10
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 12,
      "username": "john_doe",
      "old_rank_name": "Silver",
      "new_rank_name": "Bronze",
      "reason": "Demoted (Bottom 20%)",
      "weekly_points": 45,
      "position_in_old_rank": 89,
      "changed_at": "2025-11-18T00:00:00Z",
      "week_start": "2025-11-11"
    },
    {
      "id": 8,
      "username": "john_doe",
      "old_rank_name": "Bronze",
      "new_rank_name": "Silver",
      "reason": "Promoted (Top 30%)",
      "weekly_points": 320,
      "position_in_old_rank": 15,
      "changed_at": "2025-11-11T00:00:00Z",
      "week_start": "2025-11-04"
    }
  ]
}
```

---

## 11. Get Weekly Leaderboard History

**Request:**
```http
GET /api/gamification/leaderboard/history/?limit=5
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 234,
      "username": "john_doe",
      "rank_name": "Bronze",
      "rank_color": "#CD7F32",
      "week_start": "2025-11-18",
      "week_end": "2025-11-24",
      "position": 15,
      "position_in_rank": 15,
      "total_users_in_rank": 234,
      "weekly_points": 120,
      "total_points": 350,
      "rank_changed": false,
      "old_rank_name": null,
      "created_at": "2025-11-18T00:05:00Z"
    },
    {
      "id": 198,
      "username": "john_doe",
      "rank_name": "Bronze",
      "rank_color": "#CD7F32",
      "week_start": "2025-11-11",
      "week_end": "2025-11-17",
      "position": 89,
      "position_in_rank": 89,
      "total_users_in_rank": 245,
      "weekly_points": 45,
      "total_points": 230,
      "rank_changed": true,
      "old_rank_name": "Silver",
      "created_at": "2025-11-11T00:05:00Z"
    }
  ]
}
```

---

## Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**400 Bad Request:**
```json
{
  "activity_code": [
    "This field is required."
  ]
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

---

## Integration Code Examples

### JavaScript/Fetch
```javascript
// Daily check-in
async function dailyCheckIn() {
  const response = await fetch('/api/gamification/checkin/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const data = await response.json();
  console.log(`Earned ${data.points_awarded} points!`);
}

// Get leaderboard
async function getLeaderboard() {
  const response = await fetch('/api/gamification/leaderboard/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data.data;
}

// Award points
async function awardWorkoutPoints(workoutId) {
  const response = await fetch('/api/gamification/award-points/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      activity_code: 'COMPLETE_WORKOUT',
      metadata: { workout_id: workoutId }
    })
  });
  const data = await response.json();
  return data;
}
```

### Python/Requests
```python
import requests

headers = {'Authorization': f'Bearer {token}'}

# Get user stats
response = requests.get('http://localhost:8000/api/gamification/stats/', headers=headers)
stats = response.json()

# Daily check-in
response = requests.post('http://localhost:8000/api/gamification/checkin/', headers=headers)
checkin_data = response.json()

# Award points
response = requests.post(
    'http://localhost:8000/api/gamification/award-points/',
    headers=headers,
    json={
        'activity_code': 'COMPLETE_WORKOUT',
        'metadata': {'workout_id': 123}
    }
)
```

---

## Rate Limiting & Best Practices

1. **Caching**: Cache rank and activity lists as they rarely change
2. **Pagination**: Use pagination for transaction history
3. **Batch Operations**: Award multiple points in backend, not via API
4. **Optimize Queries**: Leaderboard queries are already optimized with indexes
5. **Error Handling**: Always handle daily limit errors gracefully
6. **User Experience**: Show real-time point updates with WebSockets/polling
