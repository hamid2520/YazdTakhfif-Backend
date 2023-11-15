from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'src.users'
    verbose_name = "مدیریت کاربران"

    # actstream register model
    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('User'))
