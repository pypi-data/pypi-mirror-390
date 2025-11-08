# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`mb-pipedrive-integration` is a Django-compatible Python package for integrating with the Pipedrive CRM API. It provides a clean abstraction layer for creating deals, managing persons and organizations, and synchronizing data between Django applications and Pipedrive.

**Key concepts:**
- Built using `uv` for package management
- Uses dataclasses for type-safe data modeling
- Implements automatic retry logic with exponential backoff for API requests
- Supports both Django settings and environment variables for configuration
- Role-based tagging system (tenant → INQUILINO, advisor → ASESOR INMOBILIARIO, landlord → PROPIETARIO)

## Development Commands

### Setup
```bash
# Install dependencies including dev tools
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install
```

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run with detailed coverage report
uv run pytest --cov=mb_pipedrive_integration --cov-report=term-missing

# Run integration tests (requires real API credentials)
uv run pytest tests/test_integration.py --integration

# Run specific test file
uv run pytest tests/test_services.py
```

### Code Quality
```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Individual tools
uv run black .
uv run flake8
uv run mypy mb_pipedrive_integration/
```

### Building and Publishing
```bash
# Build package
uv build

# Publish to PyPI (requires credentials)
uv publish
```

## Architecture

### Core Components

**PipedriveService** (`services.py`)
- Main service class handling all Pipedrive API interactions
- Implements `_make_request()` with retry logic, rate limiting (429), and timeout handling
- Key methods:
  - `create_person()`, `get_or_create_person()`, `update_person()` - Person management
  - `create_organization()`, `get_or_create_organization()` - Organization management with custom field lookups
  - `create_deal()` - Creates deals and automatically associates persons/organizations
  - `attach_product_to_deal()`, `attach_multiple_products_to_deal()` - Product attachments
  - `link_person_to_organization()` - Associate persons with organizations
  - `find_organization_by_custom_field()` - Generic custom field search with pagination

**Data Classes** (`dataclasses.py`)
- `PersonData` - Person info with email validation and tagging support
- `OrganizationData` - Organization info with custom field support
- `DealData` - Deal info including tenant, advisor, landlord, and organization references
- `ProductData` - Product attachment configuration for deals
- `PipedriveConfig` - Configuration with `from_django_settings()` and `from_env()` factory methods

**Exception Hierarchy** (`exceptions.py`)
```
PipedriveError (base)
├── PipedriveConfigError - Missing/invalid configuration
├── PipedriveAPIError - API errors with status code and response data
├── PipedriveNetworkError - Network issues with retry count
└── PipedriveValidationError - Data validation failures
```

### Configuration Priority
1. Explicit `PipedriveConfig` passed to `PipedriveService(config=...)`
2. Django settings (`PIPEDRIVE_*` settings)
3. Environment variables (`PIPEDRIVE_COMPANY_DOMAIN`, `PIPEDRIVE_API_TOKEN`)

### Custom Fields Mapping
Custom fields in Django settings/config are mapped with prefixes:
- Deal fields: Direct mapping (e.g., `folder_number` → custom field hash)
- Organization fields: `org_` prefix (e.g., `org_mb_id` → custom field hash)

Used in:
- `create_deal()` - Maps `folder_number`, `folder_id`, `property_owner_person`, `tenant_person`, `multiexpediente_url`
- `create_organization()` - Maps any `org_*` custom fields
- `find_organization_by_custom_field()` - Searches by any custom field with `org_` prefix

## Important Implementation Details

### Person and Organization Creation
- `create_deal()` automatically creates or retrieves tenant, advisor, and landlord persons with appropriate tags
- If advisor and organization both exist, `link_person_to_organization()` is called automatically
- Tags are applied during person creation via the `label` field (comma-separated string)

### Product Attachments
- Products can be attached with optional custom pricing, discounts, and tax
- `attach_product_to_deal()` fetches default product price if not provided
- `attach_multiple_products_to_deal()` returns detailed success/failure summary

### Error Handling Pattern
All API methods follow this pattern:
1. Try API operation with retry logic
2. Log errors with structured messages
3. Return `None` or `False` on failure (don't raise exceptions by default)
4. Exceptions only raised for critical configuration errors

### Testing Strategy
- Unit tests (`test_services.py`, `test_dataclasses.py`) use mocked API responses via `responses` library
- Integration tests (`test_integration.py`) require `--integration` flag and real API credentials
- Test fixtures in `conftest.py` provide both mock and real sandbox configurations

## Code Style

- **Formatting**: Black with 100 character line length, double quotes
- **Import ordering**: isort with Black profile
- **Type hints**: Required for all function signatures (enforced by mypy strict mode)
- **Logging**: Use module-level `logger = logging.getLogger(__name__)`
- **String formatting**: Use f-strings for logging and messages
