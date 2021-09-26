# DRF Open API Validator

## Usage

Install django-open-api-validator with pip.

```shell script
$ pip install drf-open-api-validator
```

Add django application drf_open_api_validator to INSTALLED_APPS in settings.py.

```python
INSTALLED_APPS = [
    ...
    'drf_open_api_validator',
    ...
]
```

Add RequestValidatorMiddleware and ResponseValidatorMiddleware to MIDDLEWARE in settings.py.

```python
MIDDLEWARE = [
    ...
    'drf_open_api_validator.middleware.DjangoOpenAPIRequestValidationMiddleware,
    ...
]
```

## Configuration

| settings.py value                | Type                             | Default |
|:---------------------------------|:---------------------------------|:--------|
| `OPENAPI_SPEC`                   | openapi_core.spec.paths.SpecPath | False   |
| `OPENAPI_STRICT_PATH`            | boolean                          | False   |
| `OPENAPI_STRICT_REQUEST_SCHEMA`  | boolean                          | False   |
| `OPENAPI_STRICT_RESPONSE_SCHEMA` | boolean                          | False   |

## Testing

### pytest

```
$ pytest
```

### multi version

```
$ tox
```

## Release

- Bump version. Edit setup.cfg file.
- Generate distribution files. `python -m build`.
- Check distribution files. `twine check dist/*`.
  - You need to make sure there are no "errors" displayed on the console.
- Upload distribution files. `twine upload dist/*`.
