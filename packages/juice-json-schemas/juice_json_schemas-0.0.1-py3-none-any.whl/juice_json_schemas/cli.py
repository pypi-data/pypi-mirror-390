import argparse
import logging
import sys

from juice_json_schemas.validation import ValidationError, validate_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse(instance_file, schema_file_or_url):
    try:
        validate_json(instance_file, schema_file_or_url)
    except ValidationError as e:
        logger.exception(e.get_message())
        sys.exit(1)

    errors = validate_json(instance_file, schema_file_or_url)

    if not errors:
        logger.info("✅ JSON is valid according to the schema.")
    else:
        logger.error("❌ Found %d validation error(s):\n", len(errors))
        for i, error in enumerate(errors, 1):
            path = "/".join(map(str, error.path)) or "(root)"
            logger.info("  %d. Path: %s", i, path)
            logger.info("     Message: %s\n", error.message)
        sys.exit(1)


def main():
    argparser = argparse.ArgumentParser()
    argparser.description = "Validate a JSON file against a generic schema."
    argparser.add_argument("json_file", help="Path to the JSON file to be validated")
    argparser.add_argument("schema_file_or_url", help="Path to the schema file or URL")
    args = argparser.parse_args()
    parse(args.json_file, args.schema_file_or_url)


def apl():
    argparser = argparse.ArgumentParser()
    argparser.description = "Validate a JSON file against the JUICE APL schema."
    argparser.add_argument("json_file", help="Path to the APL file to be validated")
    args = argparser.parse_args()
    parse(
        args.json_file,
        "https://juicesoc.esac.esa.int/data/schemas/jsoc-apl-schema.json",
    )


def opl():
    argparser = argparse.ArgumentParser()
    argparser.description = "Validate a OPL file against the JUICE OPL schema."
    argparser.add_argument("json_file", help="Path to the OPL file to be validated")
    args = argparser.parse_args()
    parse(
        args.json_file,
        "https://juicesoc.esac.esa.int/data/schemas/jsoc-opl-schema.json",
    )
