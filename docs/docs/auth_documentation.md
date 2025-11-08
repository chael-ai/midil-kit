# Midil Auth Module Documentation

## Overview
The **Midil Auth Module** provides a unified authentication layer for securing APIs and microservices within the Midil Kit ecosystem. It ensures secure access control through **token-based authentication**, with **AWS Cognito** as the default provider. The module is flexible and can be extended to integrate with other authentication strategies (e.g., OAuth2, Firebase, or custom JWT solutions).

---

## Core Features
- **Plug-and-Play Authentication Middleware** for FastAPI.
- **Built-in Cognito Integration** for AWS-based deployments.
- **Custom Strategy Support** – easily extendable for any identity provider.
- **JWT Authorization** and Token Validation.
- **Secure Configuration via Environment Variables.**

---

## Configuration Setup

The `config.py` defines a `CognitoAuthConfig` model:
```python
class CognitoAuthConfig(BaseModel):
    type: Literal["cognito"] = "cognito"
    user_pool_id: str
    client_id: str
    client_secret: Optional[SecretStr]
    region: str
```

In your `.env` file:
```bash
MIDIL__AUTH={
  "type": "cognito",
  "user_pool_id": "us-east-1_abcdef123",
  "client_id": "1234567890abcdef",
  "region": "us-east-1",
  "client_secret": null
}
```

> ⚙️ **Tip:** Always ensure your `.env` values match the AWS Cognito pool configuration or equivalent provider setup.

---

## Implementation Guide (Step-by-Step)

1. **Import the Middleware and Authorizer**:
   ```python
   from midil.auth.cognito import CognitoJWTAuthorizer
   from midil.midilapi.fastapi.middleware.auth_middleware import CognitoAuthMiddleware
   ```

2. **Add the Middleware to FastAPI**:
   ```python
   app.add_middleware(
       CognitoAuthMiddleware,
       authorizer=CognitoJWTAuthorizer(region="us-east-1", user_pool_id="us-east-1_abcdef123")
   )
   ```

3. **Protect Your Routes**:
   ```python
   from fastapi import Depends, FastAPI
   from midil.auth.dependencies import get_current_user

   app = FastAPI()

   @app.get("/profile")
   def profile(user: dict = Depends(get_current_user)):
       return {"message": f"Welcome {user['username']}"}
   ```

4. **Run and Test**:
   - Start the server and test with an Authorization header:
     ```bash
     curl -H "Authorization: Bearer <JWT_TOKEN>" http://localhost:8000/profile
     ```

---

## Cognito Authentication Flow

The Cognito-based flow works as follows:

1. A user logs in via Cognito and receives a JWT access token.
2. The client app includes this token in the `Authorization` header.
3. The `CognitoAuthMiddleware` intercepts the request.
4. The `CognitoJWTAuthorizer` verifies the token using Cognito's public keys.
5. The request is passed downstream only if verified.

**Simplified Architecture Diagram:**
```
Client App --> FastAPI + CognitoAuthMiddleware --> CognitoJWTAuthorizer --> AWS Cognito (Public Keys)
```

---

## Extending Authentication (Custom Strategies)

You can build your own strategy by subclassing the base authentication provider:
```python
from midil.auth.base import AuthZProvider

class CustomJWTAuthorizer(AuthZProvider):
    def verify_token(self, token: str):
        # Custom logic here (e.g., Firebase, Auth0, or internal system)
        return {"username": "custom_user", "roles": ["admin"]}
```

Then update your `.env`:
```bash
MIDIL__AUTH={"type": "custom"}
```

> 💡 **Note:** Midil is designed to make adding new authentication types straightforward—just implement a compatible provider and update the config.

---

## Testing & Troubleshooting

### Test Authentication
Use Postman or `curl` to send a request with a valid JWT:
```bash
curl -H "Authorization: Bearer <valid_token>" http://localhost:8000/profile
```
If successful, you’ll receive a JSON response with the authenticated user info.

### Common Errors
| Status | Cause | Resolution |
|--------|--------|------------|
| `401 Unauthorized` | Invalid or missing token | Ensure a valid JWT is sent. |
| `403 Forbidden` | User lacks permission | Check user roles and access policies. |
| `500 Internal Server Error` | Invalid Cognito config | Verify `.env` and Cognito setup. |

---

## Summary
The **Midil Auth Module** simplifies secure authentication across services. With AWS Cognito as its default provider, it offers a plug-and-play experience for token-based security. Developers can easily swap or extend authentication strategies while keeping the same middleware architecture.

---

**Next Steps:**
- Refer to AWS Cognito Documentation: [AWS Cognito Developer Guide](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)
- Explore `midil.auth.base` to create custom authenticators.
- Integrate authentication into event consumers or HTTP clients for full-stack consistency.

