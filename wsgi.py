"""
WSGI config for example.com project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://websitemixer.com
"""

from __future__ import absolute_import
from websitemixer import create_app

application = create_app()
