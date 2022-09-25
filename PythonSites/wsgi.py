"""
WSGI config for PythonSites project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import site
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.abspath(Path(__file__).resolve()))

root = os.path.abspath(Path(__file__).resolve().parent.parent)
sys.path.insert(0, root)

packages = os.path.join(root,
                        'venvsites/lib/python3.9/site-packages')
sys.path.insert(0, packages)
site.addsitedir(packages)

activate_this = os.path.join(root,
                             'venvsites/bin/activate_this.py')
exec(open(activate_this).read())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PythonSites.settings')
# os.environ["DJANGO_SETTINGS_MODULE"] = "{{ project_name }}.settings"

application = get_wsgi_application()
