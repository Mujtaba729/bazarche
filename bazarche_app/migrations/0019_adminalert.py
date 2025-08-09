from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('bazarche_app', '0018_product_condition'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_last_hour', models.PositiveIntegerField(default=0, verbose_name='تعداد 1 ساعت اخیر')),
                ('count_last_day', models.PositiveIntegerField(default=0, verbose_name='تعداد 24 ساعت اخیر')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')),
                ('note', models.CharField(blank=True, max_length=255, verbose_name='توضیح')),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='admin_alerts', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'هشدار مدیریتی',
                'verbose_name_plural': 'هشدارهای مدیریتی',
                'ordering': ['-created_at'],
            },
        ),
    ]


