from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .registry import registry
from .services.webhook import process_webhook_event

__all__ = (
    'WebhookView',
)


class WebhookView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        token: str = kwargs['token']
        dispatcher = registry.get_descriptor(token)
        print('Dispatcher:', dispatcher)
        dispatcher = process_webhook_event(
            token=kwargs['token'],
            request_body=request.data,
            dispatcher=dispatcher
        )
        registry.register(dispatcher)
        return Response()
