from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Create a superuser with the user role set to admin'

    def handle(self, *args, **options):
        username = input("Enter admin username: ")
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")

        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        admin_user.user_role = 'admin'
        admin_user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user {admin_user.username}'))
