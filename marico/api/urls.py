from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
             (r'^marico/upload_data/$','api.views.data_upload'),
             ##(r'^marico/try/','api.views.try'),
)
