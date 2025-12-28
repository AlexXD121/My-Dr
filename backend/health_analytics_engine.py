"""
Health Analytics Engine for My Dr AI Medical Assistant
Provides comprehensive health data analysis, pattern recognition, and insights generation
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
import json
import statistics
from collections import defaultdict, Counter

from models import (
    User, Conversation, Message, MedicalRecord, HealthAnalytics,
    SymptomRecord
)
from drug_interaction_models import UserMedication, DrugInteractionReport
from database import get_db_session

logger = logging.getLogger(__name__)


class HealthAnalyticsEngine:
    """
    Comprehensive health analytics engine for data pattern recognition,
    trend analysis, and personalized health insights generation
    """
    
    def __init__(self):
        self.logger = logger
        self.version = "2.0"
    
    async def generate_comprehensive_analytics(
        self, 
        user_id: str, 
        period_type: str = "monthly",
        analysis_scope: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive health analytics for a user
        
        Args:
            user_id: User ID to analyze
            period_type: Analysis period (daily, weekly, monthly, quarterly, yearly)
            analysis_scope: Scope of analysis (comprehensive, symptoms_only, consultations_only)
        
        Returns:
            Dictionary containing comprehensive analytics data
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            with get_db_session() as db:
                # Get user data
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise ValueError(f"User {user_id} not found")
                
                # Calculate period boundaries
                period_start, period_end = self._calculate_period_boundaries(period_type)
                
                # Generate analytics components
                analytics_data = {
                    "user_id": user_id,
                    "period_type": period_type,
                    "period_start": period_start,
                    "period_end": period_end,
                    "analysis_scope": analysis_scope,
                    "generated_at": start_time,
                    "version": self.version
                }
                
                # Basic consultation metrics
                consultation_metrics = await self._analyze_consultation_patterns(db, user_id, period_start, period_end)
                analytics_data.update(consultation_metrics)
                
                # Symptom analysis
                if analysis_scope in ["comprehensive", "symptoms_only"]:
                    symptom_analytics = await self._analyze_symptom_patterns(db, user_id, period_start, period_end)
                    analytics_data.update(symptom_analytics)
                
                # Health trends analysis
                health_trends = await self._analyze_health_trends(db, user_id, period_start, period_end)
                analytics_data.update(health_trends)
                
                # Risk assessment
                risk_assessment = await self._calculate_risk_assessment(db, user_id, period_start, period_end)
                analytics_data["risk_assessment"] = risk_assessment
                
                # Generate insights and recommendations
                insights = await self._generate_health_insights(db, user_id, analytics_data)
                analytics_data["health_insights"] = insights
                
                recommendations = await self._generate_personalized_recommendations(db, user_id, analytics_data)
                analytics_data["personalized_recommendations"] = recommendations
                
                # Calculate overall health score
                health_score = await self._calculate_overall_health_score(analytics_data)
                analytics_data["overall_health_score"] = health_score
                
                # Calculate computation time
                computation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                analytics_data["computation_time_ms"] = int(computation_time)
                
                self.logger.info(f"Generated comprehensive analytics for user {user_id} in {computation_time:.2f}ms")
                
                return analytics_data
                
        except Exception as e:
            self.logger.error(f"Failed to generate analytics for user {user_id}: {e}")
            raise
    
    async def _analyze_consultation_patterns(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze user consultation patterns and metrics"""
        
        # Get conversations in period
        conversations = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.started_at >= period_start,
                Conversation.started_at <= period_end
            )
        ).all()
        
        # Get messages in period
        conversation_ids = [conv.id for conv in conversations]
        messages = []
        if conversation_ids:
            messages = db.query(Message).filter(
                and_(
                    Message.conversation_id.in_(conversation_ids),
                    Message.timestamp >= period_start,
                    Message.timestamp <= period_end
                )
            ).all()
        
        # Calculate basic metrics
        consultation_count = len(conversations)
        total_messages = len(messages)
        user_messages = [m for m in messages if m.sender == 'user']
        ai_messages = [m for m in messages if m.sender == 'ai']
        
        # Calculate average consultation length
        avg_consultation_length = 0
        if conversations:
            consultation_lengths = []
            for conv in conversations:
                conv_messages = [m for m in messages if m.conversation_id == conv.id]
                consultation_lengths.append(len(conv_messages))
            avg_consultation_length = statistics.mean(consultation_lengths) if consultation_lengths else 0
        
        # Calculate average response time
        avg_response_time = 0
        if ai_messages:
            response_times = [m.response_time_ms for m in ai_messages if m.response_time_ms]
            avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Analyze consultation patterns
        consultation_patterns = self._analyze_consultation_timing_patterns(conversations)
        
        # Analyze urgency distribution
        urgency_distribution = self._analyze_urgency_distribution(conversations)
        
        return {
            "consultation_count": consultation_count,
            "total_messages": total_messages,
            "avg_consultation_length": round(avg_consultation_length, 2),
            "avg_response_time": round(avg_response_time, 2),
            "consultation_patterns": consultation_patterns,
            "urgency_distribution": urgency_distribution
        }
    
    async def _analyze_symptom_patterns(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze symptom patterns and frequency"""
        
        # Get symptom records
        symptom_records = db.query(SymptomRecord).filter(
            and_(
                SymptomRecord.user_id == user_id,
                SymptomRecord.recorded_at >= period_start,
                SymptomRecord.recorded_at <= period_end
            )
        ).all()
        
        # Get messages with symptom keywords
        conversation_ids = db.query(Conversation.id).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.started_at >= period_start,
                Conversation.started_at <= period_end
            )
        ).subquery()
        
        messages_with_symptoms = db.query(Message).filter(
            and_(
                Message.conversation_id.in_(conversation_ids),
                Message.symptom_keywords.isnot(None)
            )
        ).all()
        
        # Analyze symptom frequency
        symptom_frequency = defaultdict(int)
        symptom_severity_trends = defaultdict(list)
        
        # Process symptom records
        for record in symptom_records:
            for symptom in record.symptoms:
                symptom_name = symptom.get('name', '').lower()
                severity = symptom.get('severity', 0)
                
                symptom_frequency[symptom_name] += 1
                symptom_severity_trends[symptom_name].append({
                    'date': record.recorded_at.isoformat(),
                    'severity': severity
                })
        
        # Process message symptom keywords
        for message in messages_with_symptoms:
            if message.symptom_keywords:
                for keyword in message.symptom_keywords:
                    symptom_frequency[keyword.lower()] += 1
        
        # Calculate severity trends
        severity_trends = {}
        for symptom, severities in symptom_severity_trends.items():
            if len(severities) > 1:
                severity_values = [s['severity'] for s in severities]
                trend = self._calculate_trend(severity_values)
                severity_trends[symptom] = {
                    'trend': trend,
                    'current_avg': statistics.mean(severity_values[-3:]) if len(severity_values) >= 3 else statistics.mean(severity_values),
                    'overall_avg': statistics.mean(severity_values),
                    'data_points': len(severity_values)
                }
        
        # Identify new symptoms
        previous_period_start = period_start - timedelta(days=30)
        previous_symptoms = db.query(SymptomRecord).filter(
            and_(
                SymptomRecord.user_id == user_id,
                SymptomRecord.recorded_at >= previous_period_start,
                SymptomRecord.recorded_at < period_start
            )
        ).all()
        
        previous_symptom_names = set()
        for record in previous_symptoms:
            for symptom in record.symptoms:
                previous_symptom_names.add(symptom.get('name', '').lower())
        
        current_symptom_names = set(symptom_frequency.keys())
        new_symptoms = list(current_symptom_names - previous_symptom_names)
        
        return {
            "symptom_frequency": dict(symptom_frequency),
            "symptom_severity_trends": severity_trends,
            "new_symptoms_detected": new_symptoms,
            "total_unique_symptoms": len(symptom_frequency),
            "most_frequent_symptoms": sorted(symptom_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    async def _analyze_health_trends(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze health trends and patterns over time"""
        
        # Get historical analytics for trend comparison
        historical_analytics = db.query(HealthAnalytics).filter(
            and_(
                HealthAnalytics.user_id == user_id,
                HealthAnalytics.period_end < period_start
            )
        ).order_by(desc(HealthAnalytics.period_end)).limit(6).all()
        
        # Analyze consultation frequency trends
        consultation_trend = self._analyze_consultation_frequency_trend(db, user_id, period_start, period_end)
        
        # Analyze symptom severity trends
        symptom_trend = self._analyze_symptom_severity_trend(db, user_id, period_start, period_end)
        
        # Analyze medication adherence trends
        medication_trend = self._analyze_medication_adherence_trend(db, user_id, period_start, period_end)
        
        # Identify improving areas
        improving_areas = []
        concerning_trends = []
        stable_conditions = []
        
        # Compare with historical data
        if historical_analytics:
            latest_historical = historical_analytics[0]
            
            # Compare consultation patterns
            if hasattr(latest_historical, 'consultation_count'):
                current_consultations = consultation_trend.get('current_period_count', 0)
                historical_consultations = latest_historical.consultation_count
                
                if current_consultations < historical_consultations * 0.8:
                    improving_areas.append("Reduced need for medical consultations")
                elif current_consultations > historical_consultations * 1.2:
                    concerning_trends.append("Increased frequency of medical consultations")
                else:
                    stable_conditions.append("Stable consultation patterns")
        
        # Seasonal pattern analysis
        seasonal_patterns = self._analyze_seasonal_patterns(db, user_id)
        
        return {
            "health_trends": {
                "improving_areas": improving_areas,
                "concerning_trends": concerning_trends,
                "stable_conditions": stable_conditions,
                "seasonal_patterns": seasonal_patterns
            },
            "consultation_trend": consultation_trend,
            "symptom_trend": symptom_trend,
            "medication_trend": medication_trend
        }
    
    async def _calculate_risk_assessment(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive health risk assessment"""
        
        risk_factors = []
        protective_factors = []
        risk_score = 0.0
        
        # Get user profile
        user = db.query(User).filter(User.id == user_id).first()
        
        # Age-based risk factors
        if user and user.date_of_birth:
            age = user.get_age()
            if age and age > 65:
                risk_factors.append("Advanced age (>65)")
                risk_score += 0.1
            elif age and age > 50:
                risk_factors.append("Middle age (>50)")
                risk_score += 0.05
        
        # Medical history risk factors
        medical_records = db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.user_id == user_id,
                MedicalRecord.status == 'active'
            )
        ).all()
        
        chronic_conditions = []
        for record in medical_records:
            if record.record_type == 'diagnosis' and record.status == 'chronic':
                chronic_conditions.append(record.condition)
                risk_score += 0.15
        
        if chronic_conditions:
            risk_factors.append(f"Chronic conditions: {', '.join(chronic_conditions[:3])}")
        
        # Medication-based risk factors
        user_medications = db.query(UserMedication).filter(
            UserMedication.user_id == user_id
        ).all()
        
        if len(user_medications) > 5:
            risk_factors.append("Polypharmacy (>5 medications)")
            risk_score += 0.1
        
        # Recent emergency consultations
        emergency_conversations = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.urgency_level.in_(['emergency', 'critical']),
                Conversation.started_at >= period_start,
                Conversation.started_at <= period_end
            )
        ).count()
        
        if emergency_conversations > 0:
            risk_factors.append(f"Recent emergency consultations: {emergency_conversations}")
            risk_score += 0.2 * emergency_conversations
        
        # Protective factors
        recent_consultations = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.started_at >= period_start,
                Conversation.started_at <= period_end
            )
        ).count()
        
        if recent_consultations > 0:
            protective_factors.append("Active health monitoring")
            risk_score -= 0.05
        
        # Regular medication management
        if user_medications:
            protective_factors.append("Active medication management")
            risk_score -= 0.03
        
        # Determine risk level
        risk_level = "low"
        if risk_score > 0.5:
            risk_level = "critical"
        elif risk_score > 0.3:
            risk_level = "high"
        elif risk_score > 0.15:
            risk_level = "moderate"
        
        # Ensure risk score is between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 3),
            "risk_factors": risk_factors,
            "protective_factors": protective_factors,
            "assessment_date": datetime.now(timezone.utc).isoformat()
        }
    
    async def _generate_health_insights(
        self, 
        db: Session, 
        user_id: str, 
        analytics_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered health insights based on analytics data"""
        
        insights = []
        
        # Consultation pattern insights
        consultation_count = analytics_data.get("consultation_count", 0)
        if consultation_count > 10:
            insights.append({
                "type": "consultation_pattern",
                "priority": "medium",
                "title": "High Consultation Frequency",
                "description": f"You've had {consultation_count} consultations this period, which is above average. Consider discussing ongoing concerns with a healthcare provider.",
                "recommendation": "Schedule a comprehensive health check-up",
                "confidence": 0.8
            })
        elif consultation_count == 0:
            insights.append({
                "type": "consultation_pattern",
                "priority": "low",
                "title": "No Recent Consultations",
                "description": "You haven't had any consultations recently. Regular health check-ins can help maintain wellness.",
                "recommendation": "Consider periodic health assessments",
                "confidence": 0.6
            })
        
        # Symptom pattern insights
        symptom_frequency = analytics_data.get("symptom_frequency", {})
        if symptom_frequency:
            most_common_symptom = max(symptom_frequency.items(), key=lambda x: x[1])
            if most_common_symptom[1] > 3:
                insights.append({
                    "type": "symptom_pattern",
                    "priority": "high",
                    "title": f"Recurring Symptom: {most_common_symptom[0].title()}",
                    "description": f"You've reported '{most_common_symptom[0]}' {most_common_symptom[1]} times. Recurring symptoms may need professional evaluation.",
                    "recommendation": "Consult with a healthcare provider about persistent symptoms",
                    "confidence": 0.9
                })
        
        # Risk assessment insights
        risk_assessment = analytics_data.get("risk_assessment", {})
        risk_level = risk_assessment.get("risk_level", "low")
        
        if risk_level in ["high", "critical"]:
            insights.append({
                "type": "risk_assessment",
                "priority": "high",
                "title": f"{risk_level.title()} Health Risk Detected",
                "description": f"Your current health risk level is {risk_level}. This assessment is based on your medical history and recent health patterns.",
                "recommendation": "Schedule an appointment with your healthcare provider for comprehensive evaluation",
                "confidence": 0.85
            })
        
        # Health trend insights
        health_trends = analytics_data.get("health_trends", {})
        concerning_trends = health_trends.get("concerning_trends", [])
        
        if concerning_trends:
            insights.append({
                "type": "health_trend",
                "priority": "medium",
                "title": "Concerning Health Trends Detected",
                "description": f"We've identified some concerning patterns: {', '.join(concerning_trends[:2])}",
                "recommendation": "Monitor these trends closely and consider professional consultation",
                "confidence": 0.75
            })
        
        improving_areas = health_trends.get("improving_areas", [])
        if improving_areas:
            insights.append({
                "type": "health_trend",
                "priority": "low",
                "title": "Positive Health Improvements",
                "description": f"Great news! We've noticed improvements in: {', '.join(improving_areas[:2])}",
                "recommendation": "Continue your current health management approach",
                "confidence": 0.8
            })
        
        return insights
    
    async def _generate_personalized_recommendations(
        self, 
        db: Session, 
        user_id: str, 
        analytics_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized health recommendations based on user data"""
        
        recommendations = []
        
        # Get user profile for personalization
        user = db.query(User).filter(User.id == user_id).first()
        
        # Consultation frequency recommendations
        consultation_count = analytics_data.get("consultation_count", 0)
        if consultation_count == 0:
            recommendations.append({
                "category": "preventive_care",
                "priority": "medium",
                "title": "Regular Health Check-ins",
                "description": "Consider scheduling regular health consultations to maintain optimal wellness",
                "action_items": [
                    "Schedule annual physical exam",
                    "Set up quarterly health assessments",
                    "Monitor vital signs regularly"
                ],
                "timeline": "within_month"
            })
        
        # Symptom management recommendations
        symptom_frequency = analytics_data.get("symptom_frequency", {})
        if symptom_frequency:
            top_symptoms = sorted(symptom_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            
            recommendations.append({
                "category": "symptom_management",
                "priority": "high",
                "title": "Symptom Tracking and Management",
                "description": f"Focus on managing your most frequent symptoms: {', '.join([s[0] for s in top_symptoms])}",
                "action_items": [
                    "Keep a detailed symptom diary",
                    "Identify potential triggers",
                    "Discuss patterns with healthcare provider"
                ],
                "timeline": "immediate"
            })
        
        # Risk-based recommendations
        risk_assessment = analytics_data.get("risk_assessment", {})
        risk_factors = risk_assessment.get("risk_factors", [])
        
        if risk_factors:
            recommendations.append({
                "category": "risk_management",
                "priority": "high",
                "title": "Health Risk Mitigation",
                "description": "Address identified risk factors to improve your health outlook",
                "action_items": [
                    "Review risk factors with healthcare provider",
                    "Develop risk mitigation strategies",
                    "Implement lifestyle modifications"
                ],
                "timeline": "within_week"
            })
        
        # Lifestyle recommendations based on age and profile
        if user and user.date_of_birth:
            age = user.get_age()
            if age and age > 50:
                recommendations.append({
                    "category": "lifestyle",
                    "priority": "medium",
                    "title": "Age-Appropriate Health Maintenance",
                    "description": "Focus on health maintenance strategies appropriate for your age group",
                    "action_items": [
                        "Regular cardiovascular screening",
                        "Bone density assessment",
                        "Cancer screening as recommended",
                        "Maintain active lifestyle"
                    ],
                    "timeline": "within_quarter"
                })
        
        # Medication management recommendations
        user_medications = db.query(UserMedication).filter(
            UserMedication.user_id == user_id
        ).count()
        
        if user_medications > 3:
            recommendations.append({
                "category": "medication_management",
                "priority": "medium",
                "title": "Comprehensive Medication Review",
                "description": "Regular medication reviews can optimize treatment and reduce interactions",
                "action_items": [
                    "Schedule medication review with pharmacist",
                    "Check for drug interactions",
                    "Optimize medication timing",
                    "Review medication necessity"
                ],
                "timeline": "within_month"
            })
        
        return recommendations
    
    async def _calculate_overall_health_score(self, analytics_data: Dict[str, Any]) -> float:
        """Calculate overall health score based on analytics data"""
        
        score = 100.0  # Start with perfect score
        
        # Risk assessment impact
        risk_assessment = analytics_data.get("risk_assessment", {})
        risk_score = risk_assessment.get("risk_score", 0.0)
        score -= (risk_score * 30)  # Risk can reduce score by up to 30 points
        
        # Consultation frequency impact
        consultation_count = analytics_data.get("consultation_count", 0)
        if consultation_count > 15:
            score -= 10  # Too many consultations may indicate health issues
        elif consultation_count == 0:
            score -= 5   # No consultations may indicate neglect of health
        
        # Symptom frequency impact
        symptom_frequency = analytics_data.get("symptom_frequency", {})
        total_symptom_reports = sum(symptom_frequency.values()) if symptom_frequency else 0
        if total_symptom_reports > 20:
            score -= 15  # High symptom frequency reduces score
        
        # Health trends impact
        health_trends = analytics_data.get("health_trends", {})
        concerning_trends = health_trends.get("concerning_trends", [])
        improving_areas = health_trends.get("improving_areas", [])
        
        score -= len(concerning_trends) * 5  # Each concerning trend reduces score
        score += len(improving_areas) * 3    # Each improvement increases score
        
        # Ensure score is between 0 and 100
        score = max(0.0, min(100.0, score))
        
        return round(score, 1)
    
    def _calculate_period_boundaries(self, period_type: str) -> Tuple[datetime, datetime]:
        """Calculate period start and end dates based on period type"""
        
        now = datetime.now(timezone.utc)
        
        if period_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period_type == "weekly":
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(weeks=1)
        elif period_type == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
        elif period_type == "quarterly":
            quarter = (now.month - 1) // 3 + 1
            quarter_start_month = (quarter - 1) * 3 + 1
            period_start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            if quarter == 4:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=quarter_start_month + 3)
        elif period_type == "yearly":
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start.replace(year=now.year + 1)
        else:
            # Default to monthly
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
        
        return period_start, period_end
    
    def _analyze_consultation_timing_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze timing patterns in consultations"""
        
        if not conversations:
            return {"peak_hours": [], "consultation_types": {}, "duration_patterns": {}}
        
        # Analyze peak hours
        hours = [conv.started_at.hour for conv in conversations]
        hour_counts = Counter(hours)
        peak_hours = [hour for hour, count in hour_counts.most_common(3)]
        
        # Analyze consultation types
        consultation_types = Counter([conv.consultation_type for conv in conversations])
        
        # Analyze duration patterns
        durations = [conv.duration_minutes for conv in conversations if conv.duration_minutes]
        duration_patterns = {}
        if durations:
            duration_patterns = {
                "avg_duration": round(statistics.mean(durations), 2),
                "median_duration": round(statistics.median(durations), 2),
                "max_duration": max(durations),
                "min_duration": min(durations)
            }
        
        return {
            "peak_hours": peak_hours,
            "consultation_types": dict(consultation_types),
            "duration_patterns": duration_patterns
        }
    
    def _analyze_urgency_distribution(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze urgency level distribution"""
        
        if not conversations:
            return {}
        
        urgency_levels = [conv.urgency_level for conv in conversations if conv.urgency_level]
        urgency_counts = Counter(urgency_levels)
        
        total = len(urgency_levels)
        urgency_distribution = {}
        
        for level, count in urgency_counts.items():
            urgency_distribution[level] = {
                "count": count,
                "percentage": round((count / total) * 100, 1) if total > 0 else 0
            }
        
        return urgency_distribution
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_consultation_frequency_trend(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze consultation frequency trends"""
        
        # Get current period consultations
        current_consultations = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.started_at >= period_start,
                Conversation.started_at <= period_end
            )
        ).count()
        
        # Get previous period for comparison
        period_duration = period_end - period_start
        previous_start = period_start - period_duration
        previous_end = period_start
        
        previous_consultations = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.started_at >= previous_start,
                Conversation.started_at < previous_end
            )
        ).count()
        
        # Calculate trend
        trend = "stable"
        change_percentage = 0
        
        if previous_consultations > 0:
            change_percentage = ((current_consultations - previous_consultations) / previous_consultations) * 100
            
            if change_percentage > 20:
                trend = "increasing"
            elif change_percentage < -20:
                trend = "decreasing"
        elif current_consultations > 0:
            trend = "increasing"
            change_percentage = 100
        
        return {
            "current_period_count": current_consultations,
            "previous_period_count": previous_consultations,
            "trend": trend,
            "change_percentage": round(change_percentage, 1)
        }
    
    def _analyze_symptom_severity_trend(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze symptom severity trends"""
        
        # Get symptom records with severity data
        symptom_records = db.query(SymptomRecord).filter(
            and_(
                SymptomRecord.user_id == user_id,
                SymptomRecord.recorded_at >= period_start,
                SymptomRecord.recorded_at <= period_end
            )
        ).order_by(SymptomRecord.recorded_at).all()
        
        if not symptom_records:
            return {"trend": "no_data", "average_severity": 0}
        
        # Extract severity values
        severity_values = []
        for record in symptom_records:
            for symptom in record.symptoms:
                severity = symptom.get('severity', 0)
                if severity > 0:
                    severity_values.append(severity)
        
        if not severity_values:
            return {"trend": "no_data", "average_severity": 0}
        
        # Calculate trend
        trend = self._calculate_trend(severity_values)
        average_severity = statistics.mean(severity_values)
        
        return {
            "trend": trend,
            "average_severity": round(average_severity, 2),
            "severity_range": {
                "min": min(severity_values),
                "max": max(severity_values)
            },
            "data_points": len(severity_values)
        }
    
    def _analyze_medication_adherence_trend(
        self, 
        db: Session, 
        user_id: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze medication adherence trends"""
        
        # Get user medications
        user_medications = db.query(UserMedication).filter(
            UserMedication.user_id == user_id
        ).all()
        
        if not user_medications:
            return {"trend": "no_medications", "adherence_score": 0}
        
        # For now, return basic medication info
        # In a full implementation, this would analyze adherence patterns
        # from medication logs, reminders, and user reports
        
        return {
            "trend": "stable",
            "adherence_score": 85,  # Placeholder
            "total_medications": len(user_medications),
            "note": "Medication adherence tracking requires additional implementation"
        }
    
    def _analyze_seasonal_patterns(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Analyze seasonal health patterns"""
        
        # Get historical data for seasonal analysis
        one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
        
        conversations = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.started_at >= one_year_ago
            )
        ).all()
        
        if not conversations:
            return {}
        
        # Group by season
        seasonal_data = {"spring": 0, "summer": 0, "fall": 0, "winter": 0}
        
        for conv in conversations:
            month = conv.started_at.month
            if month in [3, 4, 5]:
                seasonal_data["spring"] += 1
            elif month in [6, 7, 8]:
                seasonal_data["summer"] += 1
            elif month in [9, 10, 11]:
                seasonal_data["fall"] += 1
            else:
                seasonal_data["winter"] += 1
        
        # Find peak season
        peak_season = max(seasonal_data.items(), key=lambda x: x[1])
        
        return {
            "seasonal_consultation_counts": seasonal_data,
            "peak_season": peak_season[0],
            "peak_season_count": peak_season[1]
        }


# Global analytics engine instance
health_analytics_engine = HealthAnalyticsEngine()