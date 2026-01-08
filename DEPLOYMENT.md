# Deployment Guide for Agragrati

This guide covers deploying Agragrati to production using various platforms.

---

## Table of Contents

1. [Vercel Deployment (Recommended)](#vercel-deployment-recommended)
2. [Render Deployment](#render-deployment)
3. [Railway Deployment](#railway-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Post-Deployment Checklist](#post-deployment-checklist)
7. [Troubleshooting](#troubleshooting)

---

## Vercel Deployment (Recommended)

Vercel provides excellent support for both React (Vite) frontends and Python (FastAPI) backends.

### Step 1: Prepare Your Repository

Ensure your project is pushed to GitHub:

```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/yourusername/agragrati.git
git push -u origin main
```

### Step 2: Deploy Frontend

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import Project"
3. Select your GitHub repository
4. Configure project:
  - **Project Name**: `agragrati` (or your preferred name)
  - **Framework Preset**: Vite (auto-detected)
  - **Root Directory**: `frontend`
  - **Build Command**: `npm run build`
  - **Output Directory**: `dist`

5. Add Environment Variables:
  | Variable | Value |
  |----------|-------|
  | `VITE_API_URL` | `https://your-backend-url.vercel.app` (add after backend deployment) |
  | `VITE_SUPABASE_URL` | Your Supabase project URL (optional) |
  | `VITE_SUPABASE_ANON_KEY` | Your Supabase anon key (optional) |

6. Click "Deploy"

**Frontend URL**: `https://agragrati.vercel.app`

### Step 3: Deploy Backend

1. Go to [vercel.com/new](https://vercel.com/new) again
2. Import the same repository
3. Configure project:
  - **Project Name**: `agragrati-api`
  - **Root Directory**: `backend`
  - Leave other settings as default (vercel.json handles configuration)

4. Add Environment Variables:
  | Variable | Value | Required |
  |----------|-------|----------|
  | `GROQ_API_KEY` | Your Groq API key | Yes |
  | `RAPIDAPI_KEY` | Your RapidAPI key | Optional |
  | `ADZUNA_APP_ID` | Your Adzuna App ID | Optional |
  | `ADZUNA_APP_KEY` | Your Adzuna App Key | Optional |
  | `FRONTEND_URL` | `https://agragrati.vercel.app` | Yes |

5. Click "Deploy"

**Backend URL**: `https://agragrati-api.vercel.app`

### Step 4: Update Frontend Environment

1. Go to your frontend Vercel project
2. Settings → Environment Variables
3. Update `VITE_API_URL` to your backend URL
4. Redeploy frontend (Deployments → ... → Redeploy)

---

## Render Deployment

Render is great for Python backends with more control over the server.

### Deploy Backend to Render

1. Go to [render.com/dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
  | Setting | Value |
  |---------|-------|
  | **Name** | `agragrati-api` |
  | **Root Directory** | `backend` |
  | **Runtime** | Python 3 |
  | **Build Command** | `pip install -r requirements.txt` |
  | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. Add Environment Variables (same as Vercel backend)

6. Choose plan:
  - **Free**: Sleeps after 15 min inactivity (first request slow)
  - **Starter ($7/mo)**: Always on

7. Click "Create Web Service"

**Backend URL**: `https://agragrati-api.onrender.com`

### Deploy Frontend to Render (Static Site)

1. Click "New" → "Static Site"
2. Connect repository
3. Configure:
  | Setting | Value |
  |---------|-------|
  | **Name** | `agragrati` |
  | **Root Directory** | `frontend` |
  | **Build Command** | `npm install && npm run build` |
  | **Publish Directory** | `dist` |

4. Add Environment Variables
5. Click "Create Static Site"

---

## Railway Deployment

Railway offers a generous free tier and easy deployments.

### Deploy to Railway

1. Go to [railway.app](https://railway.app/)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

#### Backend Deployment (Recommended for AI workloads):

1. **Create New Project**
  - Go to [railway.app/new](https://railway.app/new)
  - Select "Deploy from GitHub repo"
  - Choose your repository

2. **Configure Service**
  - Click on the service card
  - Go to **Settings** tab
  - Set **Root Directory**: `backend`
  - Railway auto-detects Python and uses `railway.json` config

3. **Add Environment Variables**
  Go to **Variables** tab and add:
  ```
  GROQ_API_KEY=your_groq_key
  RAPIDAPI_KEY=your_rapidapi_key (optional)
  ADZUNA_APP_ID=your_adzuna_id (optional)
  ADZUNA_APP_KEY=your_adzuna_key (optional)
  FRONTEND_URL=https://your-frontend.vercel.app
  ```

4. **Deploy**
  - Railway deploys automatically on push
  - Get your URL from **Settings** → **Domains**
  - Default: `https://your-project.up.railway.app`

5. **Custom Domain** (Optional)
  - Settings → Domains → Add Custom Domain

#### Frontend on Railway (Alternative to Vercel):

1. In same project, click **+ New** → **GitHub Repo**
2. Configure:
  - **Root Directory**: `frontend`
  - **Build Command**: `npm install && npm run build`
  - **Start Command**: `npx serve dist -s -l $PORT`
3. Add environment variables:
  ```
  VITE_API_URL=https://your-backend.up.railway.app
  ```

#### Railway Pricing:

| Plan | Monthly Cost | Best For |
|------|--------------|----------|
| Trial | Free ($5 credit) | Testing |
| Hobby | $5 + usage | Side projects |
| Pro | $20 + usage | Production |

**Typical cost for Agragrati**: $0-7/month

---

## Docker Deployment

Deploy both services using Docker Compose on any VPS (DigitalOcean, AWS, etc.).

### Prerequisites on Server

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Deploy

```bash
# Clone repository
git clone https://github.com/yourusername/agragrati.git
cd agragrati

# Create environment file
cp .env.example .env
nano .env # Add your API keys

# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### With Nginx Reverse Proxy

Create `/etc/nginx/sites-available/agragrati`:

```nginx
server {
  listen 80;
  server_name yourdomain.com;

  location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }

  location /api {
    rewrite /api/(.*) /$1 break;
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
  }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/agragrati /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Add SSL with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for AI features | Yes | `your_groq_key_here` |
| `RAPIDAPI_KEY` | RapidAPI key for JSearch | Optional | `abc123...` |
| `ADZUNA_APP_ID` | Adzuna application ID | Optional | `your_app_id` |
| `ADZUNA_APP_KEY` | Adzuna application key | Optional | `abc123...` |
| `FRONTEND_URL` | Frontend URL for CORS | Yes | `https://agragrati.vercel.app` |

### Frontend Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | Yes | `https://agragrati-api.vercel.app` |
| `VITE_SUPABASE_URL` | Supabase project URL | Optional | `https://xxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key | Optional | `your_anon_key` |

---

## Post-Deployment Checklist

- [ ] Backend `/health` endpoint returns `{"status": "healthy"}`
- [ ] Frontend loads without console errors
- [ ] Resume upload works
- [ ] AI features respond (analyze resume)
- [ ] Job search returns results (if APIs configured)
- [ ] Theme toggle works
- [ ] PWA install prompt appears
- [ ] Bookmarks save (if Supabase configured)
- [ ] Application tracker works
- [ ] Mobile responsive design works

---

## Troubleshooting

### CORS Errors

**Symptom**: `Access to fetch at 'https://api...' has been blocked by CORS policy`

**Solution**: 
1. Ensure `FRONTEND_URL` is set correctly in backend environment
2. Check the URL includes `https://` 
3. Redeploy backend after changing environment variables

### API Key Issues

**Symptom**: `500 Internal Server Error` or `GROQ_API_KEY not found`

**Solution**:
1. Verify environment variable is set in deployment platform
2. Check for typos in variable name
3. Ensure no extra spaces around the key value

### Build Failures

**Frontend Build Fails**:
```bash
# Check Node version (needs 18+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Backend Build Fails**:
```bash
# Check Python version (needs 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Cold Start Issues (Free Tiers)

Free tier services "sleep" after inactivity. First request may take 10-30 seconds.

**Solutions**:
- Upgrade to paid tier
- Use a cron service to ping `/health` every 10 minutes
- Show loading state to users

### Supabase Connection Issues

**Symptom**: Bookmarks/Applications not saving

**Solution**:
1. Check Supabase project is running
2. Verify URL and anon key are correct
3. Check RLS policies allow operations
4. Look at Supabase dashboard logs

---

## Need Help?

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [Vite Documentation](https://vitejs.dev/guide/)
- [Open an Issue](https://github.com/yourusername/agragrati/issues)
