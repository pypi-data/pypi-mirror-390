# Planhat API Documentation & Development Guide

This file contains comprehensive API documentation and key development context for building the PyPlanhat SDK.

## API Base URLs

### Main API
- **Base URL**: `https://api.planhat.com` (for general API requests)
- **Analytics URL**: `https://analytics.planhat.com` (for user tracking and metrics)

## Authentication & Security

### API Authentication
- **Method**: Bearer token or Basic Auth
- **Header**: `Authorization: Bearer {{apiAccessToken}}` or `Authorization: Basic {{token}}:`
- **Token Source**: Generated via **Private Apps** in Planhat Settings
- **Token Properties**: Static tokens, belong to Private Apps, scope limited by app permissions
- **Token Management**: Disable by disabling Private App or removing token (permanent invalidation)

### Rate Limits & Quotas
- **Main API**: 200 calls/minute (soft limit), 150 requests/second (hard limit), 50 parallel requests burst
- **Bulk Operations**: 5,000 items per request limit
- **Analytics Endpoint**: No rate limits, handles high volumes
- **Request Body**: 32MB hard limit (~150,000 items)
- **Bulk Strategy**: Execute sequentially for data integrity (not parallel)

### Security Compliance
- **Certifications**: ISO 27001, SOC 2 Type II certified
- **Data Protection**: TLS 1.2/1.3 in-transit, AES-256 at-rest
- **Infrastructure**: Google Cloud Platform (GCP) with secure multi-location storage
- **Compliance**: GDPR & CCPA compliant
- **Monitoring**: 24/7 threat monitoring with dedicated security team
- **Access Control**: SSO, SAML 2.0, granular field-level permissions

## HTTP Response Codes (Bulk Operations)

| Code | Meaning | Error Handling |
|------|---------|---------------|
| 200 | All operations successful |
| 206 | Partial success - check `createdErrors`/`updatedErrors` |
| 400 | Bad request - missing/duplicate required fields |
| 403 | Permission error - insufficient rights |
| 500 | Server error - retry, contact support if persistent |

## Core API Patterns

### Bulk Upsert Operations
- **Purpose**: Create/update multiple records in single request
- **Identification**: Uses keyables for matching (`_id` > `sourceId` > `externalId`)
- **Keyable Hierarchy**: `_id` (highest) > `sourceId` > `externalId` (lowest)
- **Enduser Special**: Includes `email` as additional keyable for matching
- **Response Object**: Contains `created`, `updated`, `createdErrors`, `updatedErrors`, `permissionErrors`
- **Update Rule**: Keyable properties can only be updated with higher-priority keys

### Array Operations
- **Supported**: Add, Replace, Remove operations on multipicklist fields
- **Syntax**: `{"fieldName": {"$operation": ["value1", "value2"]}}`
- **Operations**: 
  - `Add`: Append new values to existing array
  - `Replace`: Replace entire array with new values  
  - `Remove`: Remove specific values from existing array

## Priority Resource Schemas

### Company Resource
**Required Fields**: `name` only

**Key Properties**:
- `_id` (objectId): Planhat native identifier
- `name` (string): Company name 
- `externalId` (string): Your system's company ID
- `sourceId` (string): Integration ID (Salesforce, Hubspot)
- `companyId` (objectId): Required for most object creation

**Core Fields**:
- `owner`, `coOwner` (objectId): Account Manager IDs
- `phase` (string): Lifecycle phase (matches Planhat phases)
- `status` (string): prospect/coming/customer/canceled/lost
- `domains` (array): Auto-generated from enduser emails
- `description` (string): Company description
- `address`, `country`, `city`, `zip`, `phonePrimary`, `web` (string): Contact info

**Financial Fields** (Auto-generated):
- `mrr`, `arr`, `nrr30`, `mrrTotal`, `nrrTotal`, `mrTotal`
- `renewalMrr`, `renewalArr`, `renewalDaysFromNow`
- `customerFrom`, `customerTo`, `lastRenewal`

**Health & Activity** (Auto-generated):
- `h` (integer): Health score
- `csmScore` (integer): CSM score 1-5
- `lastActive`, `lastTouch`, `lastTouchType`
- `alerts`, `lastActivities`

**Organization Support**:
- `orgRootId`, `orgPath`, `orgLevel`, `orgUnits`
- `orgMrr`, `orgArr`, `orgMrrTotal`, `orgArrTotal`, `orgHealthTotal`

**Custom Fields**:
- `custom` (object): Flexible custom data structure

### Enduser Resource  
**Required Fields**: `companyId` + (`email` OR `externalId` OR `sourceId`)

**Key Properties**:
- `_id` (objectId): Planhat native identifier
- `email` (string): Email address (primary identifier)
- `externalId` (string): Your system's user ID
- `sourceId` (string): Integration user ID
- `companyId` (objectId): Associated company ID

**Core Fields**:
- `firstName`, `lastName`, `name` (string): User identity
- `position` (string): Role/position (e.g., "CFO")
- `phone` (string): Phone number
- `featured`, `primary`, `archived` (boolean): User flags
- `tags` (array): User tags
- `otherEmails` (array): Additional emails

**Activity & Engagement** (Auto-generated):
- `lastActive`, `beats`, `beatsTotal`, `beatTrend`
- `convs14`, `convsTotal`, `experience`
- `lastTouch`, `lastTouchType`, `lastTouchByType`

**NPS Data** (Auto-generated):
- `nps`, `npsComment`, `npsDate`, `npsSent`, `npsUnsubscribed`

**Conversation Integration**:
- `lastActivities`: Recent conversation history
- `relatedEndusers`: Related/duplicate users

**Custom Fields**:
- `custom` (object): Flexible custom data structure

**Auto-Assignment**: If `companyId` omitted, auto-assigns by email domain matching

### Conversation Resource
**Required Fields**: `companyId` only

**Key Properties**:
- `_id` (objectId): Planhat native identifier  
- `externalId` (string): Your system's conversation ID
- `type` (string): Conversation type (defaults to "note")

**Core Fields**:
- `subject` (string): Conversation title
- `description` (string): Conversation content
- `snippet` (string): Formatted content
- `date`, `outDate`, `createDate` (string): Timestamps

**Participant Management**:
- `users` (array): User objects with `id`, `name`, `isOwner`
- `endusers` (array): Involved contact IDs (auto-generated)
- `userIds` (array): All participant IDs (auto-generated)

**Conversation Properties**:
- `starred`, `pinned`, `archived` (boolean): Status flags
- `isOpen` (boolean): Open/closed state (CRM integration)
- `tags`, `activityTags` (array): Categorization
- `hasAttachments`, `hasMore` (boolean): Content flags

**Advanced Features**:
- `emailTemplateIds` (array): Template integration
- `timeBucket` (array): Time analytics
- `sender` (array): Sender information
- `history` (array): Change history
- `isCustomType` (boolean): Custom conversation type
- `assigneeName`, `numberOfParts`, `numberOfRelevantParts` (string/int): Internal tracking

**Custom Fields**:
- `custom` (object): Flexible custom data structure

**Company Reference**: Supports `extid-{companyExternalId}` and `srcid-{companySourceId}` syntax

## SDK Development Priorities

### Phase 1: Companies (P1-1 to P1-5)
1. **P1-1**: Create Company Pydantic model with exact API schema
2. **P1-2**: Implement AsyncCompanies resource with full CRUD
3. **P1-3**: Write comprehensive async tests with error scenarios  
4. **P1-4**: Generate and verify sync code
5. **P1-5**: Validate full test suite and parity

### Phase 2: Resources (P2-1 to P2-3)
1. **P2-1**: Implement End Users resource (follow P1 pattern)
2. **P2-2**: Implement Conversations resource (follow P1 pattern)
3. **P2-3**: Wire resources to main client with namespace pattern

### Critical Implementation Requirements

#### Error Handling
- Map HTTP codes to custom exception hierarchy:
  - 401/403 → `AuthenticationError`
  - 400/404 → `InvalidRequestError`  
  - 429 → `RateLimitError`
  - 5xx → `ServerError`

#### Custom Fields Support
- All resources support `custom` object with flexible `Dict[str, Any]`
- Default to empty dict `{}` in Pydantic models
- Validate custom field schemas where possible

#### Testing Strategy
- Use `pytest-httpx` for HTTP mocking (NOT responses library)
- Test both success and error scenarios
- Validate async/sync test parity
- Test bulk operations with various array sizes

#### Code Generation
- All business logic in `src/pyplanhat/_async/` only
- Generate sync code via `unasync` with token replacements
- Commit both async source and generated sync code
- Use `.gitattributes` to mark generated files

## Development Workflow

### Quality Gates
Before any task completion, ensure:
1. ✅ **Tests Pass**: Both async and sync test suites
2. ✅ **Linting Clean**: `ruff check .` shows no issues
3. ✅ **Formatted**: `ruff format --check .` passes
4. ✅ **Type Checked**: `mypy src/` passes without errors
5. ✅ **Generated Code**: Sync code regenerated and committed
6. ✅ **Documentation**: Updated if API changes made

### Commands
```bash
# Development cycle
uv sync                    # Sync dependencies
uv run pytest -v           # Run tests
uv run ruff format .       # Format code
uv run ruff check .        # Lint code  
uv run mypy src/          # Type check
python scripts/generate_sync.py  # Generate sync code

# Quality checks
uv run pytest --cov=src/pyplanhat --cov-report=term-missing
```

This comprehensive guide provides the essential context for implementing a robust, production-ready PyPlanhat SDK following modern Python best practices and the project's async-first architecture.