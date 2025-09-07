"""
FastAPI service for Nutritional Notifications AI Agent
Provides RESTful endpoints for notification generation
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pytz
import json
from nutrition_agent import NutritionAgent, NutritionAgentEvaluator

# Initialize FastAPI app
app = FastAPI(
    title="Nutritional Notifications AI Agent",
    description="AI-powered personalized nutritional notifications service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the nutrition agent
nutrition_agent = NutritionAgent()

# Pydantic models for API
class GenerateNotificationRequest(BaseModel):
    user_id: str = Field(..., description="User ID to generate notifications for")
    trigger: Optional[str] = Field(None, description="Specific trigger to test (optional)")
    now: Optional[str] = Field(None, description="Current timestamp in ISO format (optional)")

class UserProfile(BaseModel):
    user_id: str
    diet_pref: str
    allergies: List[str]
    age: int
    gender: str
    city: str
    tz: str
    usual_meal_times: Dict[str, str]
    conditions: List[str]

class FoodItem(BaseModel):
    food_id: str
    name: str
    is_veg: bool
    ingredients: List[str]
    tags: List[str]
    nutrients: Dict[str, float]

class EvaluationResults(BaseModel):
    eligibility_rate: float
    safety_violations: int
    total_notifications: int
    diversity_unique_foods: int
    diversity_ratio: float
    avg_score: float
    avg_message_length: float
    messages_under_160_chars: float

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Nutritional Notifications AI Agent API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users_loaded": len(nutrition_agent.users),
        "foods_loaded": len(nutrition_agent.foods),
        "templates_loaded": len(nutrition_agent.message_templates)
    }

@app.post("/generate")
async def generate_notifications(request: GenerateNotificationRequest):
    """
    Generate personalized nutritional notifications for a user
    """
    try:
        # Validate user exists
        if request.user_id not in nutrition_agent.users:
            raise HTTPException(
                status_code=404, 
                detail=f"User {request.user_id} not found"
            )
        
        # Parse timestamp if provided
        now = datetime.now(pytz.UTC)
        if request.now:
            try:
                now = datetime.fromisoformat(request.now.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid timestamp format. Use ISO format like '2023-09-03T17:30:00+05:30'"
                )
        
        # Generate notifications
        notifications = nutrition_agent.generate_notifications(request.user_id, now)
        
        # If specific trigger requested, filter results
        if request.trigger:
            notifications = [n for n in notifications if n['trigger'] == request.trigger]
        
        return {
            "success": True,
            "user_id": request.user_id,
            "generated_at": now.isoformat(),
            "notifications_count": len(notifications),
            "notifications": notifications
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/users")
async def get_users() -> List[str]:
    """Get list of all user IDs"""
    return list(nutrition_agent.users.keys())

@app.get("/users/{user_id}")
async def get_user_profile(user_id: str) -> UserProfile:
    """Get detailed profile for a specific user"""
    if user_id not in nutrition_agent.users:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    user = nutrition_agent.users[user_id]
    return UserProfile(
        user_id=user.user_id,
        diet_pref=user.diet_pref,
        allergies=user.allergies,
        age=user.age,
        gender=user.gender,
        city=user.city,
        tz=user.tz,
        usual_meal_times=user.usual_meal_times,
        conditions=user.conditions
    )

@app.get("/foods")
async def get_foods(
    veg_only: bool = Query(False, description="Return only vegetarian foods"),
    limit: int = Query(20, description="Maximum number of foods to return")
) -> List[FoodItem]:
    """Get list of available foods"""
    foods = list(nutrition_agent.foods.values())
    
    if veg_only:
        foods = [f for f in foods if f.is_veg]
    
    foods = foods[:limit]
    
    return [
        FoodItem(
            food_id=food.food_id,
            name=food.name,
            is_veg=food.is_veg,
            ingredients=food.ingredients,
            tags=food.tags,
            nutrients=food.nutrients
        )
        for food in foods
    ]

@app.get("/foods/{food_id}")
async def get_food_details(food_id: str) -> FoodItem:
    """Get detailed information about a specific food"""
    if food_id not in nutrition_agent.foods:
        raise HTTPException(status_code=404, detail=f"Food {food_id} not found")
    
    food = nutrition_agent.foods[food_id]
    return FoodItem(
        food_id=food.food_id,
        name=food.name,
        is_veg=food.is_veg,
        ingredients=food.ingredients,
        tags=food.tags,
        nutrients=food.nutrients
    )

@app.get("/conditions")
async def get_conditions() -> List[str]:
    """Get list of all supported health conditions"""
    return list(nutrition_agent.condition_nutrients['condition'].unique())

@app.get("/conditions/{condition}/nutrients")
async def get_condition_nutrients(condition: str) -> Dict[str, List[Dict]]:
    """Get nutrients required for a specific condition"""
    condition_data = nutrition_agent.condition_nutrients[
        nutrition_agent.condition_nutrients['condition'] == condition
    ]
    
    if len(condition_data) == 0:
        raise HTTPException(status_code=404, detail=f"Condition '{condition}' not found")
    
    nutrients = []
    for _, row in condition_data.iterrows():
        nutrients.append({
            "nutrient": row['nutrient'],
            "weight": row['weight'],
            "references": row['references'] if row['references'] else None
        })
    
    return {
        "condition": condition,
        "nutrients": nutrients
    }

@app.get("/triggers/{user_id}")
async def get_active_triggers(
    user_id: str,
    now: Optional[str] = Query(None, description="Current timestamp in ISO format")
) -> Dict[str, List[str]]:
    """Get currently active triggers for a user"""
    if user_id not in nutrition_agent.users:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    # Parse timestamp
    current_time = datetime.now(pytz.UTC)
    if now:
        try:
            current_time = datetime.fromisoformat(now.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid timestamp format"
            )
    
    user = nutrition_agent.users[user_id]
    triggers = nutrition_agent.resolve_triggers(user, current_time)
    
    return {
        "user_id": user_id,
        "timestamp": current_time.isoformat(),
        "active_triggers": triggers,
        "trigger_count": len(triggers)
    }

@app.post("/evaluate")
async def run_evaluation() -> EvaluationResults:
    """Run comprehensive offline evaluation of the system"""
    try:
        evaluator = NutritionAgentEvaluator(nutrition_agent)
        results = evaluator.run_offline_evaluation()
        
        return EvaluationResults(
            eligibility_rate=results['eligibility_rate'],
            safety_violations=results['safety_violations'],
            total_notifications=results['total_notifications'],
            diversity_unique_foods=results['diversity_unique_foods'],
            diversity_ratio=results['diversity_ratio'],
            avg_score=results['avg_score'],
            avg_message_length=results['avg_message_length'],
            messages_under_160_chars=results['messages_under_160_chars']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/demo/{user_id}")
async def generate_demo_notifications(user_id: str) -> Dict:
    """Generate demo notifications across different times of day"""
    if user_id not in nutrition_agent.users:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    demo_results = []
    base_time = datetime.now(pytz.UTC)
    
    # Test different times of day
    test_times = [
        ("Morning", 8, 0),
        ("Pre-lunch", 12, 30), 
        ("Evening", 17, 30),
        ("Post-workout", 19, 0)
    ]
    
    for label, hour, minute in test_times:
        test_time = base_time.replace(hour=hour, minute=minute)
        notifications = nutrition_agent.generate_notifications(user_id, test_time)
        
        demo_results.append({
            "scenario": label,
            "time": test_time.isoformat(),
            "notifications": notifications,
            "count": len(notifications)
        })
    
    return {
        "user_id": user_id,
        "demo_scenarios": demo_results,
        "total_scenarios": len(test_times)
    }

@app.get("/analytics/system-stats")
async def get_system_statistics() -> Dict:
    """Get overall system statistics"""
    
    # User demographics
    users = list(nutrition_agent.users.values())
    diet_distribution = {}
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46+": 0}
    
    for user in users:
        # Diet preferences
        diet_distribution[user.diet_pref] = diet_distribution.get(user.diet_pref, 0) + 1
        
        # Age groups
        if user.age <= 25:
            age_groups["18-25"] += 1
        elif user.age <= 35:
            age_groups["26-35"] += 1
        elif user.age <= 45:
            age_groups["36-45"] += 1
        else:
            age_groups["46+"] += 1
    
    # Food statistics
    foods = list(nutrition_agent.foods.values())
    veg_foods = sum(1 for f in foods if f.is_veg)
    
    # Condition statistics
    all_conditions = []
    for user in users:
        all_conditions.extend(user.conditions)
    
    condition_popularity = {}
    for condition in all_conditions:
        condition_popularity[condition] = condition_popularity.get(condition, 0) + 1
    
    return {
        "system_overview": {
            "total_users": len(users),
            "total_foods": len(foods),
            "total_conditions": len(set(all_conditions)),
            "vegetarian_foods_ratio": veg_foods / len(foods) if foods else 0
        },
        "user_demographics": {
            "diet_preferences": diet_distribution,
            "age_distribution": age_groups
        },
        "popular_conditions": dict(sorted(condition_popularity.items(), 
                                        key=lambda x: x[1], reverse=True)[:5])
    }

@app.post("/simulate-week")
async def simulate_week_notifications(
    user_ids: List[str] = Query(..., description="List of user IDs to simulate")
) -> Dict:
    """Simulate notification generation over a week for specified users"""
    
    # Validate all user IDs
    invalid_users = [uid for uid in user_ids if uid not in nutrition_agent.users]
    if invalid_users:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid user IDs: {invalid_users}"
        )
    
    simulation_results = {}
    base_time = datetime.now(pytz.UTC)
    
    for user_id in user_ids:
        user_notifications = []
        daily_counts = []
        
        # Simulate 7 days
        for day in range(7):
            day_notifications = []
            current_date = base_time + timedelta(days=day)
            
            # Test multiple time points per day
            test_hours = [7, 12, 17, 19, 21]
            
            for hour in test_hours:
                test_time = current_date.replace(hour=hour, minute=30)
                notifications = nutrition_agent.generate_notifications(user_id, test_time)
                day_notifications.extend(notifications)
            
            daily_counts.append(len(day_notifications))
            user_notifications.extend(day_notifications)
        
        # Analyze user's week
        all_foods = []
        all_triggers = []
        
        for notif_set in user_notifications:
            all_triggers.append(notif_set['trigger'])
            for item in notif_set['items']:
                all_foods.append(item['food_id'])
        
        simulation_results[user_id] = {
            "total_notifications": len(user_notifications),
            "daily_breakdown": daily_counts,
            "unique_foods": len(set(all_foods)),
            "trigger_frequency": {
                trigger: all_triggers.count(trigger) 
                for trigger in set(all_triggers)
            },
            "avg_daily_notifications": sum(daily_counts) / 7
        }
    
    return {
        "simulation_period": "7 days",
        "simulated_users": len(user_ids),
        "results": simulation_results,
        "summary": {
            "total_notifications": sum(r["total_notifications"] for r in simulation_results.values()),
            "avg_notifications_per_user": sum(r["total_notifications"] for r in simulation_results.values()) / len(user_ids)
        }
    }

@app.get("/templates")
async def get_message_templates() -> Dict:
    """Get all available message templates"""
    return {
        "templates": nutrition_agent.message_templates,
        "facts": nutrition_agent.facts,
        "template_count": len(nutrition_agent.message_templates)
    }

@app.post("/test-safety")
async def test_safety_constraints(
    user_id: str = Query(..., description="User ID to test"),
    food_id: str = Query(..., description="Food ID to test")
) -> Dict:
    """Test safety constraints for a specific user-food combination"""
    
    if user_id not in nutrition_agent.users:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    if food_id not in nutrition_agent.foods:
        raise HTTPException(status_code=404, detail=f"Food {food_id} not found")
    
    user = nutrition_agent.users[user_id]
    food = nutrition_agent.foods[food_id]
    
    # Run safety checks
    diet_compatible = nutrition_agent._check_diet_compatibility(user, food)
    has_allergy_risk = nutrition_agent._has_allergy_risk(user, food)
    is_relevant = nutrition_agent._is_relevant_to_conditions(user, food)
    
    # Detailed analysis
    potential_allergens = []
    food_allergens = set(food.tags + food.ingredients)
    user_allergens = set(user.allergies)
    
    for allergen in user_allergens.intersection(food_allergens):
        potential_allergens.append(allergen)
    
    return {
        "user_id": user_id,
        "food_id": food_id,
        "safety_analysis": {
            "diet_compatible": diet_compatible,
            "diet_reason": f"User prefers {user.diet_pref}, food is {'vegetarian' if food.is_veg else 'non-vegetarian'}",
            "allergy_safe": not has_allergy_risk,
            "potential_allergens": potential_allergens,
            "condition_relevant": is_relevant
        },
        "recommendation_eligible": diet_compatible and not has_allergy_risk and is_relevant
    }

# Custom exception handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "detail": str(exc.detail)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": "Please try again later"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Nutritional Notifications AI Agent API...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Interactive API explorer at: http://localhost:8000/redoc")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
