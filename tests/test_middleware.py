import os
from unittest import mock
from django.test import TestCase
from openapi_core import create_spec
from django.http import HttpResponse, HttpRequest
from drf_open_api_validator.middleware import DjangoOpenAPIRequestValidationMiddleware
import yaml
from openapi_core import create_spec

HERE = os.path.dirname(os.path.abspath(__file__))


def load_spec(path):
    with open(path, "rb") as fp:
        return create_spec(yaml.safe_load(fp))


class OneTest(TestCase):
    def test_it(self):
        req = HttpRequest()
        resp = HttpResponse()
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
                OPENAPI_SPEC=spec,
                OPENAPI_STRICT_PATH=True,
                OPENAPI_STRICT_REQUEST_SCHEMA=True,
                OPENAPI_STRICT_RESPONSE_SCHEMA=True,

        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )
            middleware(req)
