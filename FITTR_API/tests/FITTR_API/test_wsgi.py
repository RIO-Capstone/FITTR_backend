import os
import pytest
from django.core.wsgi import get_wsgi_application
from unittest.mock import patch

@pytest.mark.django_db
def test_wsgi_application():
    """
    Test that the WSGI application loads correctly.
    """
    with patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "FITTR_API.settings"}):
        application = get_wsgi_application()
        assert application is not None
