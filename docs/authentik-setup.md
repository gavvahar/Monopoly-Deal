# Authentik SSO Setup

This guide covers configuring Authentik to work with the Monopoly Deal app.
The app uses OAuth2/OpenID Connect. You will need to create a **Provider** and an **Application** in Authentik for each environment (dev / prod).

---

## 1. Create an OAuth2/OpenID Connect Provider

Go to **Admin Interface → Applications → Providers → Create**

| Field | Value |
| --- | --- |
| Type | OAuth2/OpenID Connect Provider |
| Name | e.g. `Provider for Monopoly Deal Dev` |
| Authorization flow | `default-provider-authorization-explicit-consent` |
| Client type | **Confidential** |
| Redirect URIs | `strict: https://<your-app-domain>/auth/callback` |
| Signing Key | Select any available key (e.g. `authentik Self-signed Certificate`) |

After saving, copy the **Client ID** and **Client Secret** — you will need them in your `.env`.

### Scopes

Ensure the following scopes are allowed on the provider:

- `openid`
- `profile`
- `email`

These are included by default. Do not remove them.

### Subject Mode

Set **Subject mode** to `Based on the User's username`.
This ensures `preferred_username` is returned in the userinfo response, which is what the app uses as the session username.

---

## 2. Create an Application

Go to **Admin Interface → Applications → Applications → Create**

| Field | Value |
| --- | --- |
| Name | e.g. `Monopoly Deal Dev` |
| Slug | e.g. `monopoly-deal-dev` *(used in logout URL — keep note of this)* |
| Provider | Select the provider created in step 1 |
| Policy engine mode | `ANY` |

---

## 3. Create Groups

Go to **Admin Interface → Directory → Groups → Create**

Create two groups per environment:

| Group Name                 | Purpose         |
| -------------------------- | --------------- |
| `Monopoly_Deal_Dev_Admins` | Admin users     |
| `Monopoly_Deal_Dev_Users`  | Regular players |

Add users to the appropriate group.

---

## 4. Bind Groups to the Application

Go to your application → **Policy / Group / User Bindings → Bind existing Policy / Group / User**

Bind both groups:

- `Monopoly_Deal_Dev_Admins`
- `Monopoly_Deal_Dev_Users`

With policy engine mode set to `ANY`, a user only needs to be in one of the groups to access the app.

---

## 5. Configure `.env`

Add the following to your `.env` file:

```env
SSO_ENABLED=true
AUTHENTIK_URL=https://<your-authentik-domain>
AUTHENTIK_CLIENT_ID=<Client ID from step 1>
AUTHENTIK_CLIENT_SECRET=<Client Secret from step 1>
AUTHENTIK_REDIRECT_URI=https://<your-app-domain>/auth/callback
AUTHENTIK_APP_SLUG=<slug from step 2>
```

### URL reference

The app uses these Authentik endpoints (constructed automatically from `AUTHENTIK_URL` and `AUTHENTIK_APP_SLUG`):

| Purpose | URL |
| --- | --- |
| Authorize | `{AUTHENTIK_URL}/application/o/authorize/` |
| Token | `{AUTHENTIK_URL}/application/o/token/` |
| Userinfo | `{AUTHENTIK_URL}/application/o/userinfo/` |
| Logout | `{AUTHENTIK_URL}/application/o/{AUTHENTIK_APP_SLUG}/end-session/` |

---

## 6. Per-environment notes

- The `dev` and `prod` Docker Compose profiles set `SSO_ENABLED=true` automatically.
- The `local` profile sets `SSO_ENABLED=false` and uses local username/password login instead — no Authentik setup needed for local.
- Create a separate Provider + Application in Authentik for each environment (dev/prod) with the correct redirect URI for that environment's domain/port.
