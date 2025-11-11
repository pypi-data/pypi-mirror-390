# ALM Traceability Management System

A PostgreSQL-based traceability management system for ALM (Application Lifecycle Management) platforms, supporting Azure DevOps and Jira integration.

## Features

- **PostgreSQL Backend**: Robust database schema with `alm_platform_type` enum and `traceability_links` table
- **ALM Platform Support**: Azure DevOps and Jira integration
- **Traceability Links**: Link sessions, requirements, and test cases with relationship types
- **MCP Tools**: Complete set of MCP tools for traceability operations
- **CloudSQL Support**: Ready for Google Cloud SQL deployment
- **Comprehensive Testing**: Built-in test suite for validation

## Database Schema

The system uses a PostgreSQL database with the following key components:

### Tables

- `sessions` - Test sessions with ALM type
- `requirements` - Requirements with ALM type
- `test_cases` - Test cases with ALM type
- `traceability_links` - Main traceability relationships

### Key Features

- `alm_platform_type` enum: `'azure_devops'`, `'jira'`
- Relationship types: `'tests'`, `'covers'`, `'implements'`, `'relates_to'`
- Confidence scoring and metadata support
- Automatic timestamps and audit trails

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

- `asyncpg>=0.29.0` - PostgreSQL async driver
- `mcp>=1.0.0` - MCP server framework
- `pydantic>=2.5.0` - Configuration management
- `python-dotenv>=1.0.0` - Environment variables

### 2. Database Setup

#### Option A: Local PostgreSQL

1. Install PostgreSQL 15+
2. Create database:
   ```bash
   createdb alm_traceability
   ```
3. Run schema:
   ```bash
   psql -d alm_traceability -f database/schema.sql
   ```

#### Option B: Google Cloud SQL

1. Create CloudSQL PostgreSQL instance
2. Configure connection in `.env`
3. Use Cloud SQL Proxy or direct connection

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alm_traceability
DB_USER=postgres
DB_PASSWORD=your-password

# Azure DevOps
ADO_ORGANIZATION=your-org
ADO_PROJECT=your-project
ADO_PERSONAL_ACCESS_TOKEN=your-pat

# Jira
JIRA_BASE_URL=https://company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJECT
```

### 4. Test the Setup

Run the comprehensive test suite:

```bash
python test_traceability.py
```

This will test:

- Database connectivity
- Schema validation
- Traceability operations
- Environment configuration

## Usage

### Starting the MCP Server

```bash
python mcp_main.py
```

The server will initialize with PostgreSQL-based traceability tools.

### Available MCP Tools

#### Database Management

- `initialize_traceability_database()` - Initialize database connection
- `test_database_connection()` - Test connectivity and schema

#### Traceability Operations

- `create_traceability_link()` - Create link between items
- `get_traceability_link(link_id)` - Get specific link
- `get_traceability_links_for_item()` - Get all links for an item
- `generate_traceability_report()` - Generate reports

#### Bulk Operations

- `link_session_to_requirements()` - Link session to multiple requirements
- `link_requirements_to_test_cases()` - Link requirements to test cases
- `get_traceability_matrix_for_session()` - Get complete matrix

### Example Usage

#### Creating a Traceability Link

```python
# Link a test session to a requirement
await create_traceability_link(
    source_type="session",
    source_id="session-001",
    target_type="requirement",
    target_id="req-001",
    relationship_type="covers",
    source_alm_type="azure_devops",
    target_alm_type="azure_devops",
    confidence_score=0.95,
    description="Test session covers login requirement"
)
```

#### Linking Requirements to Test Cases

```python
# Link multiple requirements to test cases
await link_requirements_to_test_cases(
    requirement_ids=["req-001", "req-002"],
    test_case_ids=["tc-001", "tc-002", "tc-003"],
    alm_type="azure_devops",
    confidence_score=0.9
)
```

#### Generating Reports

```python
# Generate summary report
await generate_traceability_report(
    report_type="summary",
    alm_type="azure_devops"
)

# Generate detailed report
await generate_traceability_report(
    report_type="detailed"
)
```

## Architecture

### Components

1. **`database_manager.py`** - PostgreSQL connection management with async support
2. **`traceability_manager.py`** - Core traceability operations and business logic
3. **`mcp_traceability_tools.py`** - MCP tool registration and API
4. **`config.py`** - Configuration models with database settings
5. **`database/schema.sql`** - Complete PostgreSQL schema with functions

### Database Functions

The schema includes helpful PostgreSQL functions:

- `add_traceability_link()` - Safely create links with conflict handling
- `get_traceability_links()` - Query links with direction filtering
- `update_updated_at_column()` - Automatic timestamp updates

### Views

- `traceability_matrix` - Comprehensive view joining all link details

## CloudSQL Deployment

### Prerequisites

1. Google Cloud Project with CloudSQL API enabled
2. CloudSQL PostgreSQL instance
3. Database user with sufficient permissions

### Connection Options

#### Option 1: Cloud SQL Proxy

```bash
# Install Cloud SQL Proxy
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
chmod +x cloud_sql_proxy

# Start proxy
./cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432
```

Environment configuration:

```bash
DB_HOST=localhost
DB_PORT=5432
USE_CLOUD_SQL_PROXY=true
CLOUDSQL_INSTANCE=project:region:instance
```

#### Option 2: Direct Connection

```bash
DB_HOST=your-cloudsql-ip
DB_PORT=5432
DB_SSL_MODE=require
```

## Testing

The system includes comprehensive testing:

### Test Categories

1. **Environment Configuration** - Validates all required variables
2. **Database Connection** - Tests connectivity and schema
3. **Schema Functions** - Validates PostgreSQL functions
4. **Traceability Manager** - Tests all CRUD operations

### Running Tests

```bash
# Run all tests
python test_traceability.py

# Test specific components
python test_traceability.py  # Choose option 2 for DB only
```

### Sample Data

Create sample traceability data for testing:

```bash
python test_traceability.py  # Choose option 4
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running
   - Verify credentials in `.env`
   - Test network connectivity

2. **Schema Errors**

   - Run `database/schema.sql` manually
   - Check PostgreSQL version (15+ recommended)
   - Verify user permissions

3. **Missing Dependencies**

   - Install requirements: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **CloudSQL Issues**
   - Verify instance is running
   - Check firewall rules
   - Validate SSL configuration

### Log Analysis

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python mcp_main.py
```

## Security Considerations

1. **Database Security**

   - Use strong passwords
   - Enable SSL/TLS
   - Restrict network access

2. **API Tokens**

   - Store in environment variables
   - Use least privilege access
   - Rotate regularly

3. **CloudSQL Security**
   - Enable authorized networks
   - Use private IP when possible
   - Enable audit logging

## Support

For issues and questions:

1. Check the test output: `python test_traceability.py`
2. Review logs for detailed error messages
3. Verify environment configuration
4. Test database connectivity independently

## License

This project is licensed under the MIT License.
