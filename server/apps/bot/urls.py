from django.urls import include, path

from .views import WebhookView

app_name = 'telegram-bot'

urlpatterns = [
    path('telegram/webhook/<str:token>/', WebhookView.as_view(), name='webhook')
]
