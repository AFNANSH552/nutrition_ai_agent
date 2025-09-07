"""
Demo and Testing Script for Nutritional Notifications AI Agent
Comprehensive demonstration of system capabilities
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
import time
from nutrition_agent import NutritionAgent, NutritionAgentEvaluator

class NutritionAgentDemo:
    def __init__(self):
        self.agent = NutritionAgent()
        self.api_base = "http://localhost:8000"
        
    def run_complete_demo(self):
        """Run comprehensive demo of all system capabilities"""
        
        print("🎯" + "="*60)
        print("NUTRITIONAL NOTIFICATIONS AI AGENT - COMPLETE DEMO")
        print("="*60)
        
        # 1. System Overview
        self.show_system_overview()
        
        # 2. User Profile Analysis
        self.analyze_user_profiles()
        
        # 3. Trigger System Demo
        self.demo_trigger_system()
        
        # 4. Safety Constraint Testing
        self.test_safety_constraints()
        
        # 5. Scoring System Demo
        self.demo_scoring_system()
        
        # 6. Message Generation
        self.demo_message_generation()
        
        # 7. API Testing
        self.test_api_endpoints()
        
        # 8. Evaluation Results
        self.show_evaluation_results()
        
        # 9. Edge Cases Testing
        self.test_edge_cases()
        
        print("\n🎉" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
    
    def show_system_overview(self):
        """Display system overview and loaded data"""
        print(f"\n📊 SYSTEM OVERVIEW")
        print("-" * 30)
        print(f"Users loaded: {len(self.agent.users)}")
        print(f"Foods available: {len(self.agent.foods)}")
        print(f"Conditions supported: {len(set(self.agent.condition_nutrients['condition']))}")
        print(f"Message templates: {len(self.agent.message_templates)}")
        print(f"Contextual facts: {len(self.agent.facts)}")
        
        # Show sample data
        print(f"\n🥗 Sample Foods:")
        for i, (food_id, food) in enumerate(list(self.agent.foods.items())[:3]):
            veg_status = "🌱" if food.is_veg else "🥩"
            print(f"   {veg_status} {food.name} - {list(food.nutrients.keys())[:3]}")
        
        print(f"\n🏥 Health Conditions:")
        conditions = list(set(self.agent.condition_nutrients['condition']))[:5]
        for condition in conditions:
            print(f"   • {condition}")
    
    def analyze_user_profiles(self):
        """Analyze user profile diversity"""
        print(f"\n👥 USER PROFILE ANALYSIS")
        print("-" * 30)
        
        users = list(self.agent.users.values())
        
        # Diet preferences
        diet_dist = {}
        for user in users:
            diet_dist[user.diet_pref] = diet_dist.get(user.diet_pref, 0) + 1
        
        print("Diet Preferences:")
        for diet, count in diet_dist.items():
            percentage = (count / len(users)) * 100
            print(f"   {diet.upper()}: {count} users ({percentage:.1f}%)")
        
        # Age distribution
        ages = [user.age for user in users]
        print(f"\nAge Range: {min(ages)} - {max(ages)} years (avg: {sum(ages)/len(ages):.1f})")
        
        # Most common conditions
        all_conditions = []
        for user in users:
            all_conditions.extend(user.conditions)
        
        condition_counts = {}
        for condition in all_conditions:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        
        print(f"\nTop Conditions:")
        sorted_conditions = sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for condition, count in sorted_conditions:
            print(f"   • {condition}: {count} users")
        
        # Sample user showcase
        sample_user = users[0]
        print(f"\n👤 Sample User Profile (ID: {sample_user.user_id}):")
        print(f"   Diet: {sample_user.diet_pref}")
        print(f"   Age: {sample_user.age}, Gender: {sample_user.gender}")
        print(f"   City: {sample_user.city}")
        print(f"   Allergies: {sample_user.allergies}")
        print(f"   Conditions: {sample_user.conditions}")
        print(f"   Meal times: {sample_user.usual_meal_times}")
    
    def demo_trigger_system(self):
        """Demonstrate trigger detection system"""
        print(f"\n⏰ TRIGGER SYSTEM DEMO")
        print("-" * 30)
        
        sample_user = list(self.agent.users.values())[0]
        current_time = datetime.now(pytz.timezone(sample_user.tz))
        
        print(f"User: {sample_user.user_id}")
        print(f"Current time: {current_time.strftime('%H:%M %Z')}")
        print(f"Meal times: {sample_user.usual_meal_times}")
        
        # Test different time scenarios
        scenarios = [
            ("Morning breakfast time", 8, 0),
            ("Pre-lunch window", 13, 0),  # 30 min before 13:30 lunch
            ("Evening dinner prep", 19, 30),  # 30 min before 20:00 dinner
            ("Late evening", 22, 30),  # Should be quiet hours
        ]
        
        for scenario_name, hour, minute in scenarios:
            test_time = current_time.replace(hour=hour, minute=minute)
            triggers = self.agent.resolve_triggers(sample_user, test_time)
            
            print(f"\n🕐 {scenario_name} ({hour:02d}:{minute:02d}):")
            if triggers:
                for trigger in triggers:
                    print(f"   ✅ {trigger}")
            else:
                print("   ❌ No triggers (quiet hours or no conditions met)")
    
    def test_safety_constraints(self):
        """Test safety constraint enforcement"""
        print(f"\n🛡️ SAFETY CONSTRAINTS TESTING")
        print("-" * 30)
        
        # Create test users with specific constraints
        veg_user = None
        allergic_user = None
        
        for user in self.agent.users.values():
            if user.diet_pref == 'veg' and not veg_user:
                veg_user = user
            if user.allergies and not allergic_user:
                allergic_user = user
            if veg_user and allergic_user:
                break
        
        # Test vegetarian constraints
        if veg_user:
            print(f"🌱 Vegetarian User Test (ID: {veg_user.user_id}):")
            
            for food_id, food in list(self.agent.foods.items())[:5]:
                is_compatible = self.agent._check_diet_compatibility(veg_user, food)
                status = "✅ ALLOWED" if is_compatible else "❌ BLOCKED"
                veg_status = "VEG" if food.is_veg else "NON-VEG"
                print(f"   {food.name} ({veg_status}): {status}")
        
        # Test allergy constraints  
        if allergic_user:
            print(f"\n🚫 Allergy Safety Test (ID: {allergic_user.user_id}):")
            print(f"   User allergies: {allergic_user.allergies}")
            
            for food_id, food in list(self.agent.foods.items())[:5]:
                has_risk = self.agent._has_allergy_risk(allergic_user, food)
                status = "❌ BLOCKED" if has_risk else "✅ SAFE"
                allergens = set(food.tags + food.ingredients).intersection(set(allergic_user.allergies))
                allergen_info = f" (Contains: {list(allergens)})" if allergens else ""
                print(f"   {food.name}: {status}{allergen_info}")
    
    def demo_scoring_system(self):
        """Demonstrate the scoring system in detail"""
        print(f"\n🎯 SCORING SYSTEM DEMO")
        print("-" * 30)
        
        sample_user = list(self.agent.users.values())[0]
        sample_foods = list(self.agent.foods.values())[:3]
        current_time = datetime.now(pytz.UTC)
        
        print(f"User: {sample_user.user_id}")
        print(f"User conditions: {sample_user.conditions}")
        print(f"Scoring weights: {self.agent.weights}")
        
        candidates = self.agent.generate_candidates(sample_user, current_time, "pre_lunch")
        
        if candidates:
            ranked = self.agent.rank_candidates(candidates[:3], sample_user, current_time, "pre_lunch")
            
            print(f"\n📊 Detailed Scoring Breakdown:")
            for i, (food, total_score, scores) in enumerate(ranked, 1):
                print(f"\n{i}. {food.name} (Total Score: {total_score:.3f})")
                
                for component, score in scores.items():
                    print(f"   • {component}: {score:.3f}")
                
                print(f"   Key nutrients: {list(food.nutrients.keys())[:3]}")
                
                # Show condition relevance
                primary_condition, key_nutrients = self.agent._get_primary_condition_and_nutrients(food, sample_user)
                if primary_condition:
                    print(f"   Primary condition match: {primary_condition}")
    
    def demo_message_generation(self):
        """Demonstrate message generation with different templates"""
        print(f"\n💬 MESSAGE GENERATION DEMO")
        print("-" * 30)
        
        sample_user = list(self.agent.users.values())[0]
        current_time = datetime.now(pytz.UTC)
        
        # Generate notifications for different triggers
        triggers_to_test = ['pre_lunch', 'post_activity', 'social_viral']
        
        for trigger in triggers_to_test:
            print(f"\n🎯 Trigger: {trigger}")
            
            candidates = self.agent.generate_candidates(sample_user, current_time, trigger)
            
            if candidates:
                ranked = self.agent.rank_candidates(candidates, sample_user, current_time, trigger)
                notifications = self.agent.compose_messages(ranked, sample_user, trigger, top_n=1)
                
                if notifications:
                    notif = notifications[0]
                    print(f"   📱 Message: \"{notif.message}\"")
                    print(f"   🎯 Food: {notif.food.name}")
                    print(f"   🏥 Condition: {notif.reasons['condition']}")
                    print(f"   🧬 Key nutrients: {notif.reasons['key_nutrients']}")
                    print(f"   📏 Length: {len(notif.message)} characters")
                else:
                    print("   ❌ No notifications generated")
            else:
                print("   ❌ No candidates found")
    
    def test_api_endpoints(self):
        """Test API endpoints if server is running"""
        print(f"\n🌐 API ENDPOINTS TESTING")
        print("-" * 30)
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running!")
                health_data = response.json()
                print(f"   Status: {health_data['status']}")
                print(f"   Users loaded: {health_data['users_loaded']}")
                print(f"   Foods loaded: {health_data['foods_loaded']}")
                
                # Test user listing
                users_response = requests.get(f"{self.api_base}/users")
                if users_response.status_code == 200:
                    users = users_response.json()
                    print(f"   Available users: {len(users)}")
                
                # Test notification generation
                sample_user_id = list(self.agent.users.keys())[0]
                notif_response = requests.post(f"{self.api_base}/generate", 
                                             json={"user_id": sample_user_id})
                
                if notif_response.status_code == 200:
                    notif_data = notif_response.json()
                    print(f"   Generated {notif_data['notifications_count']} notification sets")
                    
                    if notif_data['notifications']:
                        sample_notif = notif_data['notifications'][0]
                        if sample_notif['items']:
                            print(f"   Sample: \"{sample_notif['items'][0]['message']}\"")
                
                print("✅ API testing completed successfully!")
                
            else:
                print("❌ API server not responding properly")
                
        except requests.exceptions.RequestException:
            print("⚠️ API server not running - skipping API tests")
            print("   Start the API with: python api_service.py")
    
    def show_evaluation_results(self):
        """Show comprehensive evaluation results"""
        print(f"\n📈 EVALUATION RESULTS")
        print("-" * 30)
        
        evaluator = NutritionAgentEvaluator(self.agent)
        results = evaluator.run_offline_evaluation()
        
        print(f"📊 Core Metrics:")
        print(f"   Eligibility Rate: {results['eligibility_rate']:.2%}")
        print(f"   Safety Violations: {results['safety_violations']} ({'✅ PASS' if results['safety_violations'] == 0 else '❌ FAIL'})")
        print(f"   Total Notifications: {results['total_notifications']}")
        
        print(f"\n🎯 Quality Metrics:")
        print(f"   Average Score: {results['avg_score']:.3f}")
        print(f"   Unique Foods: {results['diversity_unique_foods']}")
        print(f"   Diversity Ratio: {results['diversity_ratio']:.2%}")
        
        print(f"\n📝 Message Quality:")
        print(f"   Average Length: {results['avg_message_length']:.1f} chars")
        print(f"   Under 160 chars: {results['messages_under_160_chars']:.2%}")
        
        # Performance assessment
        print(f"\n🏆 Performance Assessment:")
        
        score = 0
        max_score = 5
        
        if results['eligibility_rate'] >= 0.8:
            print("   ✅ High eligibility rate (≥80%)")
            score += 1
        else:
            print("   ⚠️ Low eligibility rate (<80%)")
        
        if results['safety_violations'] == 0:
            print("   ✅ Perfect safety record")
            score += 1
        else:
            print("   ❌ Safety violations detected")
        
        if results['diversity_ratio'] >= 0.6:
            print("   ✅ Good diversity (≥60%)")
            score += 1
        else:
            print("   ⚠️ Low diversity (<60%)")
        
        if results['avg_score'] >= 0.5:
            print("   ✅ Strong relevance scoring (≥0.5)")
            score += 1
        else:
            print("   ⚠️ Weak relevance scoring (<0.5)")
        
        if results['messages_under_160_chars'] >= 0.9:
            print("   ✅ Excellent message length compliance (≥90%)")
            score += 1
        else:
            print("   ⚠️ Poor message length compliance (<90%)")
        
        print(f"\n🎯 Overall Score: {score}/{max_score} ({'Excellent' if score >= 4 else 'Good' if score >= 3 else 'Needs Improvement'})")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print(f"\n🧪 EDGE CASES TESTING")
        print("-" * 30)
        
        # Test user with no conditions
        print("1. User with minimal conditions:")
        minimal_user = None
        for user in self.agent.users.values():
            if len(user.conditions) <= 2:
                minimal_user = user
                break
        
        if minimal_user:
            notifications = self.agent.generate_notifications(minimal_user.user_id)
            print(f"   User {minimal_user.user_id} ({len(minimal_user.conditions)} conditions): {len(notifications)} notifications")
        
        # Test user with many allergies
        print("\n2. User with multiple allergies:")
        allergic_user = None
        for user in self.agent.users.values():
            if len(user.allergies) >= 2:
                allergic_user = user
                break
        
        if allergic_user:
            notifications = self.agent.generate_notifications(allergic_user.user_id)
            print(f"   User {allergic_user.user_id} ({len(allergic_user.allergies)} allergies): {len(notifications)} notifications")
        
        # Test rate limiting
        print("\n3. Rate limiting test:")
        test_user_id = list(self.agent.users.keys())[0]
        current_time = datetime.now(pytz.UTC)
        
        # Generate multiple notifications quickly
        for i in range(3):
            notifications = self.agent.generate_notifications(test_user_id, current_time)
            print(f"   Attempt {i+1}: {len(notifications)} notifications")
            current_time += timedelta(minutes=30)  # Small time increment
        
        # Test quiet hours
        print("\n4. Quiet hours test:")
        night_time = datetime.now(pytz.UTC).replace(hour=2, minute=0)  # 2 AM
        notifications = self.agent.generate_notifications(test_user_id, night_time)
        print(f"   Night time (2 AM): {len(notifications)} notifications (should be 0)")
        
        # Test invalid inputs
        print("\n5. Error handling:")
        try:
            invalid_notifications = self.agent.generate_notifications("invalid_user")
            print(f"   Invalid user ID: {len(invalid_notifications)} notifications (should be 0)")
        except Exception as e:
            print(f"   Invalid user ID handled gracefully: {type(e).__name__}")
    
    def demo_week_simulation(self):
        """Simulate a week of notifications for sample users"""
        print(f"\n📅 WEEK SIMULATION")
        print("-" * 30)
        
        sample_users = list(self.agent.users.keys())[:3]
        base_time = datetime.now(pytz.UTC)
        
        weekly_stats = {}
        
        for user_id in sample_users:
            daily_counts = []
            all_foods = set()
            all_triggers = []
            
            for day in range(7):
                day_notifications = 0
                current_date = base_time + timedelta(days=day)
                
                # Test key times of day
                test_times = [8, 12, 17, 19]  # Breakfast, lunch, pre-dinner, post-dinner
                
                for hour in test_times:
                    test_time = current_date.replace(hour=hour)
                    notifications = self.agent.generate_notifications(user_id, test_time)
                    
                    day_notifications += len(notifications)
                    
                    for notif_set in notifications:
                        all_triggers.append(notif_set['trigger'])
                        for item in notif_set['items']:
                            all_foods.add(item['food_id'])
                
                daily_counts.append(day_notifications)
            
            weekly_stats[user_id] = {
                'daily_counts': daily_counts,
                'total_notifications': sum(daily_counts),
                'unique_foods': len(all_foods),
                'avg_daily': sum(daily_counts) / 7,
                'trigger_distribution': {trigger: all_triggers.count(trigger) 
                                       for trigger in set(all_triggers)}
            }
        
        print("📊 Weekly Simulation Results:")
        for user_id, stats in weekly_stats.items():
            print(f"\n👤 User {user_id}:")
            print(f"   Total notifications: {stats['total_notifications']}")
            print(f"   Daily average: {stats['avg_daily']:.1f}")
            print(f"   Unique foods: {stats['unique_foods']}")
            print(f"   Daily pattern: {stats['daily_counts']}")
            
            if stats['trigger_distribution']:
                top_trigger = max(stats['trigger_distribution'].items(), key=lambda x: x[1])
                print(f"   Most common trigger: {top_trigger[0]} ({top_trigger[1]}x)")
    
    def interactive_demo(self):
        """Interactive demo mode"""
        print(f"\n🎮 INTERACTIVE DEMO MODE")
        print("-" * 30)
        print("Commands:")
        print("  'user <id>' - Get user profile")
        print("  'notif <id>' - Generate notifications for user")
        print("  'food <id>' - Get food details")
        print("  'eval' - Run evaluation")
        print("  'quit' - Exit interactive mode")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit':
                    break
                elif command.startswith('user '):
                    user_id = command.split(' ', 1)[1]
                    if user_id in self.agent.users:
                        user = self.agent.users[user_id]
                        print(f"User {user_id}: {user.diet_pref}, age {user.age}")
                        print(f"Conditions: {user.conditions}")
                        print(f"Allergies: {user.allergies}")
                    else:
                        print(f"User {user_id} not found")
                
                elif command.startswith('notif '):
                    user_id = command.split(' ', 1)[1]
                    if user_id in self.agent.users:
                        notifications = self.agent.generate_notifications(user_id)
                        print(f"Generated {len(notifications)} notification sets:")
                        for notif_set in notifications:
                            for item in notif_set['items']:
                                print(f"  📱 {item['message']}")
                    else:
                        print(f"User {user_id} not found")
                
                elif command.startswith('food '):
                    food_id = command.split(' ', 1)[1]
                    if food_id in self.agent.foods:
                        food = self.agent.foods[food_id]
                        print(f"Food {food_id}: {food.name}")
                        print(f"Vegetarian: {food.is_veg}")
                        print(f"Nutrients: {food.nutrients}")
                    else:
                        print(f"Food {food_id} not found")
                
                elif command == 'eval':
                    evaluator = NutritionAgentEvaluator(self.agent)
                    results = evaluator.run_offline_evaluation()
                    print(f"Eligibility: {results['eligibility_rate']:.2%}")
                    print(f"Safety: {results['safety_violations']} violations")
                    print(f"Score: {results['avg_score']:.3f}")
                
                else:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Interactive demo ended.")


def main():
    """Main demo execution"""
    print("🚀 Initializing Nutritional AI Agent Demo...")
    
    # Create demo instance
    demo = NutritionAgentDemo()
    
    # Check if data exists
    try:
        demo.agent.load_data()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("Please run the mock data generator first:")
        print("   python mock_data_generator.py")
        return
    
    print("✅ Demo initialized successfully!")
    print("\nSelect demo mode:")
    print("1. Complete automated demo")
    print("2. Week simulation")
    print("3. Interactive mode")
    print("4. Quick evaluation only")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            demo.run_complete_demo()
        elif choice == "2":
            demo.demo_week_simulation()
        elif choice == "3":
            demo.interactive_demo()
        elif choice == "4":
            demo.show_evaluation_results()
        else:
            print("Running complete demo...")
            demo.run_complete_demo()
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n👋 Demo completed. Thank you!")


if __name__ == "__main__":
    main()