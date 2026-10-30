from django.apps import AppConfig


class UsersConfig(AppConfig):
    defualt_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals