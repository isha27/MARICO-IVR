from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import requires_csrf_token
import requests 
from django.template import RequestContext
from django.shortcuts import render_to_response
import json
from .models import maricodata 


@csrf_exempt
def data_upload(request ) :
  print "REQUEST IS :" + request.method

  if request.method == 'GET' :  
    return HttpResponse( "MARICO IVR SYSTEM")
  
  if request.method == 'POST':
   
   try:
       catch = json.loads(request.raw_post_data)['data']
   except:
       return HttpResponse(json.dumps({"response": "Error : Invalid data"}))
   for k in catch:
       Log=maricodata()
       for key,val in k.items():
         setattr(Log,key,val)
         Log.save()
   return HttpResponse(json.dumps({"response": "Successfully Saved"}))
   
