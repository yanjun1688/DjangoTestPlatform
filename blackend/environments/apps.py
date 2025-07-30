from django.apps import AppConfig


class EnvironmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'environments'
    verbose_name = '环境管理'