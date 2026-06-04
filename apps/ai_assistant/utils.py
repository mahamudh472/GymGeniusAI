import json
from openai import OpenAI
# from google.colab import userdata
import re
import base64
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')
from django.conf import settings


# Initialize OpenAI client only if API key is available
o = None
if settings.OPENAI_API_KEY:
    o = OpenAI(api_key=settings.OPENAI_API_KEY)

def robust_json_loads(text):
    """
    Safely load JSON from a string, handling potential markdown code blocks.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        import re
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        raise

def analyze_user_image(base64_image):
    """
    Analyzes a user's full-body image and returns a short,
    fitness-relevant description (posture, symmetry, muscle tone, etc.).
    """
    if not settings.OPENAI_API_KEY:
        return "Image analysis unavailable: OpenAI API key not configured."
    
    try:
        response = o.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional fitness assessment assistant. "
                        "Describe the person's physique only in factual, training-relevant terms. "
                        "Mention posture, symmetry, muscle tone, and any visible balance issues. "
                        "Avoid comments on attractiveness, race, or emotion. "
                        "Keep your output concise (1-3 lines). "
                        "Output MUST be a valid JSON object with exactly two keys: 'summary' and 'image_type'. "
                        "'image_type' should be one of ['back', 'side', 'front'] based on the image provided."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this full-body image for training-relevant observations only. Respond in JSON."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ]
        )
        
        raw_content = response.choices[0].message.content
        return robust_json_loads(raw_content)

    except Exception as e:
        return {
            "summary": "Image analysis unavailable due to service error.",
            "image_type": "unknown",
            "error": str(e)
        }
    
def analyze_single_meal(base64_image, meal_name="Meal"):
    """
    Analyze a single meal image for its nutritional profile and improvement tips.
    """
    
    if not settings.OPENAI_API_KEY:
        return {
            "meal_name": meal_name,
            "estimated_calories": 0,
            "macronutrients": {"protein_g": 0, "carbs_g": 0, "fat_g": 0},
            "micronutrients": {"vitamin_c_mg": 0, "iron_mg": 0, "calcium_mg": 0},
            "overall_health_insight": "Meal analysis unavailable: OpenAI API key not configured.",
            "improvement_suggestion": "Please configure OpenAI API key to enable meal analysis."
        }

    try:
        system_prompt = (
            "You are a certified AI nutritionist. "
            "Analyze the visible foods in the image and provide:\n"
            "- Estimated calories, protein, carbs, and fat.\n"
            "- Key micronutrients (vitamin C, calcium, iron, etc.).\n"
            "- A short health insight (2-3 sentences) summarizing overall meal quality.\n"
            "- A 2-line improvement suggestion (how to make it healthier or better balanced).\n"
            "**NOTE** DO NOT GIVE DIFFERENT DIFFERENT INFORMATION FOR SAME MEAL"
            "Return only valid JSON with this structure:\n\n"
            "{\n"
            "  'meal_name': 'string',\n"
            "  'estimated_calories': int,\n"
            "  'macronutrients': {'protein_g': ..., 'carbs_g': ..., 'fat_g': ...},\n"
            "  'micronutrients': {'vitamin_c_mg': ..., 'iron_mg': ..., 'calcium_mg': ...},\n"
            "  'overall_health_insight': 'string',\n"
            "  'improvement_suggestion': 'string'\n"
            "}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze this {meal_name.lower()} image."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]

        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=messages
        )

        return robust_json_loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "meal_name": meal_name,
            "estimated_calories": 0,
            "macronutrients": {"protein_g": 0, "carbs_g": 0, "fat_g": 0},
            "micronutrients": {"vitamin_c_mg": 0, "iron_mg": 0, "calcium_mg": 0},
            "overall_health_insight": "Meal analysis unavailable due to service error.",
            "improvement_suggestion": "Please try again later or contact support.",
            "error": str(e)
        }


def fitness_coach_ai(
    gender,
    age,
    weight_kg,
    height_cm,
    goal,
    activity_level,
    username,
    coach_name,
    current_query,
    image_summary=None,
    conversation_history=None
):
    """
    Main AI chat handler for FitCoach.
    Always returns a clean JSON object with plain-text keys:
      - reply
      - image_summary
    """
    try:
        chatbot_name = "FitCoach"
 
        system_message = {
            "role": "system",
            "content": f"""
You are "{chatbot_name}", an AI fitness coach that adopts one of four personas.
 
## Personas
- John — tough love, no excuses, best-results mindset.
- Selma — warm, supportive, emotionally smart.
- Jara — sassy, humorous, and hyper-motivating.
- Chris — professional, focused, efficient.
 
Active persona: {coach_name}
 
## User Profile
gender: {gender}
age: {age}
weight_kg: {weight_kg}
height_cm: {height_cm}
goal: {goal}
activity_level: {activity_level}
username: {username}
 
## Image Analysis Summary
{image_summary or "No image provided."}
 
## Behavior Guidelines
- Always speak as {coach_name}.
- Be conversational, motivational, and clear.
- Provide structured workout or nutrition guidance.
- DO NOT SUGGEST ANY WORKOUT ROUTINE
- You task is to guide the user to do exercise perfectly
- Use image_summary for posture/mobility cues.
- Use metric units (kg, cm, km).
- NEVER comment on attractiveness, race, or emotion.
- Respond ONLY in JSON format.
 
## JSON Response Format
{{
  "reply": "Main assistant message to the user",
  "image_summary": "Shortly analyze each portion of muscle from the image"
}}
 
Conversation history for context:
{conversation_history}
"""
        }
 
        user_message = {"role": "user", "content": current_query}
 
        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            messages=[system_message, user_message],
        )
 
        raw_output = response.choices[0].message.content.strip()
 
        # Try to parse JSON safely
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            parsed = {
                "reply": raw_output,
                "image_summary": image_summary or "N/A"
            }
 
        parsed.setdefault("reply", "I'm ready to help you get fitter!")
        parsed.setdefault("image_summary", image_summary or "N/A")
 
 
        def clean_text(text):
            if not isinstance(text, str):
                return text
 
            text = re.sub(r"\*\*|##|###|\*", "", text)  # remove markdown
            text = re.sub(r"\\u[0-9a-fA-F]{4}", "", text)  # remove unicode escapes
            text = re.sub(r"[\U0001F600-\U0001F64F]", "", text)  # remove emojis
            text = re.sub(r"[\U0001F300-\U0001F5FF]", "", text)
            text = re.sub(r"[\U0001F680-\U0001F6FF]", "", text)
            text = re.sub(r"[\U0001F1E0-\U0001F1FF]", "", text)
            text = re.sub(r"\s*\n\s*", " ", text)  # collapse newlines
            text = re.sub(r"\s{2,}", " ", text)  # remove multiple spaces
            return text.strip()
 
        parsed["reply"] = clean_text(parsed["reply"])
        parsed["image_summary"] = clean_text(parsed["image_summary"])
 
        return parsed
 
    except Exception as e:
        return {
            "reply": f"Error: {str(e)}",
            "image_summary": image_summary or "N/A"
        }

def get_target_calories(
    gender,
    age,
    weight_kg,
    height_cm,
    goal,
    activity_level,
    username,
    current_query=None,
    image_summary=None
):
    """
    Estimate the user's target daily calorie intake based on
    fitness goal, body composition, and activity level.
    Returns a clean JSON with only calorie target and rationale.
    """

    try:
        system_prompt = (
            "You are a certified fitness nutritionist. "
            "Your job is to calculate the user's estimated Monthly calorie target "
            "based on gender, age, height, weight, activity level, and fitness goal. "
            "If a body image summary is provided, consider it when adjusting the estimate. "
            "Base your reasoning roughly on TDEE (Total Daily Energy Expenditure) principles, "
            "with ±15% adjustment for goals like gaining or losing weight. "
            "Give **MONTHLY** Basis Calorie Target"
            "Output valid JSON only, in this format:\n\n"
            "{\n"
            "  'username': 'string',\n"
            "  'goal': 'string',\n"
            "  'target_calories_per_Month': int,\n"
            "}"
        )

        user_data = f"""
Username: {username}
Gender: {gender}
Age: {age}
Weight: {weight_kg} kg
Height: {height_cm} cm
Activity Level: {activity_level}
Goal: {goal}
Body Image Summary: {image_summary or "N/A"}
User Query: {current_query or "Calculate my daily calorie target."}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_data}
        ]

        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=messages
        )

        return robust_json_loads(response.choices[0].message.content)

    except Exception as e:
        return {"error": str(e)}


def update_daily_calorie_target(user, calorie_target):
    
    """
    Update the user's daily calorie target in their profile.
    """
    try:
        from django.utils import timezone
        user.daily_calorie_target = calorie_target
        user.calorie_target_updated_at = timezone.now().date()
        user.save(update_fields=['daily_calorie_target', 'calorie_target_updated_at'])
        return True
    except Exception as e:
        return False


# ==================== WORKOUT DATASET & PINECONE INTEGRATION ====================

try:
    import pandas as pd
    from tqdm import tqdm
    from pinecone import Pinecone, ServerlessSpec
    from langchain_openai import OpenAIEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# ==================== CONFIG ====================
INDEX_NAME = "workout-index"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


def get_pinecone_client():
    """Initialize and return Pinecone client."""
    if not PINECONE_AVAILABLE:
        raise ImportError("Pinecone dependencies not installed")
    
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    
    return Pinecone(api_key=pinecone_api_key)


def initialize_pinecone_index():
    """
    Initialize Pinecone index if it doesn't exist.
    Should be called manually when setting up the system.
    """
    if not PINECONE_AVAILABLE:
        return {"error": "Pinecone dependencies not installed"}
    
    try:
        pc = get_pinecone_client()
        
        if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
            pc.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIM,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            return {"status": "created", "index": INDEX_NAME}
        else:
            return {"status": "exists", "index": INDEX_NAME}
    except Exception as e:
        return {"error": str(e)}


def combine_row(row):
    """Combine all columns of a DataFrame row into a single text string."""
    return " | ".join([f"{col}: {row[col]}" for col in row.index if row[col]])


def upload_workout_dataset_to_pinecone(csv_path=None):
    """
    Load workout dataset from CSV and upload to Pinecone.
    
    Args:
        csv_path: Path to the CSV file. If None, uses default project path.
    
    Returns:
        dict with status and count of uploaded chunks
    """
    if not PINECONE_AVAILABLE:
        return {"error": "Pinecone dependencies not installed"}
    
    try:
        # Use project root path if not specified
        if csv_path is None:
            csv_path = os.path.join(settings.BASE_DIR, "gym_workouts_full.csv")
        
        if not os.path.exists(csv_path):
            return {"error": f"CSV file not found at: {csv_path}"}
        
        # Load dataset
        df = pd.read_csv(csv_path)
        df = df.fillna("").astype(str)
        
        # Combine columns into text
        df["combined_text"] = df.apply(combine_row, axis=1)
        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100,
            separators=["\n", ".", "!", "?", ";", ",", " "]
        )
        
        texts = []
        metadata = []
        
        for idx, row in df.iterrows():
            chunks = splitter.split_text(row["combined_text"])
            for chunk in chunks:
                texts.append(chunk)
                metadata.append({"row_index": int(idx)})
        
        # Initialize embeddings and vectorstore
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings
        )
        
        # Upload to Pinecone
        ids = [f"workout-{i}" for i in range(len(texts))]
        vectorstore.add_texts(texts=texts, metadatas=metadata, ids=ids)
        
        return {
            "status": "success",
            "rows_processed": len(df),
            "chunks_uploaded": len(texts)
        }
        
    except Exception as e:
        return {"error": str(e)}

def retrieve_workout_info(query, top_k=20):
    """
    Retrieve relevant workout information from Pinecone based on a query.
    
    Args:
        query: Search query string
        top_k: Number of results to return
    
    Returns:
        List of document results with content and metadata
    """
    if not PINECONE_AVAILABLE:
        return []
    
    try:
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings
        )

        results = vectorstore.similarity_search(query, k=top_k)
        
        return results
    except Exception as e:
        return []

def generate_dataset_based_workout(
    gender,
    age,
    weight_kg,
    height_cm,
    goal,
    activity_level,
    username,
    image_summary=None,
    workout_logs=None,
    top_k=7
):
    """
    Generate a personalized workout plan based on:
    - User profile
    - Retrieved dataset workouts from Pinecone
    - User's last 7 days workout logs (if provided)

    Exercises MUST come ONLY from dataset.
    Each exercise must include 'muscle_group'.
    
    Args:
        gender: User's gender
        age: User's age
        weight_kg: User's weight in kg
        height_cm: User's height in cm
        goal: Fitness goal (e.g., 'gain_weight', 'lose_weight', 'maintain')
        activity_level: Activity level (e.g., 'beginner', 'intermediate', 'advanced')
        username: User's name
        image_summary: Optional body image analysis summary
        workout_logs: Optional list of past workout logs (last 7 days)
        top_k: Number of similar workouts to retrieve from dataset
    
    Returns:
        dict: Workout plan with exercises or error message
    """
    if not settings.OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured"}
    
    if not PINECONE_AVAILABLE:
        return {"error": "Pinecone dependencies not installed"}

    try:
        # ========== 1️⃣ Retrieve Relevant Workouts ==========
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings
        )

        query = f"Workout plan for {goal}, activity level: {activity_level}, gender: {gender}"
        retrieved_docs = vectorstore.similarity_search(query, k=top_k)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # ========== 2️⃣ Include past workout logs ==========
        workout_history_text = (
            json.dumps(workout_logs, indent=2)
            if workout_logs
            else "No previous logs available."
        )

        # ========== 3️⃣ System Prompt WITH MUSCLE GROUP REQUIREMENT ==========
        system_prompt = (
            "You are a certified strength and conditioning coach.\n"
            "Use ONLY exercises from the 'Dataset Context'.\n"
            "Do NOT invent new exercises.\n"
            "Extract 'muscle_group' from the dataset context for each exercise.\n"
            "Never guess muscle groups — only use text from dataset.\n"
            "If multiple muscle groups appear in dataset row, choose primary.\n\n"

            "Workout Rules:\n"
            "- Must include at least 5 exercises\n"
            "- No duplicate exercises\n"
            "- Apply progressive overload using past 7-day logs\n"
            "- Match goal and activity level\n\n"

            "OUTPUT MUST BE STRICTLY VALID JSON:\n"
            "[\n"
            "  {\n"
            "    'workout_name': 'string',\n"
            "    'description': 'string',\n"
            "    'difficulty': 'Beginner' | 'Intermediate' | 'Advanced',\n"
            "    'estimated_duration': int,\n"
            "    'estimated_calories': int,\n"
            "    'exercises': [\n"
            "      {\n"
            "        'name': 'string',\n"
            "        'muscle_group': 'string',\n"
            "        'sets': int,\n"
            "        'reps': int,\n"
            "        'duration_seconds': int,\n"
            "        'rest_time': int,\n"
            "        'notes': 'string'\n"
            "      }\n"
            "    ]\n"
            "  }\n"
            "]"
        )

        # ========== 4️⃣ User + Dataset Context ==========
        user_profile = f"""
Username: {username}
Gender: {gender}
Age: {age}
Weight: {weight_kg} kg
Height: {height_cm} cm
Goal: {goal}
Activity Level: {activity_level}
Body Image Summary: {image_summary or "N/A"}

Previous 7 Days Workout Logs:
{workout_history_text}

Dataset Context (workouts retrieved from your indexed dataset):
{context}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_profile}
        ]

        # ========== 5️⃣ GPT Generates the Dataset-Based Plan ==========
        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=messages
        )

        return robust_json_loads(response.choices[0].message.content)

    except Exception as e:
        return {"error": str(e)}



def generate_multi_level_workouts(
    gender,
    age,
    weight_kg,
    height_cm,
    goal,
    activity_level,
    username,
    image_summary=None,
    top_k=15
):
    """
    GUARANTEED: Beginner + Intermediate + Advanced workouts.
    Method:
      - 3 separate RAG retrievals
      - 3 separate LLM calls (one per level)
      - Final combined JSON list
    """
 
    def fetch_context(level_query):
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings
        )
 
        docs = vectorstore.similarity_search(level_query, k=top_k)
        return "\n\n".join([doc.page_content for doc in docs])
 
 
    def build_level_prompt(level, context):
        return f"""
You are a certified strength and conditioning coach.
 
You must create a workout ONLY using exercises found in the dataset context below.
 
DATASET CONTEXT:
{context}
 
RULES:
- Output ONLY valid JSON.
- You MUST provide EXACTLY 4 exercises.
- Each exercise MUST include: name, muscle_group, sets, reps, duration_seconds, rest_time, notes.
- Use ONLY muscle_group names that appear in the dataset text.
- No invented exercises.
- No hallucinated muscle groups.
- Keep difficulty strictly: {level}.
- Match user goal: {goal}.
- Respond in EXACT JSON format.
 
JSON FORMAT:
{{
  "workout_name": "string",
  "description": "string",
  "difficulty": "{level}",
  "estimated_duration": 45,
  "estimated_calories": 300,
  "exercises": [
    {{
      "name": "string",
      "muscle_group": "string",
      "sets": 0,
      "reps": 0,
      "duration_seconds": 0,
      "rest_time": 0,
      "notes": "string"
    }}
  ]
}}
        """
 
 
    user_profile = f"""
User:
Username: {username}
Gender: {gender}
Age: {age}
Weight: {weight_kg} kg
Height: {height_cm} cm
Goal: {goal}
Activity Level: {activity_level}
Image Summary: {image_summary or "N/A"}
"""
 
    def generate_level(level_name):
        query = f"{level_name} level workout for {goal}, gender: {gender}"
        context = fetch_context(query)
 
        messages = [
            {"role": "system", "content": build_level_prompt(level_name, context)},
            {"role": "user", "content": user_profile}
        ]
 
        response = o.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=messages
        )
 
        return robust_json_loads(response.choices[0].message.content)
 
 
    beginner = generate_level("Beginner")
    intermediate = generate_level("Intermediate")
    advanced = generate_level("Advanced")
 
    return {
        "workout_levels": [
            beginner,
            intermediate,
            advanced
        ]
    }
