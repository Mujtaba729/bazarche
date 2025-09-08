from django.core.management.base import BaseCommand
from bazarche_app.models import MainCategory

class Command(BaseCommand):
    help = 'Check if main categories exist'

    def handle(self, *args, **kwargs):
        categories = MainCategory.objects.all()
        self.stdout.write(f'Total MainCategory objects: {categories.count()}')
        
        if categories.exists():
            for category in categories:
                self.stdout.write(f'- {category.name_fa} (ID: {category.id})')
        else:
            self.stdout.write('No MainCategory objects found!')
            
        # Also check if we have any Category objects
        from bazarche_app.models import Category
        regular_categories = Category.objects.all()
        self.stdout.write(f'Total Category objects: {regular_categories.count()}')
        
        if regular_categories.exists():
            for category in regular_categories:
                self.stdout.write(f'- {category.name_fa} (ID: {category.id})')
