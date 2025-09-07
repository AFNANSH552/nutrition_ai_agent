"""
Personalized Nutritional Notifications AI Agent
Main implementation with all core components
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math
import random

@dataclass
class User:
    user_id: str
    diet_pref: str
    allergies: List[str]
    age: int
    gender: str
    city: str
    tz: str
    usual_meal_times: Dict[str, str]
    conditions: List[str]

@dataclass
class Food:
    food_id: str
    name: str
    is_veg: bool
    ingredients: List[str]
    tags: List[str]
    nutrients: Dict[str, float]

@dataclass
class NotificationCandidate:
    food: Food
    score: float
    reasons: Dict
    message: str
    cta: Dict

class NutritionAgent:
    def __init__(self):
        self.users = {}
        self.foods = {}
        self.condition_nutrients = pd.DataFrame()
        self.activity_logs = pd.DataFrame()
        self.message_templates = {}
        self.facts = {}
        self.recent_notifications = {}  # user_id -> list of recent notifications
        
        # Scoring weights
        self.weights = {
            'w1': 0.4,  # CondMatch
            'w2': 0.3,  # NutrientGapFit  
            'w3': 0.2,  # AvailabilityBoost
            'w4': 0.1,  # RecencyNovelty
            'w5': 0.8   # AllergyRisk (penalty)
        }
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load all data from files"""
        try:
            # Load users
            with open('data/users.json', 'r') as f:
                users_data = json.load(f)
            for user_data in users_data:
                self.users[user_data['user_id']] = User(**user_data)
            
            # Load foods
            with open('data/foods.json', 'r') as f:
                foods_data = json.load(f)
            for food_data in foods_data:
                self.foods[food_data['food_id']] = Food(**food_data)
            
            # Load condition-nutrient mappings
            self.condition_nutrients = pd.read_csv('data/condition_nutrients.csv')
            
            # Load activity logs
            self.activity_logs = pd.read_csv('data/user_activity.csv')
            self.activity_logs['ts'] = pd.to_datetime(self.activity_logs['ts'])
            
            # Load templates
            with open('data/message_templates.json', 'r') as f:
                templates_data = json.load(f)
            for template in templates_data:
                self.message_templates[template['template_id']] = template
            
            # Load facts
            with open('data/facts.json', 'r') as f:
                self.facts = json.load(f)
                
            print("✅ Data loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            print("Please run the mock data generation script first")
    

def resolve_triggers(self, user: User, now: datetime) -> List[str]:
    """Determine which triggers should fire for a user at given time"""
    triggers = []

    # Ensure `now` is timezone-aware UTC
    now = pd.to_datetime(now).tz_convert("UTC")

    # Ensure activity log timestamps are timezone-aware UTC
    self.activity_logs['ts'] = pd.to_datetime(
        self.activity_logs['ts'],
        errors="coerce"
    ).dt.tz_localize("UTC", nonexistent="NaT", ambiguous="NaT")

    # Convert to user timezone for meal/quiet hour logic
    user_tz = pytz.timezone(user.tz)
    user_now = now.astimezone(user_tz)
    current_time = user_now.strftime('%H:%M')
    current_hour = user_now.hour

    # Skip quiet hours (22:00-07:00)
    if current_hour >= 22 or current_hour <= 7:
        return triggers

    # Pre-meal trigger (30 minutes before meals)
    for meal, meal_time in user.usual_meal_times.items():
        meal_dt = datetime.strptime(meal_time, '%H:%M').time()
        meal_with_date = user_now.replace(hour=meal_dt.hour, minute=meal_dt.minute)
        pre_meal_time = meal_with_date - timedelta(minutes=30)

        # Check if current time is within 5 minutes of pre-meal time
        time_diff = abs((user_now - pre_meal_time).total_seconds())
        if time_diff <= 300:  # 5 minutes tolerance
            triggers.append(f'pre_{meal}')

    # Post-activity trigger (check recent workouts)
    recent_activities = self.activity_logs[
        (self.activity_logs['user_id'] == user.user_id) &
        (self.activity_logs['event'] == 'worked_out') &
        (self.activity_logs['ts'] >= now - timedelta(hours=2))
    ]
    if len(recent_activities) > 0:
        triggers.append('post_activity')

    # Condition awareness trigger (weekly check)
    for condition in user.conditions:
        if self._should_remind_condition(user.user_id, condition, now):
            triggers.append(f'condition_{condition.lower().replace(" ", "_")}')

    # Social viral moment (random chance during peak hours)
    if 17 <= current_hour <= 20 and random.random() < 0.1:  # 10% chance during evening
        triggers.append('social_viral')

    return triggers

    
    def _should_remind_condition(self, user_id: str, condition: str, now: datetime) -> bool:
        """Check if user needs reminder for a specific condition"""
        # Get foods that address this condition
        condition_nutrients = self.condition_nutrients[
            self.condition_nutrients['condition'] == condition
        ]
        relevant_nutrients = set(condition_nutrients['nutrient'].values)
        
        # Check recent food consumption
        week_ago = now - timedelta(days=7)
        recent_foods = self.activity_logs[
            (self.activity_logs['user_id'] == user_id) &
            (self.activity_logs['event'] == 'consumed') &
            (self.activity_logs['ts'] >= week_ago)
        ]
        
        # Check if any consumed foods address this condition
        consumed_nutrients = set()
        for _, activity in recent_foods.iterrows():
            if pd.notna(activity['food_id']) and activity['food_id'] in self.foods:
                food = self.foods[activity['food_id']]
                consumed_nutrients.update(food.nutrients.keys())
        
        # If no overlap with condition nutrients, trigger reminder
        return len(relevant_nutrients.intersection(consumed_nutrients)) == 0
    
    def generate_candidates(self, user: User, now: datetime, trigger: str) -> List[Food]:
        """Generate candidate foods based on constraints and trigger"""
        candidates = []
        
        for food_id, food in self.foods.items():
            # Hard constraint: dietary preference
            if not self._check_diet_compatibility(user, food):
                continue
            
            # Hard constraint: allergies
            if self._has_allergy_risk(user, food):
                continue
            
            # Relevance: must match at least one user condition
            if not self._is_relevant_to_conditions(user, food):
                continue
            
            # Availability check (mock - assume all available for now)
            if not self._is_available(user, food, now):
                continue
            
            candidates.append(food)
        
        return candidates
    
    def _check_diet_compatibility(self, user: User, food: Food) -> bool:
        """Check if food matches user's dietary preference"""
        if user.diet_pref == 'veg':
            return food.is_veg
        elif user.diet_pref == 'nonveg':
            return True  # Non-veg users can eat everything
        elif user.diet_pref == 'egg':
            return food.is_veg or 'eggs' in food.ingredients
        return True
    
    def _has_allergy_risk(self, user: User, food: Food) -> bool:
        """Check if food contains user allergens"""
        food_allergens = set(food.tags + food.ingredients)
        user_allergens = set(user.allergies)
        return len(food_allergens.intersection(user_allergens)) > 0
    
    def _is_relevant_to_conditions(self, user: User, food: Food) -> bool:
        """Check if food is relevant to user's conditions"""
        food_nutrients = set(food.nutrients.keys())
        
        for condition in user.conditions:
            condition_nutrients = self.condition_nutrients[
                self.condition_nutrients['condition'] == condition
            ]
            required_nutrients = set(condition_nutrients['nutrient'].values)
            
            if len(food_nutrients.intersection(required_nutrients)) > 0:
                return True
        
        return False
    
    def _is_available(self, user: User, food: Food, now: datetime) -> bool:
        """Mock availability check - assume all foods available"""
        # In real implementation, would check local restaurants/stores
        return True
    
    def rank_candidates(self, candidates: List[Food], user: User, now: datetime, trigger: str) -> List[Tuple[Food, float, Dict]]:
        """Rank candidates using weighted scoring"""
        scored_candidates = []
        
        for food in candidates:
            scores = self._calculate_scores(food, user, now, trigger)
            total_score = (
                self.weights['w1'] * scores['CondMatch'] +
                self.weights['w2'] * scores['NutrientGapFit'] +
                self.weights['w3'] * scores['AvailabilityBoost'] +
                self.weights['w4'] * scores['RecencyNovelty'] -
                self.weights['w5'] * scores['AllergyRisk']
            )
            
            scored_candidates.append((food, total_score, scores))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates
    
    def _calculate_scores(self, food: Food, user: User, now: datetime, trigger: str) -> Dict[str, float]:
        """Calculate individual scoring components"""
        scores = {}
        
        # CondMatch: cosine similarity between food nutrients and condition weights
        scores['CondMatch'] = self._calculate_condition_match(food, user)
        
        # NutrientGapFit: alignment with recent nutritional gaps
        scores['NutrientGapFit'] = self._calculate_nutrient_gap_fit(food, user, now)
        
        # AvailabilityBoost: currently always 1.0 (mock)
        scores['AvailabilityBoost'] = 1.0
        
        # RecencyNovelty: balance between new foods and avoiding recent repeats
        scores['RecencyNovelty'] = self._calculate_recency_novelty(food, user, now)
        
        # AllergyRisk: should be 0 after hard filtering
        scores['AllergyRisk'] = 0.0
        
        return scores
    
    def _calculate_condition_match(self, food: Food, user: User) -> float:
        """Calculate cosine similarity between food nutrients and condition requirements"""
        # Get all nutrients mentioned in user conditions
        condition_nutrients = self.condition_nutrients[
            self.condition_nutrients['condition'].isin(user.conditions)
        ]
        
        if len(condition_nutrients) == 0:
            return 0.0
        
        # Create vectors
        all_nutrients = list(set(condition_nutrients['nutrient'].values))
        
        # Food vector
        food_vector = []
        for nutrient in all_nutrients:
            food_vector.append(food.nutrients.get(nutrient, 0.0))
        
        # Condition weight vector
        condition_vector = []
        for nutrient in all_nutrients:
            weight = condition_nutrients[
                condition_nutrients['nutrient'] == nutrient
            ]['weight'].mean()
            condition_vector.append(weight if not pd.isna(weight) else 0.0)
        
        # Calculate cosine similarity
        return self._cosine_similarity(food_vector, condition_vector)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_nutrient_gap_fit(self, food: Food, user: User, now: datetime) -> float:
        """Calculate how well food fills recent nutritional gaps"""
        # Get recent food consumption (last 24 hours)
        yesterday = now - timedelta(days=1)
        recent_foods = self.activity_logs[
            (self.activity_logs['user_id'] == user.user_id) &
            (self.activity_logs['event'] == 'consumed') &
            (self.activity_logs['ts'] >= yesterday)
        ]
        
        # Calculate consumed nutrients
        consumed_nutrients = {}
        for _, activity in recent_foods.iterrows():
            if pd.notna(activity['food_id']) and activity['food_id'] in self.foods:
                consumed_food = self.foods[activity['food_id']]
                for nutrient, amount in consumed_food.nutrients.items():
                    consumed_nutrients[nutrient] = consumed_nutrients.get(nutrient, 0) + amount
        
        # Get target nutrients for user conditions
        target_nutrients = {}
        for condition in user.conditions:
            condition_nutrients = self.condition_nutrients[
                self.condition_nutrients['condition'] == condition
            ]
            for _, row in condition_nutrients.iterrows():
                nutrient = row['nutrient']
                weight = row['weight']
                target_nutrients[nutrient] = max(target_nutrients.get(nutrient, 0), weight)
        
        # Calculate gap coverage by this food
        gap_coverage = 0.0
        total_gaps = 0
        
        for nutrient, target_weight in target_nutrients.items():
            consumed = consumed_nutrients.get(nutrient, 0)
            food_provides = food.nutrients.get(nutrient, 0)
            
            if consumed < target_weight:  # There's a gap
                gap_size = target_weight - consumed
                coverage = min(food_provides / gap_size, 1.0) if gap_size > 0 else 0.0
                gap_coverage += coverage
                total_gaps += 1
        
        return gap_coverage / total_gaps if total_gaps > 0 else 0.0
    
    def _calculate_recency_novelty(self, food: Food, user: User, now: datetime) -> float:
        """Calculate recency/novelty score"""
        # Check recent notifications for this user
        user_recent = self.recent_notifications.get(user.user_id, [])
        
        # Check if this food was recently recommended
        week_ago = now - timedelta(days=7)
        recent_food_ids = [notif['food_id'] for notif in user_recent 
                          if datetime.fromisoformat(notif['timestamp']) >= week_ago]
        
        if food.food_id in recent_food_ids:
            return 0.1  # Low score for recently recommended foods
        else:
            return 0.9  # High score for novel foods
    
    def compose_messages(self, ranked_candidates: List[Tuple[Food, float, Dict]], 
                        user: User, trigger: str, top_n: int = 3) -> List[NotificationCandidate]:
        """Compose notification messages from ranked candidates"""
        notifications = []
        
        for i, (food, score, scores) in enumerate(ranked_candidates[:top_n]):
            # Determine primary condition and benefit
            primary_condition, key_nutrients = self._get_primary_condition_and_nutrients(food, user)
            benefit = self._generate_benefit_text(key_nutrients, primary_condition)
            
            # Select appropriate template and generate message
            template_id = self._select_template(trigger)
            template = self.message_templates[template_id]
            
            # Generate why_now fact
            why_now = self._get_why_now_fact(trigger)
            
            # Generate CTA
            cta = self._generate_cta(food, primary_condition)
            
            # Fill template
            message = self._fill_template(
                template, food, benefit, primary_condition, why_now, cta
            )
            
            # Create notification candidate
            notification = NotificationCandidate(
                food=food,
                score=score,
                reasons={
                    'condition': primary_condition,
                    'key_nutrients': key_nutrients,
                    'why_now': why_now,
                    'scores': scores
                },
                message=message,
                cta=cta
            )
            
            notifications.append(notification)
        
        return notifications
    
    def _get_primary_condition_and_nutrients(self, food: Food, user: User) -> Tuple[str, List[str]]:
        """Determine primary condition and key nutrients for this food-user pair"""
        best_condition = ""
        best_score = 0.0
        key_nutrients = []
        
        for condition in user.conditions:
            condition_nutrients = self.condition_nutrients[
                self.condition_nutrients['condition'] == condition
            ]
            
            # Calculate condition relevance score
            score = 0.0
            condition_key_nutrients = []
            
            for _, row in condition_nutrients.iterrows():
                nutrient = row['nutrient']
                weight = row['weight']
                
                if nutrient in food.nutrients and food.nutrients[nutrient] > 0:
                    score += weight * food.nutrients[nutrient]
                    condition_key_nutrients.append(nutrient)
            
            if score > best_score:
                best_score = score
                best_condition = condition
                key_nutrients = condition_key_nutrients
        
        return best_condition, key_nutrients
    
    def _generate_benefit_text(self, nutrients: List[str], condition: str) -> str:
        """Generate benefit text based on nutrients and condition"""
        if not nutrients:
            return f"supports {condition.lower()}"
        
        # Map nutrients to user-friendly names
        nutrient_names = {
            'vitamin_e': 'Vitamin E',
            'zinc': 'Zinc',
            'vitamin_c': 'Vitamin C',
            'protein': 'protein',
            'iron': 'iron',
            'fiber': 'fiber',
            'omega3': 'Omega-3',
            'probiotics': 'probiotics',
            'magnesium': 'magnesium'
        }
        
        friendly_nutrients = [nutrient_names.get(n, n) for n in nutrients[:2]]  # Top 2
        
        if len(friendly_nutrients) == 1:
            return f"{friendly_nutrients[0]} boost"
        elif len(friendly_nutrients) == 2:
            return f"{friendly_nutrients[0]} + {friendly_nutrients[1]} boost"
        else:
            return "nutrient boost"
    
    def _select_template(self, trigger: str) -> str:
        """Select appropriate message template based on trigger"""
        template_map = {
            'pre_breakfast': 'pre_meal_basic',
            'pre_lunch': 'pre_meal_basic', 
            'pre_dinner': 'pre_meal_basic',
            'post_activity': 'post_workout',
            'social_viral': 'science_fact'
        }
        
        # Handle condition-specific triggers
        if trigger.startswith('condition_'):
            return 'condition_reminder'
        
        return template_map.get(trigger, 'pre_meal_basic')
    
    def _get_why_now_fact(self, trigger: str) -> str:
        """Get appropriate why_now fact based on trigger"""
        fact_map = {
            'pre_breakfast': 'morning_boost',
            'pre_lunch': 'pre_meal',
            'pre_dinner': 'pre_meal', 
            'post_activity': 'post_activity',
            'social_viral': 'omega3_benefits'
        }
        
        if trigger.startswith('condition_'):
            return 'evening_repair'
        
        fact_key = fact_map.get(trigger, 'pre_meal')
        return self.facts.get(fact_key, "Science-backed nutrition timing matters")
    
    def _generate_cta(self, food: Food, condition: str) -> Dict:
        """Generate call-to-action"""
        return {
            'label': 'Learn more',
            'deep_link': f"app://explore?food={food.food_id}&condition={condition.replace(' ', '%20')}"
        }
    
    def _fill_template(self, template: Dict, food: Food, benefit: str, 
                      condition: str, why_now: str, cta: Dict) -> str:
        """Fill message template with actual content"""
        text = template['text']
        
        # Replace placeholders
        replacements = {
            '{food}': food.name,
            '{benefit}': benefit,
            '{condition}': condition.lower(),
            '{why_now}': why_now,
            '{cta}': f"Try {food.name.lower()}"
        }
        
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        
        # Ensure message length <= 160 characters
        if len(text) > 160:
            text = text[:157] + "..."
        
        return text
    
    def generate_notifications(self, user_id: str, now: datetime = None) -> List[Dict]:
        """Main entry point - generate notifications for a user"""
        if now is None:
            now = datetime.now(pytz.UTC)
        
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        
        # Check rate limiting
        if not self._check_rate_limits(user_id, now):
            return []
        
        # Resolve triggers
        triggers = self.resolve_triggers(user, now)
        
        if not triggers:
            return []
        
        all_notifications = []
        
        for trigger in triggers:
            # Generate candidates
            candidates = self.generate_candidates(user, now, trigger)
            
            if not candidates:
                continue
            
            # Rank candidates
            ranked = self.rank_candidates(candidates, user, now, trigger)
            
            # Compose messages
            notifications = self.compose_messages(ranked, user, trigger, top_n=1)
            
            if notifications:
                # Convert to output format
                notification_dict = {
                    'user_id': user_id,
                    'trigger': trigger,
                    'generated_at': now.isoformat(),
                    'items': []
                }
                
                for notif in notifications:
                    item = {
                        'food_id': notif.food.food_id,
                        'name': notif.food.name,
                        'score': round(notif.score, 3),
                        'reasons': {
                            'condition': notif.reasons['condition'],
                            'key_nutrients': notif.reasons['key_nutrients'],
                            'why_now': notif.reasons['why_now']
                        },
                        'message': notif.message,
                        'cta': notif.cta,
                        'scores_breakdown': {k: round(v, 3) for k, v in notif.reasons['scores'].items()},
                        'weights': self.weights
                    }
                    notification_dict['items'].append(item)
                
                all_notifications.append(notification_dict)
                
                # Update recent notifications tracking
                self._update_recent_notifications(user_id, notifications[0], now)
        
        return all_notifications
    
    def _check_rate_limits(self, user_id: str, now: datetime) -> bool:
        """Check if user hasn't exceeded notification rate limits"""
        user_recent = self.recent_notifications.get(user_id, [])
        
        # Check daily limit (max 2 per day)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_notifications = [
            notif for notif in user_recent 
            if datetime.fromisoformat(notif['timestamp']) >= today_start
        ]
        
        if len(today_notifications) >= 2:
            return False
        
        # Check minimum gap (3 hours)
        if user_recent:
            last_notification_time = datetime.fromisoformat(user_recent[-1]['timestamp'])
            if (now - last_notification_time).total_seconds() < 10800:  # 3 hours
                return False
        
        return True
    
    def _update_recent_notifications(self, user_id: str, notification: NotificationCandidate, now: datetime):
        """Update recent notifications tracking"""
        if user_id not in self.recent_notifications:
            self.recent_notifications[user_id] = []
        
        self.recent_notifications[user_id].append({
            'food_id': notification.food.food_id,
            'timestamp': now.isoformat(),
            'trigger': 'recent'
        })
        
        # Keep only last 20 notifications per user
        self.recent_notifications[user_id] = self.recent_notifications[user_id][-20:]


# Evaluation and Testing Functions
class NutritionAgentEvaluator:
    def __init__(self, agent: NutritionAgent):
        self.agent = agent
    
    def run_offline_evaluation(self) -> Dict:
        """Run comprehensive offline evaluation"""
        results = {}
        
        # Test all users over a week simulation
        test_users = list(self.agent.users.keys())[:10]  # Test subset
        base_time = datetime.now(pytz.UTC)
        
        all_notifications = []
        safety_violations = 0
        eligibility_counts = {'eligible': 0, 'total': 0}
        
        for day in range(7):
            current_time = base_time + timedelta(days=day)
            
            for hour in [8, 13, 18, 20]:  # Test key hours
                test_time = current_time.replace(hour=hour)
                
                for user_id in test_users:
                    eligibility_counts['total'] += 1
                    
                    notifications = self.agent.generate_notifications(user_id, test_time)
                    
                    if notifications:
                        eligibility_counts['eligible'] += 1
                        all_notifications.extend(notifications)
                        
                        # Check safety violations
                        for notif_set in notifications:
                            for item in notif_set['items']:
                                if self._has_safety_violation(user_id, item['food_id']):
                                    safety_violations += 1
        
        # Calculate metrics
        results['eligibility_rate'] = eligibility_counts['eligible'] / eligibility_counts['total']
        results['safety_violations'] = safety_violations
        results['total_notifications'] = len(all_notifications)
        
        # Calculate diversity (unique foods)
        all_food_ids = []
        for notif_set in all_notifications:
            for item in notif_set['items']:
                all_food_ids.append(item['food_id'])
        
        unique_foods = len(set(all_food_ids))
        results['diversity_unique_foods'] = unique_foods
        results['diversity_ratio'] = unique_foods / len(all_food_ids) if all_food_ids else 0
        
        # Calculate average scores and message lengths
        scores = []
        message_lengths = []
        
        for notif_set in all_notifications:
            for item in notif_set['items']:
                scores.append(item['score'])
                message_lengths.append(len(item['message']))
        
        results['avg_score'] = np.mean(scores) if scores else 0
        results['avg_message_length'] = np.mean(message_lengths) if message_lengths else 0
        results['messages_under_160_chars'] = sum(1 for l in message_lengths if l <= 160) / len(message_lengths) if message_lengths else 0
        
        return results
    
    def _has_safety_violation(self, user_id: str, food_id: str) -> bool:
        """Check if recommendation violates safety constraints"""
        user = self.agent.users[user_id]
        food = self.agent.foods[food_id]
        
        # Check dietary preference violation
        if not self.agent._check_diet_compatibility(user, food):
            return True
        
        # Check allergy violation
        if self.agent._has_allergy_risk(user, food):
            return True
        
        return False
    
    def print_evaluation_report(self, results: Dict):
        """Print formatted evaluation report"""
        print("\n" + "="*50)
        print("NUTRITIONAL AI AGENT - EVALUATION REPORT")
        print("="*50)
        
        print(f"\n📊 CORE METRICS:")
        print(f"   Eligibility Rate: {results['eligibility_rate']:.2%}")
        print(f"   Safety Violations: {results['safety_violations']}")
        print(f"   Total Notifications: {results['total_notifications']}")
        
        print(f"\n🎯 QUALITY METRICS:")
        print(f"   Average Score: {results['avg_score']:.3f}")
        print(f"   Unique Foods Recommended: {results['diversity_unique_foods']}")
        print(f"   Diversity Ratio: {results['diversity_ratio']:.2%}")
        
        print(f"\n📝 MESSAGE METRICS:")
        print(f"   Average Message Length: {results['avg_message_length']:.1f} chars")
        print(f"   Messages ≤160 chars: {results['messages_under_160_chars']:.2%}")
        
        print(f"\n✅ SAFETY STATUS:")
        if results['safety_violations'] == 0:
            print("   🟢 All safety constraints satisfied!")
        else:
            print(f"   🔴 {results['safety_violations']} safety violations detected")


# Unit Tests
def run_unit_tests():
    """Run basic unit tests for core functionality"""
    print("\n🧪 Running Unit Tests...")
    
    agent = NutritionAgent()
    
    # Test 1: Data loading
    assert len(agent.users) > 0, "Users not loaded"
    assert len(agent.foods) > 0, "Foods not loaded"
    print("✅ Test 1 passed: Data loading")
    
    # Test 2: Diet compatibility
    user = list(agent.users.values())[0]
    veg_user = User(
        user_id="test_veg", diet_pref="veg", allergies=[], 
        age=25, gender="F", city="Mumbai", tz="Asia/Kolkata",
        usual_meal_times={}, conditions=["Glowing skin"]
    )
    
    for food in agent.foods.values():
        if not food.is_veg:
            assert not agent._check_diet_compatibility(veg_user, food), f"Veg user should not get {food.name}"
    print("✅ Test 2 passed: Diet compatibility")
    
    # Test 3: Allergy filtering
    allergic_user = User(
        user_id="test_allergy", diet_pref="veg", allergies=["nuts"], 
        age=25, gender="F", city="Mumbai", tz="Asia/Kolkata",
        usual_meal_times={}, conditions=["Glowing skin"]
    )
    
    for food in agent.foods.values():
        if "nuts" in food.tags or "nuts" in food.ingredients:
            assert agent._has_allergy_risk(allergic_user, food), f"Allergic user should be blocked from {food.name}"
    print("✅ Test 3 passed: Allergy filtering")
    
    # Test 4: Basic notification generation
    test_user_id = list(agent.users.keys())[0]
    notifications = agent.generate_notifications(test_user_id)
    assert isinstance(notifications, list), "Should return list of notifications"
    print("✅ Test 4 passed: Notification generation")
    
    print("🎉 All unit tests passed!")


if __name__ == "__main__":
    # Load and test the system
    agent = NutritionAgent()
    
    # Run unit tests
    run_unit_tests()
    
    # Run evaluation
    evaluator = NutritionAgentEvaluator(agent)
    results = evaluator.run_offline_evaluation()
    evaluator.print_evaluation_report(results)
    
    # Demo notification generation
    print("\n" + "="*50)
    print("DEMO: Sample Notifications")
    print("="*50)
    
    sample_user_id = list(agent.users.keys())[0]
    demo_notifications = agent.generate_notifications(sample_user_id)
    
    if demo_notifications:
        for i, notif_set in enumerate(demo_notifications, 1):
            print(f"\n📱 Notification Set {i}:")
            print(f"   Trigger: {notif_set['trigger']}")
            for item in notif_set['items']:
                print(f"   💬 {item['message']}")
                print(f"   🎯 Score: {item['score']} | Condition: {item['reasons']['condition']}")
    else:
        print("No notifications generated for demo user at this time.")