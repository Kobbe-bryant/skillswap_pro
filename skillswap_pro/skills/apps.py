from django.apps import AppConfig


class SkillsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skills'
    verbose_name = 'Skills'

    def ready(self):
        import skills.signals
