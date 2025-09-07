"""
Mock Data Generation for Nutritional Notifications AI Agent
Creates realistic synthetic data for testing the system
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import random

def create_users_data():
    """Create mock user profiles"""
    users = []
    conditions_pool = [
        "Glowing skin", "Hair fall", "Gut health", "Muscle pain", 
        "Nail issues", "Energy boost", "Weight management", "Immunity"
    ]
    
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune"]
    
    for i in range(1, 21):  # 20 users
        user = {
            "user_id": f"u{i:03d}",
            "diet_pref": random.choice(["veg", "nonveg", "egg"]),
            "allergies": random.sample(["nuts", "dairy", "gluten", "shellfish"], 
                                     random.randint(0, 2)),
            "age": random.randint(22, 65),
            "gender": random.choice(["M", "F", "Other"]),
            "city": random.choice(cities),
            "tz": "Asia/Kolkata",
            "usual_meal_times": {
                "breakfast": f"{random.randint(7,9):02d}:{random.choice(['00','30'])}",
                "lunch": f"{random.randint(12,14):02d}:{random.choice(['00','30'])}",
                "dinner": f"{random.randint(19,21):02d}:{random.choice(['00','30'])}"
            },
            "conditions": random.sample(conditions_pool, random.randint(2, 4))
        }
        users.append(user)
    
    return users

def create_condition_nutrient_mapping():
    """Create condition to nutrient mappings"""
    mappings = [
        # Glowing skin
        {"condition": "Glowing skin", "nutrient": "vitamin_e", "weight": 0.9, "references": "PMID:12345"},
        {"condition": "Glowing skin", "nutrient": "zinc", "weight": 0.8, "references": "PMID:12346"},
        {"condition": "Glowing skin", "nutrient": "vitamin_c", "weight": 0.7, "references": "PMID:12347"},
        {"condition": "Glowing skin", "nutrient": "omega3", "weight": 0.6, "references": ""},
        
        # Hair fall
        {"condition": "Hair fall", "nutrient": "biotin", "weight": 0.9, "references": "PMID:23456"},
        {"condition": "Hair fall", "nutrient": "iron", "weight": 0.8, "references": "PMID:23457"},
        {"condition": "Hair fall", "nutrient": "protein", "weight": 0.7, "references": "PMID:23458"},
        {"condition": "Hair fall", "nutrient": "zinc", "weight": 0.6, "references": ""},
        
        # Gut health
        {"condition": "Gut health", "nutrient": "fiber", "weight": 0.9, "references": "PMID:34567"},
        {"condition": "Gut health", "nutrient": "probiotics", "weight": 0.8, "references": "PMID:34568"},
        {"condition": "Gut health", "nutrient": "prebiotics", "weight": 0.7, "references": "PMID:34569"},
        
        # Muscle pain
        {"condition": "Muscle pain", "nutrient": "magnesium", "weight": 0.9, "references": "PMID:45678"},
        {"condition": "Muscle pain", "nutrient": "protein", "weight": 0.8, "references": "PMID:45679"},
        {"condition": "Muscle pain", "nutrient": "omega3", "weight": 0.7, "references": ""},
        
        # Energy boost
        {"condition": "Energy boost", "nutrient": "iron", "weight": 0.9, "references": "PMID:56789"},
        {"condition": "Energy boost", "nutrient": "vitamin_b12", "weight": 0.8, "references": "PMID:56790"},
        {"condition": "Energy boost", "nutrient": "complex_carbs", "weight": 0.7, "references": ""},
        
        # Immunity
        {"condition": "Immunity", "nutrient": "vitamin_c", "weight": 0.9, "references": "PMID:67890"},
        {"condition": "Immunity", "nutrient": "zinc", "weight": 0.8, "references": "PMID:67891"},
        {"condition": "Immunity", "nutrient": "vitamin_d", "weight": 0.7, "references": ""},
    ]
    
    return mappings

def create_foods_data():
    """Create mock food database"""
    foods = [
        {
            "food_id": "f001", "name": "Soaked Almonds", "is_veg": True,
            "ingredients": ["almonds"], "tags": ["nuts", "protein"],
            "nutrients": {"protein": 6.0, "vitamin_e": 7.3, "zinc": 0.9, "fiber": 3.5}
        },
        {
            "food_id": "f002", "name": "Greek Yogurt", "is_veg": True,
            "ingredients": ["milk", "yogurt cultures"], "tags": ["dairy", "probiotic"],
            "nutrients": {"protein": 10.0, "probiotics": 1.0, "calcium": 120}
        },
        {
            "food_id": "f003", "name": "Spinach Salad", "is_veg": True,
            "ingredients": ["spinach", "tomatoes"], "tags": ["leafy_greens"],
            "nutrients": {"iron": 2.7, "vitamin_c": 28.1, "fiber": 2.2, "folate": 58.2}
        },
        {
            "food_id": "f004", "name": "Grilled Chicken Breast", "is_veg": False,
            "ingredients": ["chicken breast"], "tags": ["lean_protein"],
            "nutrients": {"protein": 31.0, "vitamin_b12": 0.3, "iron": 1.0}
        },
        {
            "food_id": "f005", "name": "Quinoa Bowl", "is_veg": True,
            "ingredients": ["quinoa", "vegetables"], "tags": ["whole_grain", "complete_protein"],
            "nutrients": {"protein": 8.1, "fiber": 5.2, "iron": 2.8, "magnesium": 118}
        },
        {
            "food_id": "f006", "name": "Banana", "is_veg": True,
            "ingredients": ["banana"], "tags": ["fruit"],
            "nutrients": {"potassium": 358, "vitamin_b6": 0.4, "complex_carbs": 22.8}
        },
        {
            "food_id": "f007", "name": "Salmon Fillet", "is_veg": False,
            "ingredients": ["salmon"], "tags": ["fish", "omega3"],
            "nutrients": {"protein": 25.4, "omega3": 1.8, "vitamin_d": 11.0}
        },
        {
            "food_id": "f008", "name": "Avocado", "is_veg": True,
            "ingredients": ["avocado"], "tags": ["healthy_fats"],
            "nutrients": {"fiber": 10.0, "vitamin_e": 2.1, "potassium": 485}
        },
        {
            "food_id": "f009", "name": "Lentil Dal", "is_veg": True,
            "ingredients": ["lentils", "spices"], "tags": ["legumes", "protein"],
            "nutrients": {"protein": 9.0, "iron": 3.3, "fiber": 8.0, "folate": 180}
        },
        {
            "food_id": "f010", "name": "Eggs", "is_veg": False,
            "ingredients": ["eggs"], "tags": ["complete_protein"],
            "nutrients": {"protein": 13.0, "biotin": 10.0, "vitamin_b12": 0.9, "choline": 147}
        },
        {
            "food_id": "f011", "name": "Sweet Potato", "is_veg": True,
            "ingredients": ["sweet potato"], "tags": ["root_vegetable"],
            "nutrients": {"vitamin_a": 14187, "fiber": 3.8, "complex_carbs": 20.1, "potassium": 337}
        },
        {
            "food_id": "f012", "name": "Walnuts", "is_veg": True,
            "ingredients": ["walnuts"], "tags": ["nuts", "omega3"],
            "nutrients": {"omega3": 2.5, "protein": 4.3, "vitamin_e": 0.7, "magnesium": 45}
        }
    ]
    
    return foods

def create_activity_logs():
    """Create mock user activity logs"""
    activities = []
    base_date = datetime.now() - timedelta(days=7)
    
    user_ids = [f"u{i:03d}" for i in range(1, 21)]
    food_ids = [f"f{i:03d}" for i in range(1, 13)]
    
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        
        for user_id in random.sample(user_ids, random.randint(10, 15)):
            # Food consumption events
            for meal in random.sample(["breakfast", "lunch", "dinner"], random.randint(1, 3)):
                activities.append({
                    "user_id": user_id,
                    "ts": (current_date + timedelta(hours=random.randint(0, 23))).isoformat(),
                    "event": random.choice(["consumed", "skipped"]),
                    "food_id": random.choice(food_ids),
                    "duration_min": None
                })
            
            # Workout events
            if random.random() < 0.4:  # 40% chance of workout per day
                activities.append({
                    "user_id": user_id,
                    "ts": (current_date + timedelta(hours=random.randint(6, 20))).isoformat(),
                    "event": "worked_out",
                    "food_id": None,
                    "duration_min": random.randint(30, 90)
                })
    
    return activities

def create_message_templates():
    """Create message templates"""
    templates = [
        {
            "template_id": "pre_meal_basic",
            "text": "{food} now for {benefit} → supports {condition}. Try {cta}",
            "style": "friendly",
            "lang": "en"
        },
        {
            "template_id": "post_workout",
            "text": "Post-workout fuel: {food} provides {benefit} for {condition}. {cta} 💪",
            "style": "punchy",
            "lang": "en"
        },
        {
            "template_id": "science_fact",
            "text": "{why_now} — {food} delivers {benefit} for {condition}. {cta}",
            "style": "sciencey",
            "lang": "en"
        },
        {
            "template_id": "condition_reminder",
            "text": "Haven't focused on {condition} lately? {food} provides {benefit}. {cta}",
            "style": "gentle",
            "lang": "en"
        }
    ]
    
    return templates

def create_fact_database():
    """Create why_now facts database"""
    facts = {
        "morning_boost": "Skin cell turnover peaks overnight — support with antioxidants",
        "pre_meal": "Pre-meal protein moderates glycemic response by 23%",
        "post_activity": "Glycogen resynthesis is highest within 2 hours post-workout",
        "evening_repair": "Evening nutrition supports overnight muscle repair",
        "gut_timing": "Probiotic absorption peaks during active digestion",
        "iron_absorption": "Vitamin C increases iron absorption by up to 3x",
        "magnesium_timing": "Magnesium helps muscle relaxation and recovery",
        "omega3_benefits": "Omega-3s reduce inflammation markers within hours"
    }
    
    return facts

def save_all_data():
    """Save all mock data to files"""
    
    # Create data directory structure
    import os
    os.makedirs("data", exist_ok=True)
    
    # Users
    users = create_users_data()
    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    # Condition-Nutrient mapping
    mappings = create_condition_nutrient_mapping()
    pd.DataFrame(mappings).to_csv("data/condition_nutrients.csv", index=False)
    
    # Foods
    foods = create_foods_data()
    with open("data/foods.json", "w") as f:
        json.dump(foods, f, indent=2)
    
    # Activity logs
    activities = create_activity_logs()
    pd.DataFrame(activities).to_csv("data/user_activity.csv", index=False)
    
    # Message templates
    templates = create_message_templates()
    with open("data/message_templates.json", "w") as f:
        json.dump(templates, f, indent=2)
    
    # Facts database
    facts = create_fact_database()
    with open("data/facts.json", "w") as f:
        json.dump(facts, f, indent=2)
    
    print("✅ Mock data created successfully!")
    print("📁 Files created:")
    print("   - data/users.json")
    print("   - data/condition_nutrients.csv") 
    print("   - data/foods.json")
    print("   - data/user_activity.csv")
    print("   - data/message_templates.json")
    print("   - data/facts.json")

if __name__ == "__main__":
    save_all_data()