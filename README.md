# radiography-api
FastAPI backend for managing patient radiographic records with Google SSO authentication, JWT security, and Cloudinary image storage.

## Image Security Flow

1. Authenticate with `POST /api/v1/auth/login` and authorize Swagger with the returned bearer token.
2. Request a short-lived radiography image token with `POST /api/v1/radiography/{item_id}/image-token`.
3. Copy the `image_access_url` from the response and open it while still sending your bearer token.
4. The API validates that the token belongs to the authenticated user and returns a temporary signed Cloudinary URL.

## Manual Checks

- Valid token: generate an image token and immediately call `/api/v1/radiography/{item_id}/image-access?token=...`.
- Invalid token: change one character in the token and confirm the API returns `401`.
- Expired token: wait more than the configured image-token lifetime and confirm the API returns `401`.
