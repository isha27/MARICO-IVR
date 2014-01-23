from django.core.management.base import NoArgsCommand
from optparse import make_option
import time
import logging

class Command(NoArgsCommand):

    help = "Describe AutoDial Commands"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
    )

    def handle_noargs(self, **options):
        logging.basicConfig(format='[%(asctime)s] %(levelno)s' \
                '(%(process)d) %(module)s: %(message)s', level=logging.DEBUG)
        logging.debug("Starting AutoDial Daemon...")
        logging.warning("AutoDial Daemon is running...")
        logging.warning("Quit the daemon with CONTROL-C")
        from api import newautodial
        newautodial.exec_autodial()

