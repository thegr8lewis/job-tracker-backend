"""
ASGI config for jobtracker project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobtracker.settings')

# application = get_asgi_application()



import os
import sys
from django.core.asgi import get_asgi_application

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set the correct settings module based on environment
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    # Production/Render environment
    settings_module = 'config.settings'
else:
    # Local development
    settings_module = 'config.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
application = get_asgi_application()