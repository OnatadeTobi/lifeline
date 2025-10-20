# Testing Guide

This document explains the testing structure and how to run tests for the Lifeline project.

## Test Structure

The test suite is organized by Django apps, with each app having its own test directory:

```
apps/
  accounts/
    tests/
      test_views.py      # Tests for account-related views
  blood_requests/
    tests/
      test_views.py      # Tests for blood request functionality
  donors/
    tests/
      test_views.py      # Tests for donor-related features
  hospitals/
    tests/
      test_views.py      # Tests for hospital functionality
  locations/
    tests/
      test_views.py      # Tests for location management
  core/
    tests/
      conftest.py        # Shared test fixtures and utilities
      factories.py       # Model factories for test data
      test_utils.py      # Tests for core utilities
```

### Test Categories

1. **Authentication Tests** (`apps/accounts/tests/`)
   - User login and token management
   - Email verification
   - Password reset functionality

2. **Blood Request Tests** (`apps/blood_requests/tests/`)
   - Creating and managing blood requests
   - Donor response handling
   - Request fulfillment tracking

3. **Donor Tests** (`apps/donors/tests/`)
   - Donor registration
   - Profile management
   - Availability toggling

4. **Hospital Tests** (`apps/hospitals/tests/`)
   - Hospital registration
   - Profile management
   - Service area management

5. **Location Tests** (`apps/locations/tests/`)
   - State and LGA listing
   - Location relationships

6. **Core Utilities Tests** (`apps/core/tests/`)
   - Email masking
   - Blood type compatibility
   - Shared utilities

## Running Tests

### Setup

Make sure you have pytest and required packages installed:
```bash
pip install pytest pytest-django pytest-cov factory-boy freezegun
```

### Running All Tests

To run the entire test suite:
```bash
pytest
```

### Running Specific Tests

Run tests for a specific app:
```bash
pytest apps/accounts/tests/
```

Run a specific test file:
```bash
pytest apps/blood_requests/tests/test_views.py
```

Run a specific test class:
```bash
pytest apps/donors/tests/test_views.py::TestDonorRegistration
```

Run a specific test:
```bash
pytest apps/hospitals/tests/test_views.py::TestHospitalProfile::test_get_hospital_profile
```

### Test Coverage

To run tests with coverage reporting:
```bash
pytest --cov=apps
```

Generate a detailed HTML coverage report:
```bash
pytest --cov=apps --cov-report=html
```
The report will be available in the `htmlcov/` directory.

### Common pytest Options

- `-v`: Verbose output
- `-s`: Show print statements
- `-x`: Stop after first failure
- `--pdb`: Start debugger on failures
- `--reuse-db`: Reuse test database (faster)
- `--create-db`: Create a new test database
- `--no-migrations`: Skip running migrations

## Test Data

The test suite uses Factory Boy to generate test data. Test factories are defined in `apps/core/tests/factories.py`:

- `UserFactory`: Creates user instances
- `StateFactory`: Creates state instances
- `LocalGovernmentFactory`: Creates LGA instances
- `HospitalFactory`: Creates hospital instances
- `DonorFactory`: Creates donor instances
- `BloodRequestFactory`: Creates blood request instances
- `DonorResponseFactory`: Creates donor response instances

## Fixtures

Common test fixtures are available in `apps/core/tests/conftest.py`:

- `api_client`: Basic API client
- `authenticated_client`: Authenticated API client with user
- `donor_client`: API client authenticated as a donor
- `hospital_client`: API client authenticated as a hospital
- `state`: Creates a test state
- `local_government`: Creates a test LGA
- `blood_request`: Creates a test blood request
- `donor_response`: Creates a test donor response

## Extending Tests

When adding new features:

1. Create test files in the appropriate app's tests directory
2. Follow the existing pattern of test organization
3. Use the provided fixtures and factories
4. Add new factories if needed in `core/tests/factories.py`
5. Add new fixtures if needed in `core/tests/conftest.py`
6. Ensure both success and failure cases are covered
7. Test edge cases and validation

## Best Practices

1. Use descriptive test names that explain what is being tested
2. Follow the Arrange-Act-Assert pattern
3. Keep tests focused and atomic
4. Use appropriate fixtures to minimize setup code
5. Test both valid and invalid scenarios
6. Use parametrize for testing multiple similar cases
7. Mock external services and APIs
8. Clean up any test data or state after tests