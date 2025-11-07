import logging
import time
import typing as t

from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema

from pydantic import ValidationError

from esp_metrics_cli.models import MetricsData
from esp_metrics_cli.models.config import MetricsSettings
from esp_metrics_cli.models.result import ValidationResult
from esp_metrics_cli.utils import format_bytes
from esp_metrics_cli.utils import get_file_size
from esp_metrics_cli.utils import load_json_file
from esp_metrics_cli.utils import load_yaml_file

logger = logging.getLogger(__name__)

EXTRACTABLE_FIELD_TYPES = frozenset(['integer', 'number', 'string', 'boolean', 'object', 'array'])


@dataclass(frozen=True)
class FieldMetadata:
    """Represents metadata for a single field."""

    type: str
    title: str
    description: str
    unit: str


class MetricsValidator:
    """Consolidated metrics validator that handles all validation steps."""

    def __init__(self, settings: MetricsSettings, verbose: bool = False):
        """Initialize the validator with settings and verbosity level."""
        self.settings = settings
        self.verbose = verbose
        self._official_schema = None

    def _load_official_schema(self) -> t.Any:
        """Load the official JSON schema for metrics validation."""
        if self._official_schema is None:
            schema_path = Path(__file__).parent.parent / 'schema' / 'metrics_schema.json'
            self._official_schema = load_json_file(str(schema_path))
        return self._official_schema

    def _create_field_metadata(self, field_name: str, field_schema: dict[str, Any]) -> FieldMetadata:
        """Create FieldMetadata from schema definition."""
        return FieldMetadata(
            type=field_schema['type'],
            title=field_schema.get('title', field_name.replace('_', ' ').title()),
            description=field_schema.get('description', ''),
            unit=field_schema.get('unit', ''),
        )

    def _build_field_path(self, *parts: str) -> str:
        """Build a field path from components, filtering out empty parts."""
        return '.'.join(filter(None, parts))

    def _extract_fields_from_properties(
        self, properties: dict[str, Any], path_prefix: str = ''
    ) -> Generator[tuple[str, FieldMetadata], None, None]:
        """Recursively extract field metadata from schema properties using a generator."""
        if not isinstance(properties, dict):
            return

        for field_name, field_schema in properties.items():
            if not isinstance(field_schema, dict):
                continue

            current_path = self._build_field_path(path_prefix, field_name)
            field_type = field_schema.get('type')

            if field_type in EXTRACTABLE_FIELD_TYPES:
                yield current_path, self._create_field_metadata(field_name, field_schema)

            yield from self._process_nested_schemas(field_schema, current_path)

    def _process_nested_schemas(
        self, schema: dict[str, Any], current_path: str
    ) -> Generator[tuple[str, FieldMetadata], None, None]:
        """Process nested schema structures (properties and patternProperties)."""
        if 'properties' in schema:
            yield from self._extract_fields_from_properties(schema['properties'], current_path)

        if 'patternProperties' in schema:
            for pattern, pattern_schema in schema['patternProperties'].items():
                pattern_path = self._build_field_path(current_path, pattern)

                if not isinstance(pattern_schema, dict):
                    continue

                field_type = pattern_schema.get('type')
                if field_type in EXTRACTABLE_FIELD_TYPES:
                    yield pattern_path, self._create_field_metadata(pattern, pattern_schema)

                if 'properties' in pattern_schema:
                    yield from self._extract_fields_from_properties(pattern_schema['properties'], pattern_path)

                yield from self._process_nested_schemas(pattern_schema, pattern_path)

    def _extract_field_metadata(self, schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract metadata (type, title, description, unit) from schema properties."""
        if 'properties' not in schema:
            return {}

        return {
            path: {
                'type': metadata.type,
                'title': metadata.title,
                'description': metadata.description,
                'unit': metadata.unit,
            }
            for path, metadata in self._extract_fields_from_properties(schema['properties'])
        }

    def validate(self, input_file: str, definitions_file: str) -> ValidationResult:
        """Validate a metrics file against Pydantic model and schema."""
        start_time = time.time()
        result = ValidationResult(is_valid=False)

        try:
            metrics_payload = self._validate_file_size_and_load(input_file, result)
            if metrics_payload is None:
                return result

            schema = self._load_definitions_schema(definitions_file, result)
            if schema is None:
                return result

            if not self._validate_unit_presence(schema, result):
                return result

            if not self._validate_definitions_schema(schema, result, metrics_payload):
                return result

            field_metadata = self._extract_field_metadata(schema)
            metrics_data = {
                'commit_sha': self.settings.commit_sha,
                'branch_name': self.settings.branch_name,
                'project_url': self.settings.project_url,
                'project_id': self.settings.project_id,
                'schema_version': self.settings.schema_version,
                'timestamp': datetime.utcnow().isoformat(timespec='milliseconds'),
                'metrics': metrics_payload,
                'metadata': {'metric_fields': field_metadata},
            }

            if not self._validate_json_schema(metrics_data, result):
                return result

            if not self._validate_model(metrics_data, result):
                return result

            result.is_valid = not result.errors
            result.data = metrics_data

            if self.verbose:
                logger.info(f'Validation completed: {result.is_valid=}')
                logger.info(f'Found {result.metrics_count} metrics')

        except Exception as e:
            logger.exception('Unexpected error during validation')
            result.errors.append(f'Unexpected validation error: {e}')
        finally:
            result.validation_time = time.time() - start_time

        return result

    def _validate_file_size_and_load(self, input_file: str, result: ValidationResult) -> dict | None:
        """Validate file size and load metrics file."""
        try:
            result.file_size = get_file_size(input_file)
            if self.verbose:
                logger.info(f'Metrics file size: {format_bytes(result.file_size)}')

            if result.file_size > self.settings.max_metrics_size:
                max_mb = self.settings.max_metrics_size / (1024 * 1024)
                file_mb = result.file_size / (1024 * 1024)
                result.errors.append(
                    f'File {input_file} is too large ({file_mb:.1f}MB), maximum allowed is {max_mb:.1f}MB'
                )
                return None

            if self.verbose:
                logger.info(f'Loading metrics file: {input_file}')

            return load_json_file(input_file)  # type: ignore

        except Exception as e:
            result.errors.append(f'Error loading metrics file: {e}')
            return None

    def _load_definitions_schema(self, definitions_file: str, result: ValidationResult) -> t.Any:
        """Load definitions file and extract schema."""
        if self.verbose:
            logger.info(f'Loading definitions file: {definitions_file}')
        try:
            return load_yaml_file(definitions_file)
        except Exception as e:
            result.errors.append(f'Error loading definitions file: {e}')
            return None

    # ruff: noqa: C901
    def _validate_unit_presence(self, schema: dict, result: ValidationResult) -> bool:
        """Validate that unit fields are present in the definitions schema."""
        missing_units = []

        def _check_property(prop_path: str, prop_schema: dict) -> None:
            """Check properties for unit presence."""
            if isinstance(prop_schema, dict):
                if prop_schema.get('type') in ('integer', 'number', 'string') and 'unit' not in prop_schema:
                    missing_units.append(prop_path)

        def _check_nested_properties(prop_path: str, prop_schema: dict) -> None:
            """Check nested properties or pattern properties."""
            for key in ['properties', 'patternProperties']:
                if key in prop_schema:
                    for nested_name, nested_schema in prop_schema[key].items():
                        nested_path = f'{prop_path}.{nested_name}' if prop_path else nested_name
                        _check_property(nested_path, nested_schema)

        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                _check_property(prop_name, prop_schema)
                _check_nested_properties(prop_name, prop_schema)

        if missing_units:
            result.errors.append(f'Missing unit fields in schema properties: {", ".join(missing_units)}')
            if self.verbose:
                logger.error(f'Missing unit fields: {missing_units}')
            return False

        return True

    def _validate_definitions_schema(
        self, schema: dict, result: ValidationResult, metrics_data: dict[t.Any, t.Any]
    ) -> bool:
        """Validate metrics data against the definitions schema using jsonschema."""
        if self.verbose:
            logger.info('Validating metrics against definitions schema using JSON schema validation')

        try:
            jsonschema.validate(metrics_data, schema)

            if self.verbose:
                logger.info('Metrics passed definitions schema validation')
            return True

        except jsonschema.ValidationError as e:
            error_path = '.'.join(str(p) for p in e.absolute_path) if e.absolute_path else 'root'
            result.errors.append(f'Schema validation failed at {error_path}: {e.message}')
            if self.verbose:
                logger.error(f'Definitions schema validation failed: {e.message}')
            return False
        except jsonschema.SchemaError as e:
            result.errors.append(f'Invalid definitions schema: {e.message}')
            if self.verbose:
                logger.error(f'Invalid definitions schema: {e.message}')
            return False
        except Exception as e:
            result.errors.append(f'Unexpected definitions schema validation error: {e}')
            if self.verbose:
                logger.error(f'Unexpected definitions schema validation error: {e}')
            return False

    def _validate_json_schema(self, metrics_data: dict, result: ValidationResult) -> bool:
        """Validate metrics data against the official JSON schema."""
        if self.verbose:
            logger.info('Validating metrics against JSON schema')
        try:
            official_schema = self._load_official_schema()
            jsonschema.validate(metrics_data, official_schema)
            if self.verbose:
                logger.info('Metrics passed JSON schema validation')
            return True
        except Exception as e:
            result.errors.append(f'JSON schema validation error: {e}')
            return False

    def _validate_model(self, metrics_data: dict, result: ValidationResult) -> bool:
        """Validate metrics data against Pydantic model."""
        if self.verbose:
            logger.info('Validating metrics against schema model')
        try:
            validated_metrics = MetricsData(**metrics_data)
            result.metrics_count = len(validated_metrics.metrics)
            if self.verbose:
                logger.info('Metrics structure validated successfully')
                logger.info(f'Metrics keys: {list(validated_metrics.metrics.keys())}')
            return True
        except ValidationError as e:
            for error in e.errors():
                field_path = ' -> '.join(str(p) for p in error['loc']) if error['loc'] else 'root'
                result.errors.append(f'Pydantic validation failed at {field_path}: {error["msg"]}')
            return False
        except Exception as e:
            result.errors.append(f'Unexpected Pydantic validation error: {e}')
            return False
