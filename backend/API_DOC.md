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
- Response (201)
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
- Response (200, sets `access_token` cookie)
{
  "message": "Login successful"
}

### Current mechanic
- GET `/auth/get_mechanics` (auth required)
- Response (200)
{
  "id": 1,
  "email": "ava.williams@example.com"
}

### Logout
- POST `/auth/logout` (auth required)
- Response (200, clears `access_token` cookie)
{
  "message": "Logged out"
}

### Password recovery
- POST `/auth/recover-password`
- Body
{
  "email": "ava.williams@example.com"
}
- Response (200)
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
- Response (200)
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
  "phone": "+1-202-555-0101",    // OPTIONAL
  "pesel": "12345678901"         // OPTIONAL (exactly 11 chars)
}
- Response (201)
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",    // or null
  "pesel": "12345678901"         // or null
}

### Get client
- GET `/clients/{client_id}` (auth required)
- Response (200)
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",    // or null
  "pesel": "12345678901"         // or null
}

### Update client
- PUT `/clients/{client_id}` (auth required)
- Body (partial allowed)
{
  "name": "Noah",                // OPTIONAL
  "last_name": "Johnson",        // OPTIONAL  
  "phone": "+1-202-555-0177",    // OPTIONAL
  "pesel": "12345678902"         // OPTIONAL (exactly 11 chars)
}
- Response (200): same shape as Get client

### Delete client
- DELETE `/clients/{client_id}` (auth required) → 204 No Content

## Vehicles

### Create vehicle
- POST `/vehicles/` (auth required)
- Two options
  - With existing client:
  {
    "mark": "BMW",
    "model": "X5",
    "vin": "WAUZZZ8P79A000000",    // OPTIONAL (exactly 17 chars)
    "client_id": 10
  }
  - With inline new client:
  {
    "mark": "Audi",
    "model": "A4",
    "vin": "WAUZZZ8K9BA000000",    // OPTIONAL (exactly 17 chars)
    "client": {
      "name": "Ava",
      "last_name": "Williams",
      "phone": "+1-202-555-0123",  // OPTIONAL
      "pesel": "98765432109"       // OPTIONAL (exactly 11 chars)
    }
  }
- Response (201)
{
  "vehicle_id": 42
}

### Update vehicle
- PATCH `/vehicles/{vehicle_id}` (auth required)
- Body (partial allowed)
{
  "mark": "Audi",                    // OPTIONAL
  "model": "A6",                     // OPTIONAL
  "vin": "WAUZZZ8K9BA000001",        // OPTIONAL (exactly 17 chars)
  "client_id": 11                    // OPTIONAL
}
- Response (200): VehicleExtendedInfo

### Recently viewed vehicles
- GET `/vehicles/recent` (auth required)
- Response (200): VehicleBasicInfo[]

### Vehicle detail
- GET `/vehicles/{vehicle_id}` (auth required)
- Response (200)
{
  "id": 42,
  "model": "A4",
  "mark": "Audi",
  "vin": "WAUZZZ8K9BA000000",        // or null
  "client": {
    "id": 10,
    "name": "Ava",
    "last_name": "Williams",
    "phone": "+1-202-555-0123",      // or null
    "pesel": "98765432109"           // or null
  }
}

### Delete vehicle
- DELETE `/vehicles/{vehicle_id}` (auth required) → 204 No Content

## Repairs (per vehicle)

### Create repair
- POST `/vehicles/{vehicle_id}/repairs/` (auth required)
- Body
{
  "name": "Oil change",
  "repair_description": "OEM filter",   // OPTIONAL
  "price": 120.0,                       // OPTIONAL
  "repair_date": "2025-08-08T12:00:00Z"
}
- Response (201): RepairExtendedInfo

### List repairs
- GET `/vehicles/{vehicle_id}/repairs/?page=1&size=10` (auth required)
- Response (200): RepairBasicInfo[]

### Update repair
- PATCH `/vehicles/{vehicle_id}/repairs/{repair_id}` (auth required)
- Body (partial allowed)
{
  "name": "Oil change premium",         // OPTIONAL
  "repair_description": "Premium OEM", // OPTIONAL
  "price": 140.0,                      // OPTIONAL
  "repair_data": "2025-08-09T12:00:00Z" // OPTIONAL (note: typo in schema)
}
- Response → 204 No Content

### Repair detail
- GET `/vehicles/{vehicle_id}/repairs/{repair_id}` (auth required)
- Response (200): RepairExtendedInfo

### Delete repair
- DELETE `/vehicles/{vehicle_id}/repairs/{repair_id}` (auth required) → 204 No Content

## Search

### Search all
- GET `/search/?q=term`
- Response (200): SearchResult[]
- Features:
  - Clients ranked first, then vehicles
  - Order-independent names ("Williams Ava" matches "Ava Williams")
  - Searches across client names, phone numbers, vehicle makes, models, VINs
  - Fuzzy matching enabled for typo tolerance

## Schemas (response shapes)

### ClientExtendedInfo
{ "id": 10, "name": "Noah", "last_name": "Johnson", "phone": "+1-202-555-0101", "pesel": "12345678901" }

### VehicleBasicInfo
{ "id": 42, "model": "A4", "mark": "Audi", "client": { "id": 10, "name": "Ava", "last_name": "Williams" } }

### VehicleExtendedInfo
{ "id": 42, "model": "A4", "mark": "Audi", "vin": "WAUZZZ8K9BA000000", "client": { "id": 10, "name": "Ava", "last_name": "Williams", "phone": "+1-202-555-0123", "pesel": "98765432109" } }

### RepairBasicInfo
{ "id": 7, "name": "Oil change", "price": 120.0, "repair_date": "2025-08-08T12:00:00Z" }

### RepairExtendedInfo
{ "id": 7, "name": "Oil change", "repair_description": "OEM filter", "price": 120.0, "repair_date": "2025-08-08T12:00:00Z", "vehicle": { "id": 42, "model": "A4", "mark": "Audi", "client": { "id": 10, "name": "Ava", "last_name": "Williams" } } }

### SearchResult
{ "id": 42, "type": "client", "name": "Ava Williams", "mark": null, "model": null }





