# Production deployment

## Render backend

Create a Render **Web Service** from this repository with these settings:

- Root directory: `backend`
- Runtime: Docker
- Dockerfile path: `Dockerfile`
- Health check path: `/api/schema/`

Set the following environment variables in Render:

```text
SECRET_KEY=<a long random value>
DEBUG=false
ALLOWED_HOSTS=<your-render-service>.onrender.com
CORS_ALLOWED_ORIGINS=https://<your-vercel-domain>
DATABASE_URL=<Render PostgreSQL internal database URL>
MAX_RESUME_UPLOAD_BYTES=10485760
```

The Docker image bootstraps Django's built-in and custom-user tables before
syncing the remaining application schema, then starts Gunicorn. After its
first successful deploy, copy the public service URL, for example
`https://hireflow-api.onrender.com`.

## Vercel frontend

Import the same repository into Vercel and set **Root Directory** to
`frontend`. Vercel automatically runs `npm run build` and publishes `dist`.

Add this Production environment variable before deploying:

```text
VITE_API_URL=https://<your-render-service>.onrender.com/api/v1/
```

`VITE_API_URL` is embedded during the frontend build, so redeploy Vercel after
changing it. `frontend/vercel.json` keeps React Router routes working on a
direct refresh.
