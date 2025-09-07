# Personalized Nutritional Notifications AI Agent

A comprehensive AI-powered system that delivers science-backed, personalized nutritional notifications tailored to user profiles, health conditions, and contextual timing.

## 🎯 Features

* **Personalized Recommendations** : Matches user dietary preferences, allergies, and health conditions
* **Context-Aware Timing** : Triggers based on meal times, post-workout windows, and condition awareness
* **Science-Backed Content** : Uses nutrient-condition mappings with research references
* **Safety First** : Hard constraints for allergies and dietary restrictions
* **Multi-Modal Evaluation** : Comprehensive offline metrics and A/B testing framework
* **RESTful API** : FastAPI service with interactive documentation

## 🏗️ Architecture Overview

```
User Profile + Context → Trigger Detection → Candidate Generation → Ranking & Scoring → Message Composition → Notification Delivery
```

### Core Components

1. **Trigger System** : Pre-meal prompts, post-activity replenishment, condition reminders
2. **Candidate Generator** : Safety-first filtering with relevance matching
3. **Ranking Engine** : Multi-factor scoring with explainable weights
4. **Message Composer** : Template-based generation with contextual facts
5. **Safety Layer** : Allergy prevention and rate limiting

## 📋 Requirements

* Python 3.8+
* pandas
* numpy
* pytz
* fastapi
* uvicorn
* pydantic

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy pytz fastapi uvicorn pydantic
```

### 2. Generate Mock Data

```python
python mock_data_generator.py
```

This creates the following data files:

* `data/users.json` - User profiles with preferences and conditions
* `data/foods.json` - Food database with nutritional information
* `data/condition_nutrients.csv` - Science-backed condition-nutrient mappings
* `data/user_activity.csv` - Historical user activity logs
* `data/message_templates.json` - Notification message templates
* `data/facts.json` - Contextual "why now" facts database

### 3. Run the Core System

```python
python nutrition_agent.py
```

This will:

* Load all data
* Run unit tests
* Execute offline evaluation
* Generate sample notifications

### 4. Start the API Service

```bash
python api_service.py
```

The API will be available at:

* **Main API** : http://localhost:8000
* **Interactive Docs** : http://localhost:8000/docs
* **Alternative Docs** : http://localhost:8000/redoc

## 📊 Data Schema

### Users

```json
{
  "user_id": "u001",
  "diet_pref": "veg|nonveg|egg",
  "allergies": ["nuts", "dairy"],
  "age": 28,
  "gender": "F",
  "city": "Mumbai",
  "tz": "Asia/Kolkata",
  "usual_meal_times": {
    "breakfast": "08:30",
    "lunch": "13:30", 
    "dinner": "20:00"
  },
  "conditions": ["Glowing skin", "Gut health"]
}
```

### Foods

```json
{
  "food_id": "f001",
  "name": "Soaked Almonds",
  "is_veg": true,
  "ingredients": ["almonds"],
  "tags": ["nuts", "protein"],
  "nutrients": {
    "protein": 6.0,
    "vitamin_e": 7.3,
    "zinc": 0.9,
    "fiber": 3.5
  }
}
```

### Condition-Nutrient Mappings

```csv
condition,nutrient,weight,references
Glowing skin,vitamin_e,0.9,PMID:12345
Glowing skin,zinc,0.8,PMID:12346
Hair fall,biotin,0.9,PMID:23456
```

## 🔍 API Usage Examples

### Generate Notifications

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "u001"}'
```

### Get User Profile

```bash
curl "http://localhost:8000/users/u001"
```

### Test Safety Constraints

```bash
curl "http://localhost:8000/test-safety?user_id=u001&food_id=f001"
```

### Run System Evaluation

```bash
curl -X POST "http://localhost:8000/evaluate"
```

## 🧪 Evaluation Metrics

### Primary Metrics

* **Eligibility Rate** : % users with valid candidates per trigger
* **Safety Violations** : Should be 0 in production (hard constraint)
* **Diversity** : Unique foods recommended over time windows
* **Relevance** : Mean scoring across user conditions
* **Message Quality** : Length compliance (≤160 chars preferred)

### A/B Testing Framework

* **Control** : Random food suggestions
* **Treatment** : AI-personalized recommendations
* **Primary KPIs** : Click-through rate, save rate, add-to-cart
* **Secondary KPIs** : Long-term dietary adherence, app engagement

## ⚡ Core Functions

### Candidate Generation

```python
candidates = agent.generate_candidates(user, now, trigger)
```

### Ranking & Scoring

```python
ranked = agent.rank_candidates(candidates, user, now, trigger)
```

### Message Composition

```python
notifications = agent.compose_messages(ranked, user, trigger, top_n=3)
```

### Full Notification Pipeline

```python
notifications = agent.generate_notifications(user_id, now)
```

## 🔒 Safety Guardrails

### Hard Constraints (Pre-Scoring)

* Dietary preference compliance (veg/non-veg/egg)
* Allergy avoidance (zero tolerance)
* Availability verification

### Soft Constraints

* Rate limiting (max 2/day, 3-hour gaps)
* Quiet hours (22:00-07:00 local time)
* Novelty vs. familiarity balance

### Content Safety

* No medical claims or prescriptive language
* Science-backed facts only
* Clear sourcing with PMID references where available

## 🎯 Scoring Algorithm

```
Score = w₁ × CondMatch + w₂ × NutrientGapFit + w₃ × AvailabilityBoost + w₄ × RecencyNovelty - w₅ × AllergyRisk
```

**Default Weights:**

* CondMatch (0.4): Cosine similarity with condition requirements
* NutrientGapFit (0.3): Fills recent nutritional gaps
* AvailabilityBoost (0.2): Local availability bonus
* RecencyNovelty (0.1): Balance novelty vs. recency
* AllergyRisk (0.8): Heavy penalty for allergen presence

## 🧩 Trigger Types

### 1. Pre-Meal Prompts

* **Timing** : 30 minutes before usual meal times
* **Goal** : Optimize pre-meal nutrition for satiety and glycemic response

### 2. Post-Activity Replenishment

* **Timing** : Within 2 hours of logged workouts
* **Goal** : Support recovery with protein and glycogen replenishment

### 3. Condition Awareness

* **Timing** : Weekly check if no condition-relevant foods consumed
* **Goal** : Ensure consistent attention to health goals

### 4. Social Viral Moments

* **Timing** : Peak engagement hours (17:00-20:00)
* **Goal** : Shareable content with science facts

## 📈 Performance Benchmarks

### Typical Results (Mock Data)

* **Eligibility Rate** : 85-95% (users get valid recommendations)
* **Safety Violations** : 0 (hard constraint enforced)
* **Message Length** : <160 chars for 95%+ of notifications
* **Diversity** : 8-12 unique foods per user per week
* **Average Score** : 0.6-0.8 (out of 1.0)

## 🔧 Customization

### Adding New Conditions

1. Update `condition_nutrients.csv` with nutrient mappings
2. Add condition to user profiles in `users.json`
3. Include relevant facts in `facts.json`

### Modifying Scoring Weights

```python
agent.weights = {
    'w1': 0.5,  # Increase condition matching importance
    'w2': 0.2,  # Decrease gap fitting importance
    'w3': 0.2,  # Keep availability weight
    'w4': 0.1,  # Keep novelty weight
    'w5': 1.0   # Increase allergy penalty
}
```

### Adding Message Templates

```json
{
  "template_id": "custom_template",
  "text": "{food} provides {benefit} because {why_now}. {cta}",
  "style": "scientific",
  "lang": "en"
}
```

## 🚧 Known Limitations

1. **Mock Availability** : Real-time restaurant/store integration needed
2. **Single Language** : Currently English-only templates
3. **Simple Scheduling** : No advanced ML-based optimal timing
4. **Limited Conditions** : 8 health conditions in mock data
5. **No User Feedback Loop** : Static preference learning

## 🔮 Future Enhancements

### Near Term

* Multi-language support (Hindi, regional languages)
* Real inventory/restaurant API integration
* User feedback incorporation for preference learning
* Advanced bandits for exploration/exploitation

### Medium Term

* Wearable device integration (sleep, activity, heart rate)
* Social sharing optimization with engagement tracking
* Meal planning integration
* Nutrition goal progression tracking

### Long Term

* Real-time biomarker integration (glucose, ketones)
* AI-generated recipe suggestions
* Community features and challenges
* Advanced ML models for timing optimization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Run evaluation suite (`python nutrition_agent.py`)
5. Submit pull request with detailed description

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

* Nutritional data based on USDA food composition databases
* Scientific references from PubMed research papers
* Trigger timing based on chronobiology research
* Safety patterns from food allergy management guidelines

---

## 📞 Support

For questions, issues, or contributions:

* **Issues** : Create GitHub issue with detailed description
* **API Questions** : Check `/docs` endpoint for interactive examples
* **Performance** : Run `/evaluate` endpoint for system health metrics
* **Safety Concerns** : All safety violations logged and should be 0

**Happy Healthy Eating! 🥗💪**
