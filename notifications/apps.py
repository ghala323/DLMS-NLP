from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from documents.death_verification import check_expired_verifications
        from notifications.scheduler import run_inactivity_check
        import logging

        logger = logging.getLogger('notifications.apps')

        scheduler = BackgroundScheduler()

        scheduler.add_job(
            run_inactivity_check,
            trigger=CronTrigger(hour=9, minute=0),
            id='inactivity_check',
            name='Daily Inactivity Check',
            replace_existing=True
        )

        scheduler.add_job(
            check_expired_verifications,
            trigger=CronTrigger(hour='*/6'),
            id='expired_verifications',
            name='Check Expired Verifications',
            replace_existing=True
        )

        scheduler.start()
        logger.info('Scheduler started successfully')
