# Personalized Nutritional Notifications AI Agent - Design Document

## Problem Framing

### Objective

Build an AI agent that delivers science-backed, personalized nutritional notifications tailored to user profiles, health conditions, and contextual timing.

### Key Performance Indicators (KPIs)

- **Notification Quality**: Relevance score based on condition-nutrient matching
- **Safety**: Zero allergy/dietary violations in final output
- **Engagement Proxy**: CTR simulation based on personalization factors
- **Diversity**: Gini coefficient of food recommendations over time
- **Novelty**: Percentage of new foods (not shown in last 7 days)
- **Constraint Satisfaction**: 100% compliance with dietary preferences and allergies

## High-Level Architecture

```
User Profile + Context → Trigger Detection → Candidate Generation → Ranking & Scoring → Message Composition → Notification Delivery
```

### Core Components

1. **Trigger System**: Detects notification opportunities based on time, activity, and user behavior
2. **Candidate Generator**: Filters foods based on safety constraints and relevance
3. **Ranking Engine**: Scores candidates using multi-factor weighted scoring
4. **Message Composer**: Template-based message generation with contextual facts
5. **Scheduler**: Rate limiting and deduplication logic

## Data Schema Design

### User Profiles

- Basic demographics and preferences
- Health conditions and goals
- Meal timing patterns
- Allergy and dietary restrictions

### Food Database

- Nutritional composition
- Dietary compatibility flags
- Ingredient lists for allergy checking

### Condition-Nutrient Mapping

- Science-backed nutrient requirements per condition
- Weighted importance scores

### User Activity Logs

- Food consumption history
- Exercise/activity tracking
- Engagement with previous notifications

## Feature Engineering

### Scoring Components

1. **CondMatch** (0.4 weight): Cosine similarity between food nutrients and condition requirements
2. **NutrientGapFit** (0.3 weight): Alignment with recent nutritional gaps
3. **AvailabilityBoost** (0.2 weight): Local availability bonus
4. **RecencyNovelty** (0.1 weight): Novelty vs recency trade-off
5. **AllergyRisk** (-0.8 weight): Hard penalty for allergen presence

### Safety Guardrails

- Pre-scoring hard filters for diet/allergy constraints
- Medical claim avoidance in messaging
- Rate limiting (max 2/day, 3h minimum gap)
- Quiet hours enforcement (22:00-07:00)

## Trigger Cases Implementation

1. **Pre-meal Prompt**: 30 minutes before usual meal times
2. **Post-activity Replenish**: Within 2 hours of logged workouts
3. **Condition Awareness**: Weekly engagement check per condition
4. **Social Viral Moment**: Shareable science facts with trending foods

## Evaluation Strategy

### Offline Metrics

- Eligibility Rate: % users with valid candidates per trigger
- Safety Violations: Should be 0 in production
- Diversity: Food variety over weekly windows
- Relevance: Mean top-1 scoring across user base

### A/B Testing Framework

- Control: Random food suggestions
- Treatment: Personalized AI recommendations
- Primary: Click-through rate, save rate
- Secondary: Long-term dietary adherence, app engagement

## Technical Assumptions

- Timezone: Asia/Kolkata default
- Message length: ≤160 characters preferred
- Availability API: Mock restaurant/store data
- LLM usage: Optional, template-first approach
- Data freshness: Daily batch processing acceptable

## Future Work

- Real-time inventory integration
- Multi-language support
- Advanced bandits for exploration/exploitation
- Social sharing optimization
- Wearable device integration
