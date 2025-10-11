## MechBook API Documentation (v1)

Simple, consistent reference for frontend development.

### Base
- **Base URL**: `/api/v1`
- **Authentication**: Cookie-based JWT (`access_token`, HttpOnly)
  - Set automatically by the login endpoint
  - Valid for 1 hour
  - Send the cookie with all authenticated requests
- **Content-Type**: `application/json`

### Multi-Tenancy
**Each mechanic has isolated data space:**
- Each mechanic sees **only their own** data (clients, vehicles, repairs)
- Mechanic A **cannot** view/edit Mechanic B's data
- Duplicates are checked **per mechanic**:
  - **Name + Last Name**: Mechanic A and B can both have a client "John Smith"
  - **Phone**: Mechanic A and B can both have a client with the same phone number
  - **PESEL**: Mechanic A and B can both have a client with the same PESEL
  - **VIN**: Mechanic A and B can both have a vehicle with the same VIN
- Within **one** mechanic, duplicates are blocked (409 Conflict)

**Frontend implications:**
- Every request is automatically filtered by `mechanic_id` from JWT token
- You don't need to pass `mechanic_id` in requests - it's extracted from cookie
- `404 Not Found` can mean "doesn't exist" OR "belongs to another mechanic"

---

## Authentication

### Register
**Create a new mechanic account**
- **POST** `/auth/register`
- **Auth required**: No
- **Body**:
```json
{
  "email": "ava.williams@example.com",
  "name": "Ava Williams",
  "password": "Secret123"
}
```
- **Validation**:
  - `email`: Valid email format
  - `password`: 5-15 characters
- **Response** (200):
```json
{
  "id": 1,
  "email": "ava.williams@example.com"
}
```
- **Errors**:
  - `400`: Email already registered
  - `422`: Validation error (invalid email, password too short/long)

---

### Login
**Authenticate and receive auth cookie**
- **POST** `/auth/login`
- **Auth required**: No
- **Body**:
```json
{
  "email": "ava.williams@example.com",
  "password": "Secret123"
}
```
- **Response** (200, sets `access_token` cookie):
```json
{
  "message": "Login successful"
}
```
- **Errors**:
  - `404`: Mechanic not found
  - `400`: Incorrect password
  - `422`: Validation error

---

### Get Current Mechanic
**Get authenticated mechanic details**
- **GET** `/auth/get_mechanics`
- **Auth required**: Yes
- **Response** (200):
```json
{
  "id": 1,
  "email": "ava.williams@example.com"
}
```
- **Errors**:
  - `401`: Not authenticated (missing or invalid token)

---

### Logout
**Clear authentication cookie**
- **POST** `/auth/logout`
- **Auth required**: No (works regardless of auth state)
- **Response** (200, clears `access_token` cookie):
```json
{
  "message": "Logged out"
}
```

---

### Password Recovery
**Request password reset email**
- **POST** `/auth/recover-password`
- **Auth required**: No
- **Body**:
```json
{
  "email": "ava.williams@example.com"
}
```
- **Response** (200):
```json
{
  "message": "If an account with that email exists, a password reset email has been sent."
}
```
- **Note**: Returns same message regardless of email existence (prevents user enumeration)

---

### Password Reset
**Reset password using token from email**
- **POST** `/auth/reset-password`
- **Auth required**: No
- **Body**:
```json
{
  "token": "<reset-token-from-email>",
  "new_password": "NewSecret123"
}
```
- **Validation**:
  - `new_password`: 5-15 characters
- **Response** (200):
```json
{
  "message": "Password has been reset successfully."
}
```

---

## Clients

### List All Clients
**Get all clients with pagination**
- **GET** `/clients/`
- **Auth required**: Yes
- **Query Parameters**:
  - `page`: Page number (default: 1, min: 1)
  - `size`: Clients per page (default: 10, min: 1, max: 100)
- **Response** (200):
```json
[
  {
    "id": 15,
    "name": "Emma",
    "last_name": "Davis",
    "phone": "+1-202-555-0115",
    "pesel": "98765432109"
  },
  {
    "id": 14,
    "name": "Oliver",
    "last_name": "Wilson",
    "phone": "+1-202-555-0114",
    "pesel": null
  },
  {
    "id": 13,
    "name": "Sophia",
    "last_name": "Martinez",
    "phone": "+1-202-555-0113",
    "pesel": "11223344556"
  }
]
```
- **Notes**:
  - Returns clients ordered by **newest first** (ID descending)
  - Only returns clients belonging to the authenticated mechanic
  - Empty list `[]` if no clients found
  - If `size > 100`, automatically limited to 100
  - If `page` or `size` < 1, defaults to valid values
- **Errors**:
  - `401`: Not authenticated

---

### Count Clients
**Get total count of clients**
- **GET** `/clients/count`
- **Auth required**: Yes
- **Response** (200):
```json
{
  "count": 47
}
```
- **Notes**:
  - Returns total number of clients for the authenticated mechanic
  - Useful for pagination (calculate total pages)
  - Returns 0 if no clients
- **Errors**:
  - `401`: Not authenticated

---

### Create Client
**Create a new client**
- **POST** `/clients/`
- **Auth required**: Yes
- **Body**:
```json
{
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",
  "pesel": "12345678901"
}
```
- **Fields**:
  - `name`: **Required** (auto-capitalized)
  - `last_name`: **Required** (auto-capitalized)
  - `phone`: *Optional* (any format)
  - `pesel`: *Optional* (must be exactly 11 characters if provided)
- **Response** (201):
```json
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",
  "pesel": "12345678901"
}
```
- **Uniqueness Rules** (per mechanic):
  - **Name + Last Name**: You cannot have two clients "John Smith"
  - **Phone**: You cannot have two clients with the same phone number
  - **PESEL**: You cannot have two clients with the same PESEL
  - **Note**: Another mechanic CAN have a client with the same data
- **Errors**:
  - `401`: Not authenticated
  - `409`: Client with this name+last_name, phone, or PESEL already exists **for your mechanic account**
  - `422`: Validation error (PESEL not 11 characters)

---

### Get Client
**Retrieve client details by ID**
- **GET** `/clients/{client_id}`
- **Auth required**: Yes
- **Response** (200):
```json
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",
  "pesel": "12345678901"
}
```
- **Errors**:
  - `401`: Not authenticated
  - `404`: Client not found **or belongs to another mechanic**

---

### Update Client
**Update client details (partial updates allowed)**
- **PUT** `/clients/{client_id}`
- **Auth required**: Yes
- **Body** (all fields optional):
```json
{
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0177",
  "pesel": "12345678902"
}
```
- **Validation**:
  - `pesel`: Must be exactly 11 characters if provided
- **Response** (200): Same as Get Client
- **Errors**:
  - `401`: Not authenticated
  - `404`: Client not found
  - `422`: Validation error

---

### Delete Client
**Delete a client**
- **DELETE** `/clients/{client_id}`
- **Auth required**: Yes
- **Response**: `204 No Content`
- **Note**: 
  - **Cascade deletion**: Automatically deletes all client's vehicles and their repairs
  - Works **only on your clients** - you cannot delete another mechanic's client
- **Errors**:
  - `401`: Not authenticated
  - `404`: Client not found **or belongs to another mechanic**

---

## Vehicles

### Create Vehicle
**Create a new vehicle with client association**
- **POST** `/vehicles/`
- **Auth required**: Yes
- **Body** (Option 1: Existing client):
```json
{
  "mark": "BMW",
  "model": "X5",
  "vin": "WAUZZZ8P79A000000",
  "client_id": 10
}
```
- **Body** (Option 2: Create new client inline):
```json
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
```
- **Fields**:
  - `mark`: **Required**
  - `model`: **Required**
  - `vin`: *Optional* (must be exactly 17 characters if provided)
  - `client_id` OR `client`: **One required**
- **Response** (201):
```json
{
  "vehicle_id": 42
}
```
- **Uniqueness Rules** (per mechanic):
  - **VIN**: You cannot have two vehicles with the same VIN
  - **Note**: Another mechanic CAN have a vehicle with the same VIN
- **Errors**:
  - `400`: Missing client data OR client_id belongs to another mechanic
  - `401`: Not authenticated
  - `409`: Vehicle with this VIN already exists **for your mechanic account**
  - `422`: Validation error (VIN not 17 characters)

---

### Get Vehicle
**Retrieve vehicle details by ID**
- **GET** `/vehicles/{vehicle_id}`
- **Auth required**: Yes
- **Response** (200):
```json
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
```
- **Note**: 
  - Updates `last_view_data` timestamp when accessed
  - Returns **only your vehicles** - cannot access vehicles of other mechanics
- **Errors**:
  - `401`: Not authenticated
  - `404`: Vehicle not found **or belongs to another mechanic**

---

### Update Vehicle
**Update vehicle details (partial updates allowed)**
- **PATCH** `/vehicles/{vehicle_id}`
- **Auth required**: Yes
- **Body** (all fields optional):
```json
{
  "mark": "Audi",
  "model": "A6",
  "vin": "WAUZZZ8K9BA000001",
  "client_id": 11
}
```
- **Validation**:
  - `vin`: Must be exactly 17 characters if provided
- **Response** (200): Same as Get Vehicle
- **Errors**:
  - `401`: Not authenticated
  - `404`: Vehicle not found
  - `422`: Validation error

---

### Recently Viewed Vehicles
**Get list of recently viewed vehicles with pagination**
- **GET** `/vehicles/recent?page=1&size=8`
- **Auth required**: Yes
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `size`: Items per page (default: 8)
- **Response** (200):
```json
[
  {
    "id": 42,
    "model": "A4",
    "mark": "Audi",
    "client": {
      "id": 10,
      "name": "Ava",
      "last_name": "Williams"
    }
  }
]
```
- **Note**: Returns recently viewed vehicles ordered by `last_view_data` (most recent first)
- **Errors**:
  - `401`: Not authenticated

---

### Delete Vehicle
**Delete a vehicle**
- **DELETE** `/vehicles/{vehicle_id}`
- **Auth required**: Yes
- **Response**: `204 No Content`
- **Note**: 
  - **Cascade deletion**: Automatically deletes all repairs for this vehicle
  - Removes vehicle from search index
  - Works **only on your vehicles** - you cannot delete another mechanic's vehicle
- **Errors**:
  - `401`: Not authenticated
  - `404`: Vehicle not found **or belongs to another mechanic**

---

### Get Client Vehicles
**Get paginated list of vehicles for a specific client**
- **GET** `/clients/{client_id}/vehicles?page=1&size=3`
- **Auth required**: Yes
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `size`: Items per page (default: 3)
- **Response** (200):
```json
[
  {
    "id": 42,
    "model": "A4",
    "mark": "Audi"
  },
  {
    "id": 43,
    "model": "X5",
    "mark": "BMW"
  }
]
```
- **Note**: 
  - Returns vehicles **only for your clients**
  - Returns empty list if client doesn't have vehicles
- **Errors**:
  - `401`: Not authenticated
  - `404`: Client not found **or belongs to another mechanic**

---

## Repairs

All repair endpoints are nested under vehicles: `/vehicles/{vehicle_id}/repairs/`

### Create Repair
**Log a new repair for a vehicle**
- **POST** `/vehicles/{vehicle_id}/repairs/`
- **Auth required**: Yes
- **Body**:
```json
{
  "name": "Oil change",
  "repair_description": "Used OEM filter and 5W-30 synthetic oil",
  "price": 120.0,
  "repair_date": "2025-10-08T14:30:00Z"
}
```
- **Fields**:
  - `name`: **Required**
  - `repair_date`: **Required** (ISO 8601 datetime)
  - `repair_description`: *Optional*
  - `price`: *Optional* (can be null for warranty repairs)
- **Response** (201):
```json
{
  "id": 7,
  "name": "Oil change",
  "repair_description": "Used OEM filter and 5W-30 synthetic oil",
  "price": 120.0,
  "repair_date": "2025-10-08T14:30:00Z",
  "vehicle": {
    "id": 42,
    "model": "A4",
    "mark": "Audi",
    "client": {
      "id": 10,
      "name": "Ava",
      "last_name": "Williams"
    }
  }
}
```
- **Errors**:
  - `401`: Not authenticated
  - `404`: Vehicle not found
  - `422`: Validation error

---

### List Repairs
**Get paginated list of repairs for a vehicle**
- **GET** `/vehicles/{vehicle_id}/repairs/?page=1&size=10`
- **Auth required**: Yes
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `size`: Items per page (default: 10)
- **Response** (200):
```json
[
  {
    "id": 7,
    "name": "Oil change",
    "price": 120.0,
    "repair_date": "2025-10-08T14:30:00Z"
  },
  {
    "id": 8,
    "name": "Brake service",
    "price": null,
    "repair_date": "2025-10-15T10:00:00Z"
  }
]
```
- **Note**: Results ordered by `repair_date` descending
- **Errors**:
  - `401`: Not authenticated

---

### Get Repair
**Retrieve repair details by ID**
- **GET** `/vehicles/{vehicle_id}/repairs/{repair_id}`
- **Auth required**: Yes
- **Response** (200):
```json
{
  "id": 7,
  "name": "Oil change",
  "repair_description": "Used OEM filter and 5W-30 synthetic oil",
  "price": 120.0,
  "repair_date": "2025-10-08T14:30:00Z",
  "vehicle": {
    "id": 42,
    "model": "A4",
    "mark": "Audi",
    "client": {
      "id": 10,
      "name": "Ava",
      "last_name": "Williams"
    }
  }
}
```
- **Note**: 
  - Updates `last_seen` timestamp when accessed
  - Returns **only repairs for your vehicles**
- **Errors**:
  - `401`: Not authenticated
  - `404`: Repair not found **or belongs to vehicle of another mechanic**

---

### Update Repair
**Update repair details (partial updates allowed)**
- **PATCH** `/vehicles/{vehicle_id}/repairs/{repair_id}`
- **Auth required**: Yes
- **Body** (all fields optional):
```json
{
  "name": "Oil change premium",
  "repair_description": "Premium synthetic oil",
  "price": 140.0,
  "repair_data": "2025-10-09T14:30:00Z"
}
```
- **Note**: Field name is `repair_data` (typo in schema, will be fixed)
- **Response**: `204 No Content`
- **Errors**:
  - `401`: Not authenticated
  - `404`: Repair not found
  - `422`: Validation error

---

### Delete Repair
**Delete a repair**
- **DELETE** `/vehicles/{vehicle_id}/repairs/{repair_id}`
- **Auth required**: Yes
- **Response**: `204 No Content`
- **Errors**:
  - `401`: Not authenticated
  - `404`: Repair not found

---

## Search

### Search
**Unified search across clients and vehicles**
- **GET** `/search/?q=query`
- **Auth required**: Yes
- **Query Parameters**:
  - `q`: **Required** - Search query string
- **Response** (200):
```json
[
  {
    "id": 10,
    "type": "client",
    "name": "Ava Williams",
    "mark": null,
    "model": null
  },
  {
    "id": 42,
    "type": "vehicle",
    "name": "Audi A4",
    "mark": null,
    "model": null
  }
]
```
- **Features**:
  - **Fuzzy matching**: Tolerates typos and spelling errors
  - **Multi-field search**: Searches client names, phone numbers, vehicle marks, models, and VINs
  - **Ranking**: Clients ranked higher than vehicles
  - **Flexible matching**: Order-independent ("Williams Ava" matches "Ava Williams")
  - **Multi-tenancy**: Searches **only your data** - other mechanics' data is invisible
- **Errors**:
  - `401`: Not authenticated
  - `422`: Missing query parameter

---

## Response Schemas

### MechanicOut
```json
{
  "id": 1,
  "email": "ava.williams@example.com"
}
```

### ClientExtendedInfo
```json
{
  "id": 10,
  "name": "Noah",
  "last_name": "Johnson",
  "phone": "+1-202-555-0101",
  "pesel": "12345678901"
}
```
**Note**: `phone` and `pesel` can be `null`

### ClientBasicInfo
```json
{
  "id": 10,
  "name": "Ava",
  "last_name": "Williams"
}
```

### VehicleExtendedInfo
```json
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
```
**Note**: `vin`, `phone`, and `pesel` can be `null`

### VehicleBasicInfo
```json
{
  "id": 42,
  "model": "A4",
  "mark": "Audi",
  "client": {
    "id": 10,
    "name": "Ava",
    "last_name": "Williams"
  }
}
```

### RepairExtendedInfo
```json
{
  "id": 7,
  "name": "Oil change",
  "repair_description": "Used OEM filter",
  "price": 120.0,
  "repair_date": "2025-10-08T14:30:00Z",
  "vehicle": {
    "id": 42,
    "model": "A4",
    "mark": "Audi",
    "client": {
      "id": 10,
      "name": "Ava",
      "last_name": "Williams"
    }
  }
}
```
**Note**: `repair_description` and `price` can be `null`

### RepairBasicInfo
```json
{
  "id": 7,
  "name": "Oil change",
  "price": 120.0,
  "repair_date": "2025-10-08T14:30:00Z"
}
```
**Note**: `price` can be `null`

### SearchResult
```json
{
  "id": 42,
  "type": "client",
  "name": "Ava Williams",
  "mark": null,
  "model": null
}
```
**Note**: 
- `type`: "client" or "vehicle"
- For clients: `name` is filled, `mark`/`model` are null
- For vehicles: `name` is filled with "Mark Model", `mark`/`model` are null

---

## Error Responses

All error responses follow this format:
```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **204**: No Content (successful deletion/update)
- **400**: Bad Request (validation error, missing data)
- **401**: Unauthorized (missing or invalid auth token)
- **404**: Not Found
- **409**: Conflict (duplicate data)
- **422**: Unprocessable Entity (Pydantic validation error)
- **500**: Internal Server Error

---

## Authentication Flow

1. **Register**: `POST /auth/register` → Get mechanic ID
2. **Login**: `POST /auth/login` → Receive `access_token` cookie
3. **Make requests**: Include cookie automatically (HttpOnly)
4. **Check auth**: `GET /auth/get_mechanics` → Verify logged in
5. **Logout**: `POST /auth/logout` → Clear cookie

