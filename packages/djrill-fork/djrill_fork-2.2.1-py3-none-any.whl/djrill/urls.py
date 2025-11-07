from django.urls import re_path

from .views import DjrillWebhookView


urlpatterns = [
    re_path(r'^webhook/$', DjrillWebhookView.as_view(), name='djrill_webhook'),
]
