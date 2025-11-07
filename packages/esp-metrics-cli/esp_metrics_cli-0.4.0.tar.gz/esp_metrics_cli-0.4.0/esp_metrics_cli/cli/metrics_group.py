import json
import logging
import sys
import time
import typing as t

import click

from esp_metrics_cli.models.config import BucketType
from esp_metrics_cli.models.config import MetricsSettings
from esp_metrics_cli.models.result import UploadResult

from ..uploaders.metrics_uploader import MetricsUploader
from ..utils import load_json_file
from ..validators.metrics_validator import MetricsValidator
from ._options import option_bucket_type
from ._options import option_custom_bucket
from ._options import option_definitions_file
from ._options import option_input_file
from ._options import option_output_file
from ._options import option_skip_schema_validation
from ._options import option_verbose

logger = logging.getLogger(__name__)


def print_errors(errors):
    click.echo('Errors:')
    for error in errors:
        click.echo(f'  - {error}')


def handle_exception(msg, e):
    click.secho(f'{msg}: {e}', fg='red')
    logger.exception(msg)
    sys.exit(1)


def _validate_upload_options(bucket_type: str, custom_bucket: str) -> None:
    """Validate upload command options."""
    if bucket_type == BucketType.CUSTOM.value and not custom_bucket:
        raise click.UsageError('--custom-bucket is required when --bucket-type=custom')


def _print_upload_info(
    input_file: str,
    bucket_type: str | None,
    custom_bucket: str | None,
    verbose: bool,
    definitions_file: str | None = None,
) -> None:
    """Print upload information if verbose mode is enabled."""
    if not verbose:
        return

    click.echo(f'Uploading metrics file: {input_file}')
    if definitions_file:
        click.echo(f'Using definitions file: {definitions_file}')
    if bucket_type:
        click.echo(f'Bucket type override: {bucket_type}')
        if bucket_type == BucketType.CUSTOM.value and custom_bucket:
            click.echo(f'Custom bucket: {custom_bucket}')


def _handle_upload_result(
    result: UploadResult, verbose: bool, start_time: float, metrics_count: int | None = None
) -> bool:
    """Handle and print upload result."""
    if not result.upload_successful:
        click.secho('✗ Upload failed!', fg='red')
        if result.upload_error:
            click.echo(f'Upload error: {result.upload_error}')
        return False

    click.secho('✓ Upload successful!', fg='green')
    if verbose:
        upload_time = time.time() - start_time
        if metrics_count:
            click.echo(f'Uploaded {metrics_count} metrics in {upload_time:.2f} seconds')
        else:
            click.echo(f'Upload completed in {upload_time:.2f} seconds')
        if result.upload_url:
            click.echo(f'Upload URL: {result.upload_url}')
    return True


@click.command()
@option_definitions_file()
@option_input_file
@option_output_file
@option_verbose
@click.pass_context
def validate(ctx, definitions_file, input_file, output_file, verbose):
    """Validate a metrics file against schema definitions."""
    start_time = time.time()
    settings = MetricsSettings()
    validator = MetricsValidator(settings, verbose)
    if verbose:
        click.echo(f'Validating metrics file: {input_file}')
        click.echo(f'Using definitions file: {definitions_file}')
    try:
        result = validator.validate(input_file, definitions_file)
    except Exception as e:
        handle_exception('✗ Validation error', e)

    validation_time = time.time() - start_time
    result.validation_time = validation_time

    if not result.is_valid:
        click.secho('✗ Validation failed!', fg='red')
        print_errors(result.errors)
        ctx.exit(1)

    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(result.data, f, indent=2)
        except Exception as e:
            click.secho(f'Warning: Could not save output file: {e}', fg='yellow')

    click.secho('✓ Validation successful!', fg='green')
    if verbose:
        click.echo(f'Validated {result.metrics_count} metrics in {validation_time:.2f} seconds')


def _upload_without_validation(
    input_file: str, uploader: MetricsUploader, bucket_type: str | None, custom_bucket: str | None, verbose: bool
) -> t.Any:
    """Load and upload metrics without validation."""
    _print_upload_info(input_file, bucket_type, custom_bucket, verbose)
    if verbose:
        click.echo('Schema validation is skipped')

    try:
        return load_json_file(input_file)  # type: ignore[no-any-return]
    except Exception as e:
        handle_exception('✗ Error loading metrics file', e)
        raise  # For type checker - handle_exception calls sys.exit()


def _upload_with_validation(
    input_file: str,
    definitions_file: str,
    validator: MetricsValidator,
    bucket_type: str | None,
    custom_bucket: str | None,
    verbose: bool,
    ctx: click.Context,
) -> tuple[t.Any, int]:
    """Validate and prepare metrics for upload."""
    _print_upload_info(input_file, bucket_type, custom_bucket, verbose, definitions_file)

    validation_result = validator.validate(input_file, definitions_file)
    if not validation_result.is_valid:
        click.secho('✗ Validation failed! Cannot upload invalid metrics.', fg='red')
        print_errors(validation_result.errors)
        ctx.exit(1)

    return validation_result.data, validation_result.metrics_count


@click.command()
@option_definitions_file(required=False)
@option_input_file
@option_verbose
@option_bucket_type
@option_custom_bucket
@option_skip_schema_validation
@click.pass_context
def upload(ctx, definitions_file, input_file, verbose, bucket_type, custom_bucket, skip_schema_validation):
    """Upload validated metrics to the service."""
    start_time = time.time()
    _validate_upload_options(bucket_type, custom_bucket)

    if not skip_schema_validation and not definitions_file:
        raise click.UsageError('--definitions is required unless --skip-schema-validation is set')

    settings = MetricsSettings()
    uploader = MetricsUploader(settings, verbose)

    if skip_schema_validation:
        metrics_data = _upload_without_validation(input_file, uploader, bucket_type, custom_bucket, verbose)
        metrics_count = None
    else:
        validator = MetricsValidator(settings, verbose)
        metrics_data, metrics_count = _upload_with_validation(
            input_file, definitions_file, validator, bucket_type, custom_bucket, verbose, ctx
        )

    try:
        result = uploader.upload(metrics_data, bucket_type, custom_bucket)
    except Exception as e:
        handle_exception('✗ Upload error', e)

    success = _handle_upload_result(result, verbose, start_time, metrics_count)
    if not success:
        ctx.exit(1)
