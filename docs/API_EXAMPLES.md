# API Usage Examples

Complete examples for using the Travel Concierge API.

## Base URL

```
http://localhost:8080
```

## Authentication Flow

### 1. Register New User

**Endpoint**: `POST /auth/register`

```bash
curl -X POST "http://localhost:8080/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "traveler@example.com",
    "password": "SecureP@ss123",
    "full_name": "Jane Traveler"
  }'
```

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "traveler@example.com",
  "full_name": "Jane Traveler",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### 2. Login

**Endpoint**: `POST /auth/login`

```bash
curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "traveler@example.com",
    "password": "SecureP@ss123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the `access_token` - use it in all subsequent requests!**

### 3. Get Current User Info

**Endpoint**: `GET /auth/me`

```bash
curl -X GET "http://localhost:8080/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Trip Planning

### Plan a Trip to Tokyo

**Endpoint**: `POST /itinerary/plan`

```bash
curl -X POST "http://localhost:8080/itinerary/plan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "destination": "Tokyo",
    "duration_days": 5,
    "budget": 50000,
    "currency": "INR",
    "dietary_preferences": ["vegetarian"],
    "interests": ["museums", "markets", "temples", "technology"],
    "additional_notes": "Interested in authentic Japanese culture and modern tech"
  }'
```

**Response** (abbreviated):
```json
{
  "request_id": "req_20240101120000",
  "destination": "Tokyo",
  "duration_days": 5,
  "options": [
    {
      "option_type": "budget",
      "title": "Tokyo Explorer - Budget Edition",
      "description": "Affordable 5-day trip focusing on budget-friendly options and local experiences",
      "total_estimated_cost": 35000,
      "daily_plans": [
        {
          "day": 1,
          "title": "Day 1: Tokyo Exploration",
          "activities": [
            {
              "time": "Morning",
              "name": "Tokyo National Museum",
              "description": "Premier museum showcasing local history and culture",
              "duration": "2-3 hours",
              "cost": 500,
              "category": "museum"
            }
          ],
          "estimated_cost": 7000,
          "meals": [
            {"type": "Breakfast", "restaurant": "Local cafe near hotel", "cost": 100},
            {"type": "Lunch", "restaurant": "Veggie Delight Tokyo", "cost": 200},
            {"type": "Dinner", "restaurant": "Hotel restaurant", "cost": 200}
          ],
          "accommodation": {
            "type": "Budget hotel",
            "cost": 2100
          },
          "transportation": {
            "mode": "Public transport + taxi",
            "cost": 300
          }
        }
      ],
      "packing_checklist": [
        "Passport and travel documents",
        "Travel insurance papers",
        "Phone and charger",
        "Comfortable walking shoes",
        "Day backpack"
      ],
      "local_insights": [
        "Keep valuables secure",
        "Use registered taxis",
        "Respect local customs"
      ],
      "transportation_tips": [
        "Metro system is efficient and affordable for getting around",
        "Use taxi apps like Uber, Ola"
      ]
    },
    {
      "option_type": "balanced",
      "title": "Tokyo Complete Experience",
      "total_estimated_cost": 50000
    },
    {
      "option_type": "splurge",
      "title": "Tokyo Luxury Getaway",
      "total_estimated_cost": 65000
    }
  ],
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### Get My Trips

**Endpoint**: `GET /itinerary/my-trips`

```bash
curl -X GET "http://localhost:8080/itinerary/my-trips?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
[
  {
    "id": "itinerary-123",
    "destination": "Tokyo",
    "duration_days": 5,
    "budget": 50000,
    "currency": "INR",
    "travel_style": "balanced",
    "status": "draft",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Get Specific Itinerary

**Endpoint**: `GET /itinerary/{itinerary_id}`

```bash
curl -X GET "http://localhost:8080/itinerary/itinerary-123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Delete Itinerary

**Endpoint**: `DELETE /itinerary/{itinerary_id}`

```bash
curl -X DELETE "http://localhost:8080/itinerary/itinerary-123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Chat with Assistant

### Send a Message

**Endpoint**: `POST /chat/message`

**Example 1: General Travel Question**

```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "What is the best way to travel inside Tokyo?"
  }'
```

**Response**:
```json
{
  "message": "Tokyo has an excellent public transportation system. The best way to get around is:\n\n1. **Tokyo Metro & Toei Subway**: The metro system is efficient and affordable (¥50-200 per ride). Get a PASMO or Suica card for easy travel.\n\n2. **JR Yamanote Line**: This circular line connects major areas like Shibuya, Shinjuku, and Tokyo Station.\n\n3. **Taxis**: Available but expensive. Use apps like JapanTaxi or Uber for convenience.\n\n4. **Walking**: Many areas like Asakusa and Harajuku are pedestrian-friendly.\n\nI recommend getting a day pass for unlimited subway travel if you plan multiple trips.",
  "sources": [
    {
      "type": "external_transportation",
      "summary": "Data from transportation API"
    }
  ],
  "tool_calls": ["transportation_api"],
  "tokens_used": 450
}
```

**Example 2: Weather Query**

```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "What's the weather like in Tokyo right now?"
  }'
```

**Response**:
```json
{
  "message": "Current weather in Tokyo:\n\n🌤️ **Temperature**: 25°C (feels like 26°C)\n**Conditions**: Partly cloudy\n**Humidity**: 65%\n**Wind**: 5.5 m/s\n\nIt's pleasant weather for sightseeing! Bring a light jacket for evening.",
  "sources": [
    {
      "type": "external_weather",
      "summary": "Data from weather API"
    }
  ],
  "tool_calls": ["weather_api"],
  "tokens_used": 380
}
```

**Example 3: Restaurant Recommendations**

```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "Can you recommend some vegetarian restaurants in Tokyo?"
  }'
```

**Example 4: With Conversation History**

```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "How far is it from my hotel?",
    "conversation_history": [
      {"role": "user", "content": "Recommend restaurants in Tokyo"},
      {"role": "assistant", "content": "I recommend Veggie Delight Tokyo in downtown..."}
    ]
  }'
```

### Get Chat History

**Endpoint**: `GET /chat/history`

```bash
curl -X GET "http://localhost:8080/chat/history?limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
[
  {"role": "user", "content": "What's the best time to visit Tokyo?"},
  {"role": "assistant", "content": "The best time to visit Tokyo is..."},
  {"role": "user", "content": "What about cherry blossom season?"},
  {"role": "assistant", "content": "Cherry blossom season in Tokyo..."}
]
```

## Document Management

### Upload a Document

**Endpoint**: `POST /documents/upload`

```bash
curl -X POST "http://localhost:8080/documents/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@japan_visa_guidelines.pdf"
```

**Response**:
```json
{
  "id": "doc-456",
  "filename": "japan_visa_guidelines.pdf",
  "file_type": "pdf",
  "status": "processing",
  "chunk_count": 0,
  "created_at": "2024-01-01T13:00:00Z"
}
```

**Note**: Document is processed asynchronously. Status changes to "completed" when ready.

### Get My Documents

**Endpoint**: `GET /documents/my-documents`

```bash
curl -X GET "http://localhost:8080/documents/my-documents?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
[
  {
    "id": "doc-456",
    "filename": "japan_visa_guidelines.pdf",
    "file_type": "pdf",
    "status": "completed",
    "chunk_count": 25,
    "created_at": "2024-01-01T13:00:00Z"
  }
]
```

### Query Uploaded Document

After uploading, you can ask questions about the document:

```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "What are the visa requirements for Japan mentioned in my document?"
  }'
```

The RAG system will retrieve relevant sections from your uploaded document.

### Delete Document

**Endpoint**: `DELETE /documents/{document_id}`

```bash
curl -X DELETE "http://localhost:8080/documents/doc-456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Health & Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Prometheus Metrics

```bash
curl http://localhost:8080/metrics
```

Returns Prometheus-formatted metrics.

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error description",
  "request_id": "req-123-456"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized (invalid/missing token)
- `404`: Not Found
- `500`: Internal Server Error

**Example Error**:

```bash
curl -X POST "http://localhost:8080/itinerary/plan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -d '{}'
```

**Response** (401):
```json
{
  "detail": "Could not validate credentials"
}
```

## Rate Limiting

Default limits:
- 60 requests per minute
- 1000 requests per day

Exceeded limits return `429 Too Many Requests`.

## Using Postman

1. Import base URL: `http://localhost:8080`
2. Create environment variable: `ACCESS_TOKEN`
3. Add header to all requests: `Authorization: Bearer {{ACCESS_TOKEN}}`
4. Use collections to organize requests

## Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8080"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "traveler@example.com",
    "password": "SecureP@ss123"
})
token = response.json()["access_token"]

# Use token in subsequent requests
headers = {"Authorization": f"Bearer {token}"}

# Plan trip
trip_request = {
    "destination": "Tokyo",
    "duration_days": 5,
    "budget": 50000,
    "currency": "INR",
    "dietary_preferences": ["vegetarian"],
    "interests": ["museums", "markets"]
}

response = requests.post(
    f"{BASE_URL}/itinerary/plan",
    json=trip_request,
    headers=headers
)

itinerary = response.json()
print(f"Generated {len(itinerary['options'])} itinerary options")
```

## Interactive API Documentation

For interactive testing, visit:
**http://localhost:8080/docs**

Features:
- Try all endpoints
- See request/response schemas
- Automatic authorization
- No coding required

---

**Need more examples?** Check the Swagger UI or explore the code in `backend/app/api/`.
