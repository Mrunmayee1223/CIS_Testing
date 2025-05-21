# api/management/commands/check_tasks.py
from django.core.management.base import BaseCommand
from api.models import CustomUser, Task
from django.utils.timezone import now, timedelta

class Command(BaseCommand):
    help = 'Deactivate users with 5+ missed tasks in last 7 days'

    def handle(self, *args, **kwargs):
        week_ago = now() - timedelta(days=7)
        for user in CustomUser.objects.filter(role='user', is_active=True):
            missed_count = Task.objects.filter(assigned_to=user, missed=True, deadline__gte=week_ago).count()
            if missed_count >= 5:
                user.is_active = False
                user.save()
                self.stdout.write(f'User {user.username} deactivated.')
