"""
Data Cleanup Service
Handles automated data retention and cleanup based on user privacy settings
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db
from models import User, Conversation, Message, MedicalRecord
from encryption_service import (
    data_retention_service, audit_logger, privacy_control_service
)

class DataCleanupService:
    """Service for automated data cleanup and retention management"""
    
    def __init__(self):
        self.cleanup_interval = timedelta(hours=24)  # Run daily
        self.last_cleanup = None
        self.is_running = False
    
    async def start_cleanup_scheduler(self):
        """Start the automated cleanup scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        print("🧹 Starting data cleanup scheduler...")
        
        while self.is_running:
            try:
                await self.run_cleanup_cycle()
                await asyncio.sleep(self.cleanup_interval.total_seconds())
            except Exception as e:
                print(f"❌ Error in cleanup scheduler: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    def stop_cleanup_scheduler(self):
        """Stop the automated cleanup scheduler"""
        self.is_running = False
        print("🛑 Stopped data cleanup scheduler")
    
    async def run_cleanup_cycle(self):
        """Run a complete cleanup cycle"""
        print("🧹 Starting data cleanup cycle...")
        
        try:
            db = next(get_db())
            
            # Get all active users
            users = db.query(User).filter(User.is_active == True).all()
            
            cleanup_stats = {
                'users_processed': 0,
                'conversations_deleted': 0,
                'messages_deleted': 0,
                'medical_records_deleted': 0,
                'users_notified': 0
            }
            
            for user in users:
                try:
                    user_stats = await self.cleanup_user_data(db, user)
                    
                    # Update overall stats
                    for key, value in user_stats.items():
                        cleanup_stats[key] = cleanup_stats.get(key, 0) + value
                    
                    cleanup_stats['users_processed'] += 1
                    
                except Exception as e:
                    print(f"❌ Error cleaning up data for user {user.email}: {e}")
                    audit_logger.log_access(
                        user_id=user.firebase_uid,
                        resource="data_cleanup",
                        action="cleanup_error",
                        success=False,
                        details={'error': str(e)}
                    )
            
            self.last_cleanup = datetime.utcnow()
            
            print(f"✅ Data cleanup cycle completed: {cleanup_stats}")
            
            # Log cleanup summary
            audit_logger.log_access(
                user_id="system",
                resource="data_cleanup",
                action="cleanup_cycle_completed",
                success=True,
                details=cleanup_stats
            )
            
            db.close()
            
        except Exception as e:
            print(f"❌ Error in cleanup cycle: {e}")
            audit_logger.log_access(
                user_id="system",
                resource="data_cleanup",
                action="cleanup_cycle_error",
                success=False,
                details={'error': str(e)}
            )
    
    async def cleanup_user_data(self, db: Session, user: User) -> Dict[str, int]:
        """Clean up data for a specific user based on their retention policy"""
        stats = {
            'conversations_deleted': 0,
            'messages_deleted': 0,
            'medical_records_deleted': 0,
            'users_notified': 0
        }
        
        try:
            # Get user's data retention policy
            retention_policy = user.get_data_retention_period()
            retention_period = data_retention_service.get_retention_period(retention_policy)
            
            if retention_period is None:  # Indefinite retention
                return stats
            
            cutoff_date = datetime.utcnow() - retention_period
            
            # Clean up conversations and messages
            old_conversations = db.query(Conversation).filter(
                and_(
                    Conversation.user_id == user.id,
                    Conversation.created_at < cutoff_date
                )
            ).all()
            
            for conversation in old_conversations:
                # Count messages before deletion
                message_count = db.query(Message).filter(
                    Message.conversation_id == conversation.id
                ).count()
                
                # Delete conversation (messages will be deleted by cascade)
                db.delete(conversation)
                
                stats['conversations_deleted'] += 1
                stats['messages_deleted'] += message_count
            
            # Clean up old medical records (if user allows)
            medical_retention_years = user.get_privacy_setting('data_retention.medical_record_retention_years', 7)
            medical_cutoff_date = datetime.utcnow() - timedelta(days=medical_retention_years * 365)
            
            old_medical_records = db.query(MedicalRecord).filter(
                and_(
                    MedicalRecord.user_id == user.id,
                    MedicalRecord.date_recorded < medical_cutoff_date
                )
            ).all()
            
            for record in old_medical_records:
                db.delete(record)
                stats['medical_records_deleted'] += 1
            
            # Commit deletions
            if stats['conversations_deleted'] > 0 or stats['medical_records_deleted'] > 0:
                db.commit()
                
                # Log cleanup for this user
                audit_logger.log_data_access(
                    user_id=user.firebase_uid,
                    data_type="retention_cleanup",
                    operation="delete",
                    record_count=stats['conversations_deleted'] + stats['medical_records_deleted']
                )
                
                print(f"🧹 Cleaned up data for {user.email}: {stats}")
            
            # Check if user should be notified about upcoming data expiry
            await self.check_data_expiry_notifications(db, user)
            
        except Exception as e:
            print(f"❌ Error cleaning up user data: {e}")
            db.rollback()
            raise
        
        return stats
    
    async def check_data_expiry_notifications(self, db: Session, user: User):
        """Check if user should be notified about upcoming data expiry"""
        try:
            retention_policy = user.get_data_retention_period()
            retention_period = data_retention_service.get_retention_period(retention_policy)
            
            if retention_period is None:  # Indefinite retention
                return
            
            # Check for data that will expire in 30 days
            warning_date = datetime.utcnow() - retention_period + timedelta(days=30)
            
            conversations_expiring = db.query(Conversation).filter(
                and_(
                    Conversation.user_id == user.id,
                    Conversation.created_at < warning_date,
                    Conversation.created_at >= datetime.utcnow() - retention_period
                )
            ).count()
            
            if conversations_expiring > 0:
                # In a real implementation, this would send an email/notification
                print(f"📧 User {user.email} has {conversations_expiring} conversations expiring in 30 days")
                
                audit_logger.log_access(
                    user_id=user.firebase_uid,
                    resource="data_expiry_notification",
                    action="notification_sent",
                    success=True,
                    details={
                        'conversations_expiring': conversations_expiring,
                        'retention_policy': retention_policy
                    }
                )
        
        except Exception as e:
            print(f"❌ Error checking data expiry notifications: {e}")
    
    async def cleanup_inactive_users(self, db: Session, inactive_days: int = 365):
        """Clean up data for users who have been inactive for a long time"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=inactive_days)
            
            inactive_users = db.query(User).filter(
                or_(
                    User.last_login < cutoff_date,
                    and_(User.last_login.is_(None), User.created_at < cutoff_date)
                ),
                User.is_active == True
            ).all()
            
            for user in inactive_users:
                # Deactivate user instead of deleting
                user.is_active = False
                user.deactivated_at = datetime.utcnow()
                
                audit_logger.log_access(
                    user_id=user.firebase_uid,
                    resource="user_account",
                    action="auto_deactivated",
                    success=True,
                    details={
                        'reason': 'inactive',
                        'inactive_days': inactive_days,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    }
                )
            
            db.commit()
            
            if inactive_users:
                print(f"🔒 Deactivated {len(inactive_users)} inactive user accounts")
        
        except Exception as e:
            print(f"❌ Error cleaning up inactive users: {e}")
            db.rollback()
    
    async def anonymize_research_data(self, db: Session):
        """Create anonymized datasets for research purposes"""
        try:
            # Get users who have consented to research data sharing
            research_users = db.query(User).filter(
                User.is_active == True
            ).all()
            
            research_consented = [
                user for user in research_users 
                if user.can_share_for_research()
            ]
            
            if not research_consented:
                return
            
            anonymized_data = []
            
            for user in research_consented:
                anonymized_user = user.anonymize_for_research()
                if anonymized_user:
                    anonymized_data.append(anonymized_user)
            
            # In a real implementation, this would save to a research database
            print(f"📊 Generated anonymized research data for {len(anonymized_data)} users")
            
            audit_logger.log_access(
                user_id="system",
                resource="research_data",
                action="anonymization_completed",
                success=True,
                details={
                    'users_anonymized': len(anonymized_data),
                    'total_research_users': len(research_consented)
                }
            )
        
        except Exception as e:
            print(f"❌ Error anonymizing research data: {e}")
    
    async def generate_privacy_report(self, db: Session) -> Dict[str, Any]:
        """Generate a privacy compliance report"""
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Count users by retention policy
            retention_stats = {}
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                policy = user.get_data_retention_period()
                retention_stats[policy] = retention_stats.get(policy, 0) + 1
            
            # Count users who have consented to research
            research_consent_count = sum(
                1 for user in users if user.can_share_for_research()
            )
            
            # Count users with analytics enabled
            analytics_enabled_count = sum(
                1 for user in users if user.can_use_for_analytics()
            )
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'total_users': total_users,
                'active_users': active_users,
                'retention_policy_distribution': retention_stats,
                'research_consent_rate': research_consent_count / active_users if active_users > 0 else 0,
                'analytics_consent_rate': analytics_enabled_count / active_users if active_users > 0 else 0,
                'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None
            }
            
            print(f"📋 Generated privacy compliance report: {report}")
            
            return report
        
        except Exception as e:
            print(f"❌ Error generating privacy report: {e}")
            return {}

# Global cleanup service instance
data_cleanup_service = DataCleanupService()

# Utility functions
async def start_data_cleanup():
    """Start the data cleanup service"""
    await data_cleanup_service.start_cleanup_scheduler()

def stop_data_cleanup():
    """Stop the data cleanup service"""
    data_cleanup_service.stop_cleanup_scheduler()

async def run_manual_cleanup():
    """Run a manual cleanup cycle"""
    await data_cleanup_service.run_cleanup_cycle()