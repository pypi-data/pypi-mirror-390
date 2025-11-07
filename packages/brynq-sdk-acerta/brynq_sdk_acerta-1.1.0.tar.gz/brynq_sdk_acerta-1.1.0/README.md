# BrynQ SDK - Acerta

Python SDK for interacting with the Acerta HR & Payroll API.

## Overview

The Acerta SDK provides a clean and intuitive interface to interact with Acerta's HR and payroll management system. Built on top of the BrynQ platform, it offers seamless integration with validated data handling using Pandera and Pydantic.

## Features

- 🔐 **Secure Authentication**: Bearer token-based authentication with automatic credential management
- 🌍 **Multi-Environment Support**: Easily switch between test and production environments
- ✅ **Data Validation**: Built-in validation using Pandera (GET) and Pydantic (POST/PUT/PATCH)
- 📊 **Pandas Integration**: GET operations return validated DataFrames for easy data manipulation
- 🔄 **Complete CRUD Operations**: Full support for Create, Read, Update, and Delete operations

## Installation

```bash
pip install brynq-sdk-acerta
```

## Quick Start

```python
from brynq_sdk_acerta import Acerta

# Initialize client (debug=True for test environment)
client = Acerta(system_type="source", debug=False)

# Get employees
employees_df, invalid_df = client.employees.get()

# Get planning data
planning_df, invalid_df = client.planning.get()

# Create new employee
employee_data = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com"
}
response = client.employees.create(employee_data)
```

## Available Resources

### Core Resources
- **`employees`** - Employee management (includes addresses, contact information, family, bank accounts)
- **`employment`** - Employment contracts and relationships
- **`employer`** - Employer information and cost centers
- **`agreements`** - Employment agreements and contracts
- **`planning`** - Workforce planning and scheduling

### Nested Resources
Access nested resources through their parent:
```python
# Employee sub-resources
client.employees.addresses
client.employees.contact_information
client.employees.family
client.employees.bank_accounts

# Employer sub-resources
client.employer.cost_centers
```

## Environment Configuration

The SDK supports two environments:

- **Production**: `https://api.acerta.be`
- **Test**: `https://a-api.acerta.be` (enabled with `debug=True`)

```python
# Production environment
client = Acerta(system_type="source", debug=False)

# Test environment
client = Acerta(system_type="source", debug=True)
```

## Data Validation

### GET Operations
Returns a tuple of two DataFrames:
- **Valid data**: Successfully validated records
- **Invalid data**: Records that failed validation with error details

```python
valid_df, invalid_df = client.employees.get()
print(f"Valid records: {len(valid_df)}")
print(f"Invalid records: {len(invalid_df)}")
```

### POST/PUT/PATCH Operations
Data is automatically validated against Pydantic schemas before sending:

```python
# Data is validated before the request
response = client.employees.create({
    "firstName": "Jane",
    "lastName": "Smith",
    "dateOfBirth": "1990-01-15"
})
```

## Error Handling

The SDK includes comprehensive error handling with descriptive messages:

```python
try:
    response = client.employees.create(employee_data)
    if response.status_code == 201:
        print("Employee created successfully")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Requirements

- Python 3.8+
- pandas >= 2.2.0
- pydantic >= 2.5.0
- pandera >= 0.16.0
- requests >= 2.25.1
- brynq-sdk-functions >= 2.0.5
- brynq-sdk-brynq >= 3

## Support

For issues, questions, or contributions, please contact BrynQ support at support@brynq.com

## License

BrynQ License - © BrynQ
