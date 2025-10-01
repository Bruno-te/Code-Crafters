# MoMo SMS Transaction API Documentation

## Overview
This REST API provides CRUD operations for MoMo SMS transaction data. The API is built using Python's `http.server` module and implements Basic Authentication for security.

## Authentication
The API uses Basic Authentication. All requests must include an Authorization header with base64-encoded credentials.

**Username:** `admin`  
**Password:** `password123`  
**Authorization Header:** `Basic YWRtaW46cGFzc3dvcmQxMjM=`

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. GET /transactions
List all transactions.

**Request:**
```http
GET /transactions
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

**Response:**
```json
{
  "transactions": [
    {
      "id": "TXN000001",
      "date": "2024-01-15T10:30:00Z",
      "amount": 150.0,
      "currency": "GHS",
      "sender": "+233241234567",
      "recipient": "+233241234568",
      "message": "MoMo: You have received GHS 150.00...",
      "type": "credit",
      "status": "success",
      "fee": 0.0,
      "balance": 1250.0
    }
  ],
  "count": 25
}
```

### 2. GET /transactions/{id}
Get a specific transaction by ID.

**Request:**
```http
GET /transactions/TXN000001
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

**Response:**
```json
{
  "id": "TXN000001",
  "date": "2024-01-15T10:30:00Z",
  "amount": 150.0,
  "currency": "GHS",
  "sender": "+233241234567",
  "recipient": "+233241234568",
  "message": "MoMo: You have received GHS 150.00...",
  "type": "credit",
  "status": "success",
  "fee": 0.0,
  "balance": 1250.0
}
```

### 3. POST /transactions
Create a new transaction.

**Request:**
```http
POST /transactions
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Content-Type: application/json

{
  "amount": 100.00,
  "date": "2024-01-18T16:00:00Z",
  "message": "Test transaction",
  "type": "credit",
  "status": "success",
  "sender": "+233241234599",
  "recipient": "+233241234600"
}
```

**Response:**
```json
{
  "id": "TXN123456",
  "amount": 100.0,
  "date": "2024-01-18T16:00:00Z",
  "message": "Test transaction",
  "type": "credit",
  "status": "success",
  "sender": "+233241234599",
  "recipient": "+233241234600"
}
```

### 4. PUT /transactions/{id}
Update an existing transaction.

**Request:**
```http
PUT /transactions/TXN000001
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Content-Type: application/json

{
  "amount": 125.00,
  "message": "Updated message",
  "status": "completed"
}
```

**Response:**
```json
{
  "id": "TXN000001",
  "amount": 125.0,
  "message": "Updated message",
  "status": "completed",
  "date": "2024-01-15T10:30:00Z",
  "currency": "GHS",
  "sender": "+233241234567",
  "recipient": "+233241234568",
  "type": "credit",
  "fee": 0.0,
  "balance": 1250.0
}
```

### 5. DELETE /transactions/{id}
Delete a transaction.

**Request:**
```http
DELETE /transactions/TXN000001
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

**Response:**
```json
{
  "message": "Transaction 'TXN000001' deleted successfully",
  "deleted_transaction": {
    "id": "TXN000001",
    "date": "2024-01-15T10:30:00Z",
    "amount": 150.0,
    "currency": "GHS",
    "sender": "+233241234567",
    "recipient": "+233241234568",
    "message": "MoMo: You have received GHS 150.00...",
    "type": "credit",
    "status": "success",
    "fee": 0.0,
    "balance": 1250.0
  }
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid JSON or missing required fields |
| 401 | Unauthorized - Invalid credentials |
| 404 | Not Found - Transaction ID not found |
| 409 | Conflict - Transaction ID already exists |
| 500 | Internal Server Error |

## Error Response Format
```json
{
  "error": "Error message description"
}
```

## Running the Server

### Windows
```bash
cd api
start_server.bat
```

### Linux/Mac
```bash
cd api
chmod +x start_server.sh
./start_server.sh
```

### Manual
```bash
cd api
python server.py --port 8000
```

## Testing

Use the provided test script:
```bash
cd api
python test_api.py
```

Or use curl commands from `curl_examples.txt`:
```bash
# Get all transactions
curl -X GET "http://localhost:8000/transactions" \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM="
```

## Data Model

### Transaction Object
```json
{
  "id": "string",           // Unique transaction identifier
  "date": "string",         // ISO 8601 timestamp
  "amount": "number",       // Transaction amount
  "currency": "string",     // Currency code (e.g., "GHS")
  "sender": "string",       // Sender phone number
  "recipient": "string",    // Recipient phone number
  "message": "string",      // SMS message content
  "type": "string",         // Transaction type (credit/debit)
  "status": "string",       // Transaction status
  "fee": "number",          // Transaction fee
  "balance": "number"       // Account balance after transaction
}
```

## Security Notes

⚠️ **Important:** This API uses Basic Authentication for demonstration purposes only. In production environments, consider implementing:

- JWT (JSON Web Tokens) for stateless authentication
- OAuth2 for third-party authorization
- HTTPS for encrypted communication
- Password hashing (bcrypt, Argon2)
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS configuration for web applications

## Limitations of Basic Authentication

1. **Credentials transmitted with every request** - increases security risk
2. **No token expiration** - credentials remain valid until changed
3. **Base64 encoding only** - easily decoded, not encrypted
4. **No logout mechanism** - client must discard credentials
5. **Vulnerable to replay attacks** - same credentials can be reused

## Production Recommendations

1. **JWT Implementation**: Use JSON Web Tokens with expiration
2. **HTTPS**: Always use encrypted connections
3. **Password Hashing**: Store hashed passwords, never plain text
4. **Rate Limiting**: Implement request throttling
5. **Input Validation**: Validate and sanitize all inputs
6. **Audit Logging**: Log all API access and modifications
7. **Database Security**: Use parameterized queries, connection encryption
