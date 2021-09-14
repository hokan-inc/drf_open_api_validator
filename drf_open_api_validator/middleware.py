import logging

import django
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from openapi_core.contrib.django.requests import DjangoOpenAPIRequestFactory
from openapi_core.templating.paths.exceptions import OperationNotFound, PathNotFound, ServerNotFound
from openapi_core.templating.paths.finders import PathFinder
from openapi_core.validation.request.validators import RequestValidator

logger = logging.getLogger(__name__)


class DjangoOpenAPIRequestValidationMiddleware:
    def __init__(self, get_response):
        self.request_factory = DjangoOpenAPIRequestFactory()
        self.get_response = get_response
        self.request_validator = RequestValidator(settings.OPENAPI_SPEC)
        self.path_finder = PathFinder(settings.OPENAPI_SPEC)
        self.strict_path = settings.OPENAPI_STRICT_PATH
        self.strict_schema = settings.OPENAPI_STRICT_SCHEMA

    def __call__(self, request: HttpRequest):
        openapi_request = self.request_factory.create(request)

        try:
            self.path_finder.find(openapi_request)
        except (PathNotFound, OperationNotFound, ServerNotFound) as err:
            if self.strict_path:
                return JsonResponse(
                    data={"errors": [str(err)]},
                    status=404,
                )
            logger.debug("Invalid path, but ingore: %s", err)
            return self.get_response(request)
        else:
            result = self.request_validator.validate(openapi_request)
            if result.errors:
                if self.strict_schema:
                    data = {
                        "errors": [str(error) for error in result.errors],
                    }
                    return JsonResponse(
                        data=data,
                        status=400,
                    )
            logger.debug("Invalid schema, but ingore: %s", result.errors)
        return self.get_response(request)
