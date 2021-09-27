import os
from unittest import mock
from django.test import TestCase
from openapi_core import create_spec
from django.http import HttpResponse, HttpRequest
from drf_open_api_validator.middleware import DjangoOpenAPIRequestValidationMiddleware
import yaml
from openapi_core import create_spec
from rest_framework.test import APIRequestFactory


HERE = os.path.dirname(os.path.abspath(__file__))


def load_spec(path):
    with open(path, "rb") as fp:
        return create_spec(yaml.safe_load(fp))


class OneTest(TestCase):
    def setUp(self):
        self.request_factory = APIRequestFactory()

    def test_success(self):
        req = self.request_factory.post(
            "/pets",
            {"name": "foo"},
            format="json",
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
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
            resp = middleware(req)
            self.assertEqual(resp.status_code, 200)

    def test_failed_to_craete_openapi_request(self):
        """Ignore the error if you can't create an OpenAPI request."""
        resp = HttpResponse(
            content_type="application/json",
            status=200,
        )
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
            resp = middleware(None)
            self.assertEqual(resp.status_code, 200)  # ingore error

    def test_url_path_not_found(self):
        """Error without a path."""
        req = self.request_factory.post("/NOTFOUND")
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
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

            resp = middleware(req)
            self.assertEqual(resp.status_code, 404)

    def test_url_path_not_found_ignore(self):
        """If OPENAPI_STRICT_PATH is false, no error will occur even if the path is missing."""
        req = self.request_factory.post("/NOTFOUND", {"name": "foo"}, format="json")
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=True,
            OPENAPI_STRICT_RESPONSE_SCHEMA=True,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )

            resp = middleware(req)
            self.assertEqual(resp.status_code, 200)  # ingore error

    def test_request_unknown_error(self):
        req = self.request_factory.post("/pets", {"name": "foo"}, format="json")
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
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

            with mock.patch.object(
                middleware.request_validator, "validate", side_effect=ValueError
            ):

                with self.assertRaises(ValueError):
                    middleware(req)

    def test_request_unknown_error_ignore(self):
        req = self.request_factory.post("/pets", {"name": "foo"}, format="json")
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=True,
            OPENAPI_STRICT_RESPONSE_SCHEMA=True,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )

            with mock.patch.object(
                middleware.request_validator, "validate", side_effect=ValueError
            ):
                resp = middleware(req)
                self.assertEqual(resp.status_code, 200)  # ingore error

    def test_request_validate_error(self):
        req = self.request_factory.post(
            "/pets", {"BAD_SCHEMA": "TESTING"}, format="json"
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=True,
            OPENAPI_STRICT_RESPONSE_SCHEMA=True,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )
            resp = middleware(req)
            self.assertEqual(resp.status_code, 400)  # ingore error

    def test_request_validate_error_ignore(self):
        req = self.request_factory.post(
            "/pets", {"BAD_SCHEMA": "TESTING"}, format="json"
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"message": "OK"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=False,
            OPENAPI_STRICT_RESPONSE_SCHEMA=True,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )
            resp = middleware(req)
            self.assertEqual(resp.status_code, 200)  # ingore error

    def test_response_validate_error(self):
        req = self.request_factory.post(
            "/pets", {"BAD_SCHEMA": "TESTING"}, format="json"
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"BAD SCHEMA": "NG"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=False,
            OPENAPI_STRICT_RESPONSE_SCHEMA=True,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )
            resp = middleware(req)
            self.assertEqual(resp.status_code, 500)

    def test_response_validate_error_ignore(self):
        req = self.request_factory.post(
            "/pets", {"BAD_SCHEMA": "TESTING"}, format="json"
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"BAD SCHEMA": "NG"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=False,
            OPENAPI_STRICT_RESPONSE_SCHEMA=False,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )
            resp = middleware(req)
            self.assertEqual(resp.status_code, 200)

    def test_response_unknown_error(self):
        req = self.request_factory.post(
            "/pets", {"BAD_SCHEMA": "TESTING"}, format="json"
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"BAD SCHEMA": "NG"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=False,
            OPENAPI_STRICT_RESPONSE_SCHEMA=True,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )

            with mock.patch.object(
                middleware.response_validator, "validate", side_effect=ValueError
            ):
                with self.assertRaises(ValueError):
                    resp = middleware(req)

    def test_response_unknown_error_ignore(self):
        req = self.request_factory.post(
            "/pets", {"BAD_SCHEMA": "TESTING"}, format="json"
        )
        resp = HttpResponse(
            content_type="application/json",
            status=200,
            content=b'{"BAD SCHEMA": "NG"}',
        )
        spec = load_spec(os.path.join(HERE, "openapi.yaml"))

        with self.settings(
            OPENAPI_SPEC=spec,
            OPENAPI_STRICT_PATH=False,
            OPENAPI_STRICT_REQUEST_SCHEMA=False,
            OPENAPI_STRICT_RESPONSE_SCHEMA=False,
        ):
            middleware = DjangoOpenAPIRequestValidationMiddleware(
                get_response=mock.MagicMock(return_value=resp)
            )

            with mock.patch.object(
                middleware.response_validator, "validate", side_effect=ValueError
            ):
                resp = middleware(req)
            self.assertEqual(resp.status_code, 200)
