# Firebase Live Data Setup

This project can now run in two modes:

- `mock` mode when Firebase is not configured.
- `firebase` mode when the Firebase environment variables are present.

## What gets stored

- Water quality samples in `monitoring/water_quality_logs`
- Object detection records in `monitoring/detection_logs`
- Latest water sample in `monitoring/water_quality/latest`
- Latest detection sample in `monitoring/detection/latest`

Live camera frames are kept transiently for the dashboard only. They are not written to Firebase Storage.

## Required environment variables

Set these on the deployed Flask server:

```bash
SECRET_KEY=your-secret
FIREBASE_DATABASE_URL=https://autonomous-boat-906cf-default-rtdb.asia-southeast1.firebasedatabase.app/
FIREBASE_CREDENTIALS_PATH="D:\Claude\secret\autonomous-boat-906cf-firebase-adminsdk-fbsvc-ad9a9e11f3.json"
INGEST_API_KEY=rasel-2025
```

`GOOGLE_APPLICATION_CREDENTIALS` also works as the credentials path if you prefer that convention.

`FIREBASE_STORAGE_BUCKET` is optional for this workflow because images are not persisted.

## Raspberry Pi upload flow

Send three kinds of data from the Pi:

1. Water quality JSON to `POST /api/ingest/water`
2. Detection JSON to `POST /api/ingest/detection`
3. Camera frame upload to `POST /api/ingest/frame`

Detection class mapping:

- `class_id: 0` = `Plastic Bottle`
- `class_id: 1` = `Debris`

The example below uses `Plastic Bottle` only as a sample payload for class `0`.

Use the header:

```http
X-INGEST-TOKEN: your-pi-upload-token
```

## Example payloads

### Water quality

```json
{
  "device_id": "pi-01",
  "timestamp": "2026-07-06T10:20:30",
  "tds": 182,
  "turbidity": 4.2,
  "temperature": 28.1,
  "status": "Good"
}
```

### Detection

```json
{
  "device_id": "pi-01",
  "timestamp": "2026-07-06T10:20:31",
  "class_id": 0,
  "class_name": "Plastic Bottle",
  "object_type": "Plastic Bottle",
  "bottle_count": 1,
  "debris_count": 0,
  "total_objects": 1,
  "confidence_score": 0.94,
  "image_url": "https://..."
}
```

### Frame upload

Send the image as multipart form data with the field name `image` if you want the dashboard to show a live snapshot. The server keeps only the latest frame in memory for display; it does not store the image in Firebase Storage.

## Raspberry Pi sender example

```python
import requests

BASE_URL = "https://your-domain.com"
TOKEN = "your-pi-upload-token"
HEADERS = {"X-INGEST-TOKEN": TOKEN}

water_payload = {
    "device_id": "pi-01",
    "timestamp": "2026-07-06T10:20:30",
    "tds": 182,
    "turbidity": 4.2,
    "temperature": 28.1,
    "status": "Good",
}

requests.post(f"{BASE_URL}/api/ingest/water", json=water_payload, headers=HEADERS, timeout=10)
```

## Deploy order

1. Configure Firebase Realtime Database.
2. Deploy the Flask app with the env vars above.
3. Update the Raspberry Pi sender script to post to the deployed URL.
4. Confirm data appears in Firebase.
5. Open the dashboard and verify the live cards and snapshot refresh.

## Notes

- If Firebase is not configured, the app falls back to mock data.
- The dashboard polls the backend, so the page updates automatically once live records are being written.
- The snapshot endpoint returns the latest live frame from memory, not a stored image.
