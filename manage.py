#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import colorama

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodbankmanagement.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    colorama.init()
    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + "Database connection successful" + colorama.Style.RESET_ALL)


    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
