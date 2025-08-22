import logging
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from django.apps import apps

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def load_initial_data(sender, **kwargs):
    """
    Load initial data for all apps after migration
    """    
    # Dictionary mapping app names to their initial data loading commands
    initial_data_commands = {
        'apps.common': ['load_countries', 'load_regions']
    }

    app_name = sender.name

    if app_name in initial_data_commands:
        for command in initial_data_commands[app_name]:
            try:
                call_command(command)
            except Exception as e:
                logger.error(f"Error loading initial data for {app_name} using command {command}: {str(e)}") 