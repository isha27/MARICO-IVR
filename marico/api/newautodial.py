import re
import time
import uuid
import logging
import psycopg2
import socket

from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import utc
from xmlrpclib import ServerProxy
from django.db import transaction
from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.ram_store import RAMJobStore
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore
from django import db
from django.db.models import Max
from string import Template

from .models import maricodata

db_set = settings.DATABASES['default']

sched = Scheduler()

SERVER = ServerProxy("http://freeswitch:works@localhost:8080")


@transaction.autocommit
def num_fetch(maricodata, count):
    """Return list of numbers
    Takes campaign and total count of numbers to fetch from DB to dial call.
    """
    """
    phonebooks = campaign.phonebooks.filter(enabled__lte=
            datetime.utcnow().replace(tzinfo=utc))
    for phonebook in phonebooks:
        contacts = phonebook.contacts.filter(status=False).distinct(
                'numeric')[0:count]
        if (contacts.count() > 0):
            numbers_tup = contacts.values_list('numeric','first_name',
                    'last_name','description','info')
            numbers_list = map(list, numbers_tup)
            for num in numbers_list:
                num.insert(0, phonebook.id)
            return numbers_list
    return []
    """
    data = maricodata.objects.filter(dialled = False).distinct('retailercode')
    if (data.count()>0):
      print "ISHAAAAAAAAAAAAA" + str(data.count())
      numbers = data.values_list('retailercode','phone')
      numbers_list = map(list ,numbers)
      print numbers_list
      return numbers_list  
    return []


def fs_call():
    """
    This function is use to schedule dial process recursively.
    """
    try :
        fsdial(maricodata)
    except (NameError, psycopg2.OperationalError, psycopg2.InterfaceError):
        print "Postgres server not loaded"


@transaction.autocommit
def fsdial(maricodata):
    try:
          ftdm_down_state = SERVER.freeswitch.api('ftdm', 'core state DOWN')
          ftdm_state_split = ftdm_down_state.splitlines()
          ftdm_down_count = int(ftdm_state_split[-1].split()[-1])
          for j in ftdm_state_split[0:-2]:
              if j.find("c16") != -1:
                  ftdm_down_count = ftdm_down_count - 31
    except socket.error, v:
          print "RPC Error %s: Freeswitch RPC module may not be" \
                "loaded or properly configured" % v[0]
          return None
    except:
          ftdm_down_count = 0
          print "FreeTDM Module may not be loaded"
          try:
              SERVER.freeswitch.api("load", "mod_freetdm")
          except socket.error, v:
              print "RPC Error %s: Freeswitch RPC module may not be" \
                    " loaded or properly configured" % v[0]

    count = ftdm_down_count
    print "Channel Available %s" % (ftdm_down_count)
    numbers = num_fetch(maricodata, count)
    for num in numbers:
        try:
            fs_originate = "originate ........"      # TODO
            #fs_originate_str = fs_originate + num + space + ivr extn
            print num[1]
            fs_originate_str = "originate {ignore_early_media=true}freetdm/g0/a/"+num[1]+" "+"23456"
            print fs_originate_str
            maricodata.objects.filter(phone=num[1]).update(dialled = True)
            ##obj.dialled=True
            SERVER.freeswitch.api("bgapi", fs_originate_str)
        except socket.error, v:
            print "RPC Error %s: Freeswitch RPC module or Redis may not be" \
                  "loaded or properly configured" % v[0]
            return None


def exec_autodial():
    """
    Start APSchedular for autodialing.
    """
    global ENABLE
    sched.add_jobstore(RAMJobStore(), 'list')
    execution_time = datetime.now() + timedelta(minutes=0.1)
    sched.add_interval_job(fs_call, seconds=10, start_date=execution_time,
                           name='calls', jobstore='list')
    logging.info('START:', time.time())
    sched.configure(daemonic=False)
    sched.start()
    #sched._thread.join()


if __name__ == '__main__':
    exec_autodial()

