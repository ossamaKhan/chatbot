import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbot_packages.settings")  # Make sure this path is correct

application = get_wsgi_application()
app = application