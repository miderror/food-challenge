from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = "backend.core.admin.MyAdminSite"

    def ready(self):
        super().ready()

        from django.contrib import admin

        try:
            from django_celery_beat.models import (
                ClockedSchedule,
                CrontabSchedule,
                IntervalSchedule,
                PeriodicTask,
                SolarSchedule,
            )

            admin.site.unregister(PeriodicTask)
            admin.site.unregister(IntervalSchedule)
            admin.site.unregister(CrontabSchedule)
            admin.site.unregister(SolarSchedule)
            admin.site.unregister(ClockedSchedule)
        except (ImportError, admin.sites.NotRegistered):
            pass
