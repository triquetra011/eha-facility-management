#!/usr/bin/env python

__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'


import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehafm.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
