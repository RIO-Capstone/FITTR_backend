import os
import pytest
from unittest.mock import patch
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

@pytest.mark.django_db
def test_asgi_application():
    """
    Test that the ASGI application loads correctly.
    """
    with patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "FITTR_API.settings"}):
        application = get_asgi_application()
        assert application is not None

# def test_websocket_routing():
#     """
#     Test that the WebSocket routing is correctly included in the ASGI application.
#     """
#     from FITTR_API.asgi import application
#     assert isinstance(application, ProtocolTypeRouter)
#     assert "websocket" in application.application_mapping
#     assert isinstance(application.application_mapping["websocket"], AuthMiddlewareStack)
#     assert isinstance(application.application_mapping["websocket"].inner, URLRouter)
