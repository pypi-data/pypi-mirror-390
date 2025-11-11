"""Tests for Company Pydantic model and Companies resource."""

import pytest

from pyplanhat._exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServerError,
)
from pyplanhat._sync.resources.companies import Company


def test_company_minimal_creation():
    """Test creating a company with only required field."""
    company = Company(name="Test Company")

    assert company.name == "Test Company"
    assert company.id is None
    assert company.external_id is None
    assert company.source_id is None
    assert company.custom == {}


def test_company_with_all_fields():
    """Test creating a company with all fields populated."""
    company_data = {
        "name": "Full Company",
        "_id": "12345",
        "externalId": "ext-123",
        "sourceId": "src-456",
        "owner": "user-789",
        "coOwner": "user-101",
        "phase": "customer",
        "status": "customer",
        "domains": ["example.com", "test.com"],
        "description": "A test company",
        "address": "123 Main St",
        "country": "US",
        "city": "San Francisco",
        "zip": "94105",
        "phonePrimary": "+1-555-0123",
        "web": "https://example.com",
        "mrr": 1000.0,
        "arr": 12000.0,
        "nrr30": 1050.0,
        "mrrTotal": 1500.0,
        "nrrTotal": 1575.0,
        "mrTotal": 2000.0,
        "renewalMrr": 800.0,
        "renewalArr": 9600.0,
        "renewalDaysFromNow": 30,
        "customerFrom": "2023-01-01T00:00:00Z",
        "customerTo": "2024-01-01T00:00:00Z",
        "lastRenewal": "2023-06-01T00:00:00Z",
        "h": 85,
        "csmScore": 4,
        "lastActive": "2023-12-01T12:00:00Z",
        "lastTouch": "2023-12-01T10:00:00Z",
        "lastTouchType": "email",
        "alerts": [{"type": "health", "message": "Low engagement"}],
        "lastActivities": [{"type": "call", "date": "2023-11-30"}],
        "orgRootId": "org-root-123",
        "orgPath": ["org-root-123", "org-child-456"],
        "orgLevel": 2,
        "orgUnits": [{"id": "unit-1", "name": "Unit 1"}],
        "orgMrr": 5000.0,
        "orgArr": 60000.0,
        "orgMrrTotal": 7500.0,
        "orgArrTotal": 90000.0,
        "orgHealthTotal": 80,
        "custom": {"industry": "Technology", "employees": 100},
    }

    company = Company(**company_data)

    assert company.name == "Full Company"
    assert company.id == "12345"
    assert company.external_id == "ext-123"
    assert company.source_id == "src-456"
    assert company.owner == "user-789"
    assert company.co_owner == "user-101"
    assert company.phase == "customer"
    assert company.status == "customer"
    assert company.domains == ["example.com", "test.com"]
    assert company.description == "A test company"
    assert company.address == "123 Main St"
    assert company.country == "US"
    assert company.city == "San Francisco"
    assert company.zip == "94105"
    assert company.phone_primary == "+1-555-0123"
    assert company.web == "https://example.com"
    assert company.mrr == 1000.0
    assert company.arr == 12000.0
    assert company.nrr30 == 1050.0
    assert company.mrr_total == 1500.0
    assert company.nrr_total == 1575.0
    assert company.mr_total == 2000.0
    assert company.renewal_mrr == 800.0
    assert company.renewal_arr == 9600.0
    assert company.renewal_days_from_now == 30
    assert company.customer_from == "2023-01-01T00:00:00Z"
    assert company.customer_to == "2024-01-01T00:00:00Z"
    assert company.last_renewal == "2023-06-01T00:00:00Z"
    assert company.h == 85
    assert company.csm_score == 4
    assert company.last_active == "2023-12-01T12:00:00Z"
    assert company.last_touch == "2023-12-01T10:00:00Z"
    assert company.last_touch_type == "email"
    assert company.alerts == [{"type": "health", "message": "Low engagement"}]
    assert company.last_activities == [{"type": "call", "date": "2023-11-30"}]
    assert company.org_root_id == "org-root-123"
    assert company.org_path == ["org-root-123", "org-child-456"]
    assert company.org_level == 2
    assert company.org_units == [{"id": "unit-1", "name": "Unit 1"}]
    assert company.org_mrr == 5000.0
    assert company.org_arr == 60000.0
    assert company.org_mrr_total == 7500.0
    assert company.org_arr_total == 90000.0
    assert company.org_health_total == 80
    assert company.custom == {"industry": "Technology", "employees": 100}


def test_company_serialization_with_alias():
    """Test that model serializes correctly with aliases."""
    company = Company(
        name="Test Company",
        _id="12345",
        external_id="ext-123",
        source_id="src-456",
        co_owner="user-101",
        phone_primary="+1-555-0123",
        custom={"key": "value"},
    )

    # Test serialization with by_alias=True for _id field
    data = company.model_dump(exclude_none=True, by_alias=True)

    assert data["name"] == "Test Company"
    assert data["_id"] == "12345"  # Should use alias
    assert data["externalId"] == "ext-123"  # Should use alias
    assert data["sourceId"] == "src-456"  # Should use alias
    assert data["coOwner"] == "user-101"  # Should use alias
    assert data["phonePrimary"] == "+1-555-0123"  # Should use alias
    assert data["custom"] == {"key": "value"}

    # Ensure excluded None fields are not present
    assert "owner" not in data
    assert "phase" not in data


def test_company_deserialization_from_api_response():
    """Test parsing Company from API response JSON."""
    api_response = {
        "_id": "company-123",
        "name": "API Company",
        "externalId": "api-ext-456",
        "owner": "user-789",
        "phase": "prospect",
        "status": "prospect",
        "domains": ["api-example.com"],
        "mrr": 2500.0,
        "arr": 30000.0,
        "h": 90,
        "custom": {"tier": "Enterprise", "region": "US-West"},
    }

    company = Company(**api_response)

    assert company.name == "API Company"
    assert company.id == "company-123"
    assert company.external_id == "api-ext-456"
    assert company.owner == "user-789"
    assert company.phase == "prospect"
    assert company.status == "prospect"
    assert company.domains == ["api-example.com"]
    assert company.mrr == 2500.0
    assert company.arr == 30000.0
    assert company.h == 90
    assert company.custom == {"tier": "Enterprise", "region": "US-West"}


def test_company_validation_error_missing_name():
    """Test that validation fails when required name field is missing."""
    with pytest.raises(ValueError) as exc_info:
        Company()  # Missing required name field

    assert "name" in str(exc_info.value)


def test_company_custom_fields_default_factory():
    """Test that custom fields use default factory correctly."""
    company1 = Company(name="Company 1")
    company2 = Company(name="Company 2")

    # Both should have empty dict for custom fields
    assert company1.custom == {}
    assert company2.custom == {}

    # They should be independent (not same object)
    assert company1.custom is not company2.custom


def test_company_field_population_by_name():
    """Test that fields can be populated by both name and alias."""
    # Using field names (snake_case)
    company1 = Company(
        name="Test 1",
        external_id="ext-1",
        source_id="src-1",
        co_owner="owner-1",
        phone_primary="+1-555-0001",
    )

    # Using aliases (camelCase)
    company2 = Company(
        name="Test 2",
        externalId="ext-2",
        sourceId="src-2",
        coOwner="owner-2",
        phonePrimary="+1-555-0002",
    )

    assert company1.external_id == "ext-1"
    assert company1.source_id == "src-1"
    assert company1.co_owner == "owner-1"
    assert company1.phone_primary == "+1-555-0001"

    assert company2.external_id == "ext-2"
    assert company2.source_id == "src-2"
    assert company2.co_owner == "owner-2"
    assert company2.phone_primary == "+1-555-0002"


def test_company_model_json_schema():
    """Test that the model generates a valid JSON schema."""
    schema = Company.model_json_schema()

    # Check required fields
    assert "name" in schema["required"]
    assert len(schema["required"]) == 1  # Only name should be required

    # Check field definitions
    properties = schema["properties"]
    assert "name" in properties
    assert "_id" in properties  # Should be present with alias
    assert "externalId" in properties  # Should be present with alias
    assert "sourceId" in properties  # Should be present with alias
    assert "custom" in properties

    # Check field types
    assert properties["name"]["type"] == "string"
    assert properties["custom"]["type"] == "object"
    # In Pydantic v2, default factory fields don't show default in schema
    assert properties["custom"] is not None


# CRUD Tests for Companies Resource


def test_list_companies_success(async_client, httpx_mock):
    """Test listing all companies successfully."""
    mock_response = [
        {
            "_id": "company-1",
            "name": "Company A",
            "externalId": "ext-1",
            "status": "customer",
            "mrr": 1000.0,
        },
        {
            "_id": "company-2",
            "name": "Company B",
            "externalId": "ext-2",
            "status": "prospect",
            "mrr": 0.0,
        },
    ]

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies",
        json=mock_response,
    )

    companies = async_client.companies.list()

    assert len(companies) == 2
    assert companies[0].id == "company-1"
    assert companies[0].name == "Company A"
    assert companies[0].external_id == "ext-1"
    assert companies[0].status == "customer"
    assert companies[0].mrr == 1000.0

    assert companies[1].id == "company-2"
    assert companies[1].name == "Company B"
    assert companies[1].external_id == "ext-2"
    assert companies[1].status == "prospect"
    assert companies[1].mrr == 0.0


def test_list_companies_empty(async_client, httpx_mock):
    """Test listing companies when no companies exist."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies",
        json=[],
    )

    companies = async_client.companies.list()

    assert companies == []


def test_get_company_success(async_client, httpx_mock):
    """Test getting a specific company successfully."""
    mock_response = {
        "_id": "company-123",
        "name": "Test Company",
        "externalId": "ext-123",
        "status": "customer",
        "mrr": 2500.0,
        "custom": {"tier": "Enterprise"},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies/company-123",
        json=mock_response,
    )

    company = async_client.companies.get("company-123")

    assert company.id == "company-123"
    assert company.name == "Test Company"
    assert company.external_id == "ext-123"
    assert company.status == "customer"
    assert company.mrr == 2500.0
    assert company.custom == {"tier": "Enterprise"}


def test_get_company_not_found(async_client, httpx_mock):
    """Test getting a non-existent company raises error."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies/nonexistent",
        status_code=404,
        text="Company not found",
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        async_client.companies.get("nonexistent")

    assert exc_info.value.status_code == 404
    assert "Company not found" in exc_info.value.response_body


def test_create_company_success(async_client, httpx_mock):
    """Test creating a new company successfully."""
    new_company = Company(
        name="New Company",
        external_id="new-ext",
        status="prospect",
        custom={"industry": "Technology"},
    )

    mock_response = {
        "_id": "company-new",
        "name": "New Company",
        "externalId": "new-ext",
        "status": "prospect",
        "custom": {"industry": "Technology"},
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.planhat.com/companies",
        status_code=201,
        json=mock_response,
    )

    created_company = async_client.companies.create(new_company)

    assert created_company.id == "company-new"
    assert created_company.name == "New Company"
    assert created_company.external_id == "new-ext"
    assert created_company.status == "prospect"
    assert created_company.custom == {"industry": "Technology"}


def test_create_company_validation_error(async_client, httpx_mock):
    """Test creating a company with invalid data raises error."""
    httpx_mock.add_response(
        method="POST",
        url="https://api.planhat.com/companies",
        status_code=400,
        text="Invalid request: missing required field",
    )

    company = Company(name="Test Company")

    with pytest.raises(APIError) as exc_info:
        async_client.companies.create(company)

    assert exc_info.value.status_code == 400
    assert "Invalid request" in str(exc_info.value)


def test_update_company_success(async_client, httpx_mock):
    """Test updating an existing company successfully."""
    updated_company = Company(
        name="Updated Company",
        status="customer",
        mrr=5000.0,
    )

    mock_response = {
        "_id": "company-123",
        "name": "Updated Company",
        "status": "customer",
        "mrr": 5000.0,
    }

    httpx_mock.add_response(
        method="PUT",
        url="https://api.planhat.com/companies/company-123",
        json=mock_response,
    )

    result = async_client.companies.update("company-123", updated_company)

    assert result.id == "company-123"
    assert result.name == "Updated Company"
    assert result.status == "customer"
    assert result.mrr == 5000.0


def test_update_company_not_found(async_client, httpx_mock):
    """Test updating a non-existent company raises error."""
    httpx_mock.add_response(
        method="PUT",
        url="https://api.planhat.com/companies/nonexistent",
        status_code=404,
        text="Company not found",
    )

    company = Company(name="Test Company")

    with pytest.raises(InvalidRequestError) as exc_info:
        async_client.companies.update("nonexistent", company)

    assert exc_info.value.status_code == 404
    assert "Company not found" in exc_info.value.response_body


def test_delete_company_success(async_client, httpx_mock):
    """Test deleting a company successfully."""
    httpx_mock.add_response(
        method="DELETE",
        url="https://api.planhat.com/companies/company-123",
        status_code=204,
    )

    # Should not raise any exception
    async_client.companies.delete("company-123")


def test_delete_company_not_found(async_client, httpx_mock):
    """Test deleting a non-existent company raises error."""
    httpx_mock.add_response(
        method="DELETE",
        url="https://api.planhat.com/companies/nonexistent",
        status_code=404,
        text="Company not found",
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        async_client.companies.delete("nonexistent")

    assert exc_info.value.status_code == 404
    assert "Company not found" in exc_info.value.response_body


def test_authentication_error(async_client, httpx_mock):
    """Test authentication error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies",
        status_code=401,
        text="Invalid API key",
    )

    with pytest.raises(AuthenticationError) as exc_info:
        async_client.companies.list()

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.response_body


def test_rate_limit_error(async_client, httpx_mock):
    """Test rate limit error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies",
        status_code=429,
        text="Rate limit exceeded",
    )

    with pytest.raises(RateLimitError) as exc_info:
        async_client.companies.list()

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value)


def test_server_error(async_client, httpx_mock):
    """Test server error handling."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies",
        status_code=500,
        text="Internal server error",
    )

    with pytest.raises(ServerError) as exc_info:
        async_client.companies.list()

    assert exc_info.value.status_code == 500
    assert "Internal server error" in str(exc_info.value)


def test_generic_api_error(async_client, httpx_mock):
    """Test generic API error handling for other 4xx errors."""
    httpx_mock.add_response(
        method="GET",
        url="https://api.planhat.com/companies",
        status_code=422,
        text="Unprocessable entity",
    )

    with pytest.raises(APIError) as exc_info:
        async_client.companies.list()

    assert exc_info.value.status_code == 422
    assert "Unprocessable entity" in str(exc_info.value)
