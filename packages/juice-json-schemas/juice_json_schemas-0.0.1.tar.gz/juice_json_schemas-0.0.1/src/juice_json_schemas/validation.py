import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import CannotDetermineSpecification


class ValidationError(Exception):
    def get_message(self):
        return self.__str__()


class JsonFileError(ValidationError):
    def __init__(self, file_path):
        super().__init__(f"JSON file error: {file_path}")


class RemoteJsonFileError(ValidationError):
    def __init__(self, url):
        super().__init__(f"Remote JSON file error: {url}")


class InvalidJsonError(ValidationError):
    def __init__(self, path):
        super().__init__(f"Invalid JSON: {path}")


class InvalidSchemaError(ValidationError):
    def __init__(self, path):
        super().__init__(f"Invalid schema: {path}")


def load_json_from_path_or_url(path_or_url):
    """Load JSON either from a local file or from a URL."""
    parsed = urlparse(path_or_url)

    if parsed.scheme in ("http", "https"):
        try:
            with urlopen(path_or_url) as response:  # noqa: S310
                return json.load(response)
        except Exception as e:
            raise RemoteJsonFileError(path_or_url) from e
    try:
        path = Path(path_or_url)
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise JsonFileError(path_or_url) from e
    except json.JSONDecodeError as e:
        raise InvalidJsonError(path_or_url) from e


def validate_json(instance_path, schema_path):
    """Validate JSON instance against schema (local or remote), reporting all errors."""
    instance = load_json_from_path_or_url(instance_path)
    schema = load_json_from_path_or_url(schema_path)

    try:
        # Build a registry that knows where to find the root schema
        registry = Registry().with_resource(schema_path, Resource.from_contents(schema))
        validator = Draft202012Validator(schema, registry=registry)
    except SchemaError as e:
        raise InvalidSchemaError(schema_path) from e
    except CannotDetermineSpecification as e:
        raise InvalidSchemaError(schema_path) from e

    # Return all errors sorted by their path
    return sorted(validator.iter_errors(instance), key=lambda e: e.path)
