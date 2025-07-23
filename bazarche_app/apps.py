from django.apps import AppConfig

class BazarcheAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bazarche_app'

    def ready(self):
        """ثبت signals وقتی اپلیکیشن آماده می‌شه"""
        import bazarche_app.signals 