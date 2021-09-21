import logging

import django
from django.conf import settings
from django.http import HttpRequest, JsonResponse

from openapi_core.contrib.django.requests import DjangoOpenAPIRequestFactory
from openapi_core.contrib.django.responses import DjangoOpenAPIResponseFactory
from openapi_core.templating.paths.exceptions import (OperationNotFound,
                                                      PathNotFound,
                                                      ServerNotFound)
from openapi_core.templating.paths.finders import PathFinder
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator

logger = logging.getLogger(__name__)


class DjangoOpenAPIRequestValidationMiddleware:
    def __init__(self, get_response):
        self.request_factory = DjangoOpenAPIRequestFactory()
        self.response_factory = DjangoOpenAPIResponseFactory()
        self.get_response = get_response
        self.request_validator = RequestValidator(settings.OPENAPI_SPEC)
        self.response_validator = ResponseValidator(settings.OPENAPI_SPEC)
        self.path_finder = PathFinder(settings.OPENAPI_SPEC)
        self.strict_path = settings.OPENAPI_STRICT_PATH
        self.strict_request_schema = settings.OPENAPI_STRICT_REQUEST_SCHEMA
        self.strict_response_schema = settings.OPENAPI_STRICT_RESPONSE_SCHEMA

    def __call__(self, request: HttpRequest):
        # Check path
        try:
            openapi_request = self.request_factory.create(request)
            self.path_finder.find(openapi_request)
        except (PathNotFound, OperationNotFound, ServerNotFound) as err:
            logger.warning("Invalid path", exc_info=True)
            if self.strict_path:
                return JsonResponse(
                    data={"errors": [str(err)]},
                    status=404,
                )
            return self.get_response(request)
        except Exception:
            logger.warning("An error occured in the open api validator", exc_info=True)
            return self.get_response(request)

        # Check input
        try:
            result = self.request_validator.validate(openapi_request)
            if result.errors:
                logger.warning("Invalid schema, but ingore: %s", result.errors)

                if self.strict_request_schema:
                    data = {
                        "errors": [str(error) for error in result.errors],
                    }
                    return JsonResponse(
                        data=data,
                        status=400,
                    )
                return self.get_response(request)

        except Exception:
            logger.warning("An error occured in the open api validator", exc_info=True)
            return self.get_response(request)

        response = self.get_response(request)

        # Check output
        try:
            openapi_response = self.response_factory.create(response)
            result = self.response_validator.validate(openapi_response)
            if result.errors:
                logger.warning("Invalid response schema: %s", result)
        except Exception:
            logger.warning("An error occured in the open api validator", exc_info=True)
            if self.strict_response_schema:
                raise

        return response
