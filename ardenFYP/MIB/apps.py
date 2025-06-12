from django.apps import AppConfig


class MibConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MIB'
class MibConfig(AppConfig):  
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MIB'

    def ready(self):
        import MIB.signals 