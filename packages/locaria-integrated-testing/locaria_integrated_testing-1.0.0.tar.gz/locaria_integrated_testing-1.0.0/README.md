# Locaria Integrated Testing Framework

A lightweight, automated testing system for data pipelines and tools. Focuses on business-logic validation, data quality checks, and operational sanity tests rather than UI or cosmetic testing.

## Features

- **Business Logic Validation** - Test time splits sum to 100%, financial ratios are within bounds, etc.
- **Data Quality Checks** - Schema validation, null checks, row count sanity, data freshness
- **Configurable Thresholds** - Firestore-based configuration for easy threshold updates
- **Integrated Logging** - Sheet Logger integration for persistent test result storage
- **Email Alerts** - Real-time failure notifications via existing email manager API
- **Pipeline-Specific Tests** - Custom business logic validation for different data domains

## Quick Start

### Basic Usage

```python
from modules.integrated_tests import create_testkit, SchemaTests, DataQualityTests, FreshnessTests

# Initialize testing framework
testkit = create_testkit("locate_2_pulls", "daily_updates")

# Initialize test classes
schema_tests = SchemaTests(testkit)
data_quality_tests = DataQualityTests(testkit)
freshness_tests = FreshnessTests(testkit)

try:
    # Your data pipeline code
    df = extract_data()
    
    # Stage 1: Intake tests
    schema_tests.check_required_columns(df, ["employee_id", "date", "hours"])
    schema_tests.check_data_types(df, {"employee_id": "object", "hours": "float64"})
    
    # Stage 2: Transform tests
    df_transformed = transform_data(df)
    # Row count checks moved to RowCountTests
    row_count_tests.check_row_count_change(df_transformed, "table_name", "append")
    
    # Stage 3: Load tests
    load_to_bq(df_transformed, table="finance.time_splits")
    freshness_tests.check_data_freshness(df_transformed, "timestamp")
    
finally:
    # Always finalize the test run
    testkit.finalize_run()
```

## Environment Setup

The framework automatically integrates with the existing `locate_2_pulls` configuration store. No additional environment variables are required for basic functionality.

### Optional Environment Variables

For advanced usage or when running outside the `locate_2_pulls` environment:

```bash
# Email API configuration (fallback)
export EMAIL_API_URL="https://your-app.appspot.com/api/tools/send_email_direct"

# Sheet Logger configuration (fallback)
export TEST_LOGS_SPREADSHEET_ID="your-google-sheets-id"
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
```

### Automatic Configuration

The framework automatically uses:
- **Firestore Project**: `locaria-dev-config-store` (from config store)
- **Sheet Logger**: Existing sheet logger instance from config store
- **Email API**: Tool URL from config store (`tool_URL + api/tools/send_email_direct`)

## Test Classes

### SchemaTests

Schema validation tests for data quality assurance:

- `check_required_columns()` - Validate required columns exist
- `check_data_types()` - Validate column data types
- `check_null_constraints()` - Check for nulls in critical fields
- `check_unique_constraints()` - Validate unique key constraints
- `check_column_values()` - Check values within expected ranges or sets
- `check_schema_completeness()` - Comprehensive schema validation

### DataQualityTests

Data quality tests for common validation scenarios:

- `check_row_count_change()` - Row count change check with Firestore history (append/truncate)
- `check_numeric_ranges()` - Values within expected ranges
- `check_duplicate_records()` - Detect duplicate entries
- `check_data_completeness()` - Data completeness above threshold
- `check_date_ranges()` - Date values within reasonable bounds

### FreshnessTests

Data freshness tests for ensuring data is up-to-date:

- `check_data_freshness()` - Verify data is up-to-date
- `check_timestamp_progression()` - Timestamps moving forward
- `check_data_consistency()` - Data frequency and gap validation
- `check_data_age_distribution()` - Data age distribution analysis

## Configuration

Configuration is stored in Firestore in the `locaria-dev-config-store` project (automatically detected from the existing config store) under the `integrated_testing_config` collection.

### Default Configuration

```json
{
  "thresholds": {
    "row_count_change": {
      "warn_percentage": 20,
      "fail_percentage": 50
    },
    "out_of_office_percentage": {
      "warn_threshold": 25,
      "fail_threshold": 35
    },
    "time_split_tolerance": {
      "precision": 0.01
    },
    "data_freshness": {
      "max_age_hours": 24,
      "warn_age_hours": 12
    }
  },
  "test_switches": {
    "enable_schema_validation": true,
    "enable_business_logic_checks": true,
    "enable_freshness_checks": true,
    "enable_row_count_validation": true
  },
  "email_alerts": {
    "failure_recipients": ["data_team@locaria.com"],
    "warning_recipients": ["data_team@locaria.com"],
    "digest_frequency": "daily"
  }
}
```

### Managing Configuration

```python
from modules.integrated_tests import ConfigManager

# Initialize config manager
config_manager = ConfigManager()

# Create default configuration for a repository
config_manager.create_default_config_for_repository("locate_2_pulls")

# Update thresholds
config_manager.update_thresholds(
    "locate_2_pulls",
    "row_count_change",
    {"warn_percentage": 15, "fail_percentage": 40}
)

# Update test switches
config_manager.update_test_switches(
    "locate_2_pulls",
    {"enable_schema_validation": False}
)
```

## Test Severity Levels

- **FAIL** - Stops pipeline execution, logs error, sends immediate email alert
- **WARN** - Continues pipeline execution, logs warning, sends digest email
- **PASS** - Test passed, logs success

## Email Templates

The framework uses pre-configured email templates in the email manager:

- **Test Failure Alert** - Immediate notification for FAIL results
- **Test Warning Digest** - Grouped notification for WARN results

## Examples

See the `examples/` directory for complete pipeline implementations:

- `sample_pipeline.py` - Complete pipeline with integrated testing
- `config_store_integration_example.py` - Demonstrates automatic config store integration

Run the examples:

```bash
cd modules/integrated_tests/examples
python sample_pipeline.py
python config_store_integration_example.py
```

## Architecture

```
integrated_tests/
├── __init__.py                 # Main module exports
├── main/
│   └── testkit.py             # Core framework and orchestration
├── utils/
│   └── config_manager.py      # Firestore configuration management
├── generic_tests/
│   ├── __init__.py
│   ├── schema_tests.py        # Schema validation tests
│   ├── data_quality_tests.py  # Data quality tests
│   └── freshness_tests.py     # Data freshness tests
├── pipeline_specific_tests/   # Business logic tests per domain
│   └── __init__.py
├── examples/
│   └── sample_pipeline.py     # Usage examples
└── README.md
```

## Best Practices

### Test Design
- Focus on business logic and data quality
- Use descriptive test names that explain the business rule
- Test at multiple stages: intake, transform, load, post-load
- Include both positive and negative test cases

### Error Handling
- Always use try/finally blocks to ensure test finalization
- Handle missing data gracefully
- Provide meaningful error messages
- Log sufficient context for debugging

### Performance
- Batch test operations when possible
- Use efficient pandas operations
- Avoid unnecessary data copies
- Cache configuration when appropriate

### Configuration
- Use Firestore for dynamic configuration
- Provide sensible defaults
- Document all thresholds and switches
- Version control configuration changes

## Troubleshooting

### Common Issues

1. **Sheet Logger Not Working**
   - Check `TEST_LOGS_SPREADSHEET_ID` environment variable
   - Verify Google credentials path
   - Ensure spreadsheet exists and is accessible

2. **Email Alerts Not Sending**
   - Check `EMAIL_API_URL` environment variable
   - Verify email templates are configured in email manager
   - Check network connectivity

3. **Firestore Configuration Issues**
   - Verify `locaria-dev-config-store` project access
   - Check collection and document permissions
   - Ensure configuration document exists

4. **Test Failures**
   - Check test thresholds in Firestore
   - Verify data quality and schema
   - Review test logic and business rules

### Debug Mode

Enable debug logging by setting the log level in configuration:

```python
config_manager.update_repository_config(
    "locate_2_pulls",
    {"logging": {"log_level": "DEBUG"}}
)
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Include comprehensive error handling
3. Add configuration options for thresholds
4. Update documentation
5. Add examples for new functionality

## Support

For questions or issues, contact the Data Team at data_team@locaria.com.
