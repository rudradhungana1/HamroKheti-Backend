from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None,password=None):
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.user_role = 'admin'
        user.save(using=self._db)
        return user
