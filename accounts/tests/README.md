# Tests

This directory contains project-wide test configurations and integration tests for the Django JWT Authentication Service.

## Files

### Configuration
- **`pytest.ini`** - Pytest configuration file with test discovery settings, markers, and options

### Integration Tests
- **`test_rate_limiting.py`** - Rate limiting integration tests across all authentication endpoints

## Directory Structure

```
tests/
├── README.md              # This file
├── pytest.ini            # Pytest configuration
└── test_rate_limiting.py  # Rate limiting tests
```

## Usage

### Running Tests

**All tests from project root:**
```bash
pytest
```

**Specific test file:**
```bash
pytest tests/test_rate_limiting.py
```

**With coverage:**
```bash
pytest --cov=auth_service --cov-report=html
```

### Test Categories

- **Unit Tests**: Located in `accounts/tests/` for individual components
- **Integration Tests**: Located in this directory for cross-component functionality
- **Rate Limiting Tests**: Comprehensive throttling and rate limit validation

## Configuration

The `pytest.ini` file contains:
- Test discovery patterns
- Output formatting options
- Coverage settings
- Custom pytest markers
- Django test settings

## Notes

- Unit tests for individual apps are located within their respective app directories (`accounts/tests/`)
- This directory focuses on system-wide integration tests
- Rate limiting tests validate throttling across all authentication endpoints
