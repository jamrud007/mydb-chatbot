# MySQL Chatbot - Test Suite

This directory contains all test files for the MySQL Chatbot application.

## Test Files

### Core Features
- `test_query_timeout.py` - Query timeout functionality
- `test_input_sanitization.py` - SQL injection protection

### Advanced Features  
- `test_structured_logging.py` - JSON structured logging
- `test_metrics.py` - Performance metrics collection
- `test_history_export.py` - Conversation export functionality
- `test_i18n.py` - Multi-language support
- `test_query_suggestions.py` - Autocomplete system
- `test_schema_docs.py` - Documentation generator

## Running Tests

### Run all tests:
```bash
# From project root
python -m pytest tests/

# Or run individually
python tests/test_query_timeout.py
python tests/test_metrics.py
```

### Run specific test:
```bash
python tests/test_i18n.py
```

## Test Coverage

All tests verify:
- ✅ Functionality works as expected
- ✅ Error handling is correct
- ✅ Edge cases are handled
- ✅ Output format is valid

## Notes

- All tests are standalone and can be run independently
- Tests use the actual database connection (ensure DB is running)
- Some tests create temporary data (auto-cleaned)
