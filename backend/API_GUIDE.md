## MechBook API Doc (v1)

Simple, consistent reference for frontend dev.

### Base
- Base URL: `/api/v1`
- Auth: Cookie-based JWT set by the login endpoint (`access_token`, HttpOnly). Send the cookie on all authenticated requests.

## Authentication

### Register
- POST `/auth/register`
- Body
{
  "email": "ava.williams@example.com",
  "name": "Ava Williams",
  "password": "Secret123"
}
- Response
{
  "id": 1,
  "email": "ava.williams@example.com"
}

### Login (sets auth cookie)
- POST `/auth/login`
- Body
{
  "email": "ava.williams@example.com",
  "password": "Secret123"
}
- Response (and sets `access_token` cookie)
{
  "message": "Login successful"
}

### Current mechanic
- GET `/auth/get_mechanics`
- Response
{
  "id": 1,
  "email": "ava.williams@example.com"
}

### Password recovery
- POST `/auth/recover-password`
- Body
{
  "email": "ava.williams@example.com"
}
- Response
{
  "message": "If an account with that email exists, a password reset email has been sent."
}

### Password reset
- POST `/auth/reset-password`
- Body
{
  "token": "<reset-token>",
  "new_password": "NewSecret123"
}
- Response
{
  "message": "Password has been reset successfully."
}

## Clients

### Create client
- POST `/clients/` (auth required)
- Body
{
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",    OPTIONAL
  "pesel": "12345678901"         OPTIONAL
}
- Response
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101" or None,
  "pesel": "12345678901" or None
}

### Get client
- GET `/clients/{client_id}`
- Response
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101", None,   
  "pesel": "12345678901", None
}

### Update client
- PUT `/clients/{client_id}`
- Body (partial allowed)
{
  "phone": "+1-202-555-0177"
}
- Response: same shape as Get client

### Delete client
- DELETE `/clients/{client_id}` → 204 No Content

## Vehicles

### Create vehicle
- POST `/vehicles/` (auth required)
- Two options
  - With existing client:
  {
    "mark": "BMW",
    "model": "X5",
    "vin": "WAUZZZ8P79A000000",
    "client_id": 10
  }
  - With inline new client:
  {
    "mark": "Audi",
    "model": "A4",
    "vin": "WAUZZZ8K9BA000000",
    "client": {
      "name": "Ava",
      "last_name": "Williams",
      "phone": "+1-202-555-0123",
      "pesel": "98765432109"
    }
  }
- Response
{
  "vehicle_id": 42
}

### Update vehicle
- PATCH `/vehicles/{vehicle_id}`
- Body (partial allowed)
{
  "mark": "Audi",
  "model": "A6"
}
- Response: VehicleExtendedInfo

### Recently viewed
- GET `/vehicles/recent`
- Response: VehicleBasicInfo[]

### Vehicle detail
- GET `/vehicles/{vehicle_id}`
- Response
{
  "id": 42,
  "model": "A4",
  "mark": "Audi",
  "vin": "WAUZZZ8K9BA000000",
  "client": {
    "id": 10,
    "name": "Ava",
    "last_name": "Williams",
    "phone": "+1-202-555-0123",
    "pesel": "98765432109"
  }
}

### Delete vehicle
- DELETE `/vehicles/{vehicle_id}` → 204 No Content

## Repairs (per vehicle)

### Create repair
- POST `/vehicles/{vehicle_id}/repairs/`
- Body
{
  "name": "Oil change",
  "repair_description": "OEM filter",
  "price": 120.0,
  "repair_date": "2025-08-08T12:00:00Z"
}
- Response: RepairExtendedInfo

### List repairs
- GET `/vehicles/{vehicle_id}/repairs/?page=1&size=10`
- Response: RepairBasicInfo[]

### Update repair
- PATCH `/vehicles/{vehicle_id}/repairs/{repair_id}`
- Body (partial allowed)
{
  "price": 140.0
}
- Response → 204 No Content

### Repair detail
- GET `/vehicles/{vehicle_id}/repairs/{repair_id}`
- Response: RepairExtendedInfo

### Delete repair
- DELETE `/vehicles/{vehicle_id}/repairs/{repair_id}` → 204 No Content

## Search

### Search all
- GET `/search/?q=term`
- Response: SearchResult[]
- Clients are ranked first; vehicles related to matched clients follow.
- Order-independent names ("Williams Ava" matches "Ava Williams"). Typo tolerance enabled.

## Schemas (shapes)

### VehicleBasicInfo
{ "id": 42, "model": "A4", "mark": "Audi", "client": { "id": 10, "name": "Ava", "last_name": "Williams" } }

### VehicleExtendedInfo
{ "id": 42, "model": "A4", "mark": "Audi", "vin": "WAUZZZ8K9BA000000", "client": { "id": 10, "name": "Ava", "last_name": "Williams", "phone": "+1-202-555-0123", "pesel": "98765432109" } }

### RepairBasicInfo
{ "id": 7, "name": "Oil change", "price": 120.0, "repair_date": "2025-08-08T12:00:00Z" }

### RepairExtendedInfo
{ "id": 7, "name": "Oil change", "repair_description": "OEM filter", "price": 120.0, "repair_date": "2025-08-08T12:00:00Z", "vehicle": { "id": 42, "model": "A4", "mark": "Audi", "client": { "id": 10, "name": "Ava", "last_name": "Williams" } } }

### ClientExtendedInfo
{ "id": 10, "name": "Noah", "last_name": "Johnson", "phone": "+1-202-555-0101", "pesel": "12345678901" }

## Notes & status codes
- Most routes require the auth cookie from `/auth/login`.
- 201 on create, 200 on reads, 204 on updates (repairs) and deletes.
- 400 for validation/business rule errors (e.g., duplicate VIN/phone), 404 for not found.
- Sensitive fields `pesel` and `vin` are encrypted at rest in the DB; API returns decrypted values.
- Search is backed by Elasticsearch and reflects DB changes near‑real‑time.

## Quick curl examples

### Login
curl -i -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ava.williams@example.com","password":"Secret123"}'

### Create client (send cookie from login response)
curl -i -X POST http://localhost:8000/api/v1/clients/ \
  -H 'Content-Type: application/json' \
  -H 'Cookie: access_token=<paste-cookie>' \
  -d '{"name":"Noah","last_name":"Johnson","phone":"+1-202-555-0101","pesel":"12345678901"}'


