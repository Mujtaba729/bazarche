from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bazarche_app.models import UserFeedback, Product

class Command(BaseCommand):
    help = 'Test notification system'

    def handle(self, *args, **options):
        # Check if we have users
        users = User.objects.filter(is_active=True)
        self.stdout.write(f"Active users: {users.count()}")
        
        # Check if we have products
        products = Product.objects.filter(is_approved=True)
        self.stdout.write(f"Approved products: {products.count()}")
        
        # Check notifications
        notifications = UserFeedback.objects.filter(subject__startswith="NOTIFICATION_")
        self.stdout.write(f"Total notifications: {notifications.count()}")
        
        # Check unread notifications
        unread_notifications = UserFeedback.objects.filter(
            subject__startswith="NOTIFICATION_",
            is_read=False
        )
        self.stdout.write(f"Unread notifications: {unread_notifications.count()}")
        
        # Show recent notifications
        recent_notifications = notifications.order_by('-timestamp')[:5]
        self.stdout.write("\nRecent notifications:")
        for notif in recent_notifications:
            self.stdout.write(f"- {notif.user.username}: {notif.subject} - {notif.message[:50]}...")
        
        # Test creating a notification
        if users.exists() and products.exists():
            user = users.first()
            product = products.first()
            
            # Create test notification
            test_notification = UserFeedback.objects.create(
                email=user.email or user.username,
                subject="NOTIFICATION_TEST_123",
                message=f"تست اعلان برای محصول {product.name_fa}",
                user=user
            )
            
            self.stdout.write(f"\nCreated test notification: {test_notification.id}")
            self.stdout.write("Test completed successfully!")
        else:
            self.stdout.write("No users or products found for testing")
