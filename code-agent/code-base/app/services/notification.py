"""
Notification service for real-time updates
"""

import redis
import json
from typing import Dict, Any, Optional
from app.core.config import settings


class NotificationService:
    """Notification service for real-time updates"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def publish_notification(
        self,
        channel: str,
        message: Dict[str, Any]
    ) -> bool:
        """Publish notification to Redis channel"""
        try:
            self.redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            print(f"Failed to publish notification: {e}")
            return False
    
    def notify_order_update(self, user_id: int, order_id: int, status: str) -> bool:
        """Notify user about order status update"""
        message = {
            "type": "order_update",
            "user_id": user_id,
            "order_id": order_id,
            "status": status,
            "timestamp": str(datetime.utcnow())
        }
        return self.publish_notification(f"user:{user_id}:notifications", message)
    
    def notify_stock_update(self, product_id: int, new_stock: int) -> bool:
        """Notify about product stock update"""
        message = {
            "type": "stock_update",
            "product_id": product_id,
            "new_stock": new_stock,
            "timestamp": str(datetime.utcnow())
        }
        return self.publish_notification("product:stock_updates", message)
    
    def notify_system_alert(self, alert_type: str, message: str) -> bool:
        """Notify system administrators about alerts"""
        alert_message = {
            "type": "system_alert",
            "alert_type": alert_type,
            "message": message,
            "timestamp": str(datetime.utcnow())
        }
        return self.publish_notification("system:alerts", alert_message)


# Global notification service instance
notification_service = NotificationService()
