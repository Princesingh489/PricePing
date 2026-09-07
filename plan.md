# PricePing Production Deployment Plan (100% Free Tier Analysis)

> **Document Type:** Production Architecture, Cost Analysis & Deployment Blueprint  
> **Target Application:** PricePing (React Frontend, FastAPI Backend, PostgreSQL DB, Redis Broker, Celery Worker, Celery Beat, Playwright Scraping Engine)  
> **Budget Constraint:** $0.00 / month (100% Free Forever)  
> **Source Code Modifications:** None (Preserving all existing code)

---

## 1. Executive Summary & Top Recommendation

### The Core Challenge
PricePing is not a simple static website or a basic REST CRUD API. It is an **asynchronous e-commerce scraping and monitoring platform** composed of **6 interdependent components**:
1. **Frontend**: React 19 + Vite SPA with dynamic charting and real-time alerts.
2. **Backend API**: FastAPI / Uvicorn handling search, comparison, and authentication.
3. **Database**: PostgreSQL 16 (relational schema, Alembic migrations, price history timeseries).
4. **Cache & Broker**: Redis 7 (in-memory caching and Celery message bus).
5. **Background Workers**: Celery Worker (executing asynchronous scraper pipelines).
6. **Task Scheduler**: Celery Beat (periodically checking prices every 30 mins / 6 hours).
7. **Browser Automation Engine**: **Playwright Headless Chromium** (required for Tier-3 fallback scraping on anti-bot protected sites like Amazon, Flipkart, AJIO, and Myntra).

> [!WARNING]
> **The Playwright RAM Gotcha on Standard Free PaaS:**  
> Free tiers on platforms like Render, Koyeb, or Railway either:
> - Only offer **512 MB RAM** (A single Playwright Chromium instance requires 400 MB–900 MB RAM; running Playwright on a 512 MB PaaS container triggers immediate **Out-Of-Memory (OOM) termination**).
> - **Spin down / Sleep** after 15 minutes of inactivity (which kills background Celery Beat schedulers).
> - Free Render databases are **wiped and deleted after 90 days**.

---

### 🏆 Verdict: The Preferred 100% Free Production Architectures

Depending on your preference for setup complexity versus operational control, here are the top 2 recommended production architectures:

| Ranking | Strategy | Components | Strengths | Trade-offs |
| :--- | :--- | :--- | :--- | :--- |
| 🥇 **#1 Top Preference** | **All-in-One VPS (Oracle Cloud Always Free)** | Full `docker-compose` on 1 VM (4 OCPU, 24 GB RAM, 200 GB SSD) | **Zero code changes**, 24 GB RAM effortlessly handles Playwright, 24/7 continuous Celery scheduler, permanent Postgres. | Requires initial Linux server setup (Docker, firewall, domain pointing). |
| 🥈 **#2 Serverless / Managed PaaS** | **Multi-Cloud Serverless Stack** | Frontend: **Vercel**<br>Database: **Supabase**<br>Redis: **Upstash**<br>API + Worker: **Hugging Face Docker Space** (16 GB RAM free) or **Koyeb** | Zero Linux server management, automatic CI/CD on git push, global CDN. | Multi-dashboard management, environment variable duplication across platforms. |

---

## 2. Option 1 (Recommended): Oracle Cloud Infrastructure (OCI) Always Free Tier

### Why This Is The Best Fit
Oracle Cloud provides an **"Always Free"** tier that is unmatched by any cloud provider in the industry:
- **Compute**: Ampere A1 ARM instance with up to **4 OCPU cores and 24 GB of RAM** (or split into 2 instances), OR 2 AMD x86 instances with 1 GB RAM each.
- **Storage**: **200 GB Block Volume** (NVMe SSD storage) 100% free forever.
- **Bandwidth**: **10 TB outbound data transfer per month** free.
- **Public IP**: Free static public IPv4 address.
- **Cost**: **$0.00 / month forever** (Requires a valid credit card for identity verification during signup, but is never billed within the free allowance).

### Architecture on OCI
```
                       Internet / Users
                              │
                      [ Cloudflare DNS ] (Free CDN + SSL)
                              │
                    ┌─────────▼─────────┐
                    │  OCI Always Free  │ (Ubuntu 22.04 / 24.04 ARM64)
                    │  (24 GB RAM / 4c) │
                    └─────────┬─────────┘
                              │
       ┌──────────────────────┴──────────────────────┐
       │             Docker Compose Stack             │
       │                                              │
       │  ┌──────────────┐          ┌──────────────┐  │
       │  │ Nginx Reverse│◄────────►│ React SPA    │  │
       │  │ Proxy (Port  │          │ (Production  │  │
       │  │ 80 / 443)    │          │  dist build) │  │
       │  └──────┬───────┘          └──────────────┘  │
       │         │                                    │
       │  ┌──────▼───────┐          ┌──────────────┐  │
       │  │ FastAPI      │◄────────►│ PostgreSQL   │  │
       │  │ Backend      │          │ 16 Container │  │
       │  └──────┬───────┘          └──────────────┘  │
       │         │                                    │
       │  ┌──────▼───────┐          ┌──────────────┐  │
       │  │ Redis 7      │◄────────►│ Celery Beat  │  │
       │  │ Broker/Cache │          │ Scheduler    │  │
       │  └──────┬───────┘          └──────────────┘  │
       │         │                                    │
       │  ┌──────▼─────────────────────────────────┐  │
       │  │ Celery Worker + Playwright Chromium   │  │
       │  │ (Scrapes Amazon, Flipkart, AJIO, etc.) │  │
       │  └────────────────────────────────────────┘  │
       └──────────────────────────────────────────────┘
```

### Advantages for PricePing:
1. **Zero Code Changes**: The existing `docker-compose.yml` can run directly in production with minor environment tweaks.
2. **Massive Memory Headroom**: 24 GB of RAM allows running 4-8 parallel Playwright headless browser contexts simultaneously without any OOM crashes.
3. **True Background Scheduling**: Celery Beat runs continuously 24/7/365 to track price drops without sleeping or throttling.
4. **Data Sovereignty & Persistence**: PostgreSQL data is stored on a persistent 200 GB SSD volume with no 90-day deletion limits.

---

## 3. Option 2: Managed Multi-Cloud Serverless Stack (Zero-Ops)

If you do not want to manage an Ubuntu server, you can split PricePing across top-tier free cloud services:

```
                                  Client Browser
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 │                                             │
          [ Web UI Access ]                             [ API Requests ]
                 │                                             │
                 ▼                                             ▼
        ┌──────────────────┐                         ┌───────────────────┐
        │  Vercel / Pages  │                         │ Hugging Face      │
        │  React 19 Vite   │                         │ Docker Space      │
        │  (Global Edge)   │                         │ FastAPI Backend + │
        │  100% Free CDN   │                         │ Celery Worker     │
        └──────────────────┘                         │ (16 GB RAM Free!) │
                                                     └─────────┬─────────┘
                                                               │
                         ┌─────────────────────────────────────┴────────────┐
                         │                                                  │
                         ▼                                                  ▼
              ┌─────────────────────┐                            ┌─────────────────────┐
              │  Supabase Postgres  │                            │    Upstash Redis    │
              │  500 MB Free DB     │                            │ 10,000 requests/day │
              │  Automated Backups  │                            │ Free Serverless     │
              └─────────────────────┘                            └─────────────────────┘
```

### Component Breakdown:

#### 1. Frontend: Vercel or Cloudflare Pages
- **Cost**: $0.00 forever.
- **Specs**: 100 GB bandwidth/month, instant global edge CDN, automated deployments directly connected to your GitHub repository `frontend/` directory.
- **Custom Domain & SSL**: Free automated Let's Encrypt certificates.

#### 2. Database: Supabase
- **Cost**: $0.00 forever.
- **Specs**: 500 MB dedicated PostgreSQL database, built-in connection pooler (port 6543 for PgBouncer), automated daily backups, web-based Table Editor.
- **Suitability**: Perfectly supports SQLAlchemy and asyncpg. 500 MB is sufficient to track over 250,000 product price history points.

#### 3. Broker & Cache: Upstash Redis
- **Cost**: $0.00 forever.
- **Specs**: 10,000 commands/day free, standard Redis protocol compatibility with TLS, persistence enabled.
- **Suitability**: Serves as the Celery message broker and caching tier for scraper results.

#### 4. Backend & Playwright Worker: Hugging Face Spaces (Docker Space)
- **Cost**: $0.00 forever.
- **Specs**: **2 vCPU, 16 GB RAM**, 50 GB persistent disk, public HTTPS endpoint.
- **Why HF Spaces?**: Standard free app hosts (Render/Koyeb) limit you to 512 MB RAM, which crashes Playwright Chromium. Hugging Face Spaces offers **16 GB RAM on their free tier**, making it one of the only free cloud platforms capable of running heavy headless browser scraping suites.

---

## 4. Platform Comparison Matrix

| Criteria | Oracle Cloud Always Free (Option 1) | Hugging Face + Supabase + Vercel (Option 2) | Render.com Free Tier | Railway.app |
| :--- | :--- | :--- | :--- | :--- |
| **Total Monthly Cost** | **$0.00** | **$0.00** | **$0.00** (with major limits) | Paid ($5/mo trial only) |
| **RAM Available for Scrapers** | **24 GB** (Ampere) | **16 GB** (HF Space) | 512 MB (Crashes Playwright) | 512 MB - 1 GB |
| **PostgreSQL Persistence** | Permanent (200 GB SSD) | Permanent (500 MB Supabase) | Deleted after 90 days! | Limited trial credits |
| **Celery Beat (24/7 Scheduling)** | Native continuous process | Continuous via HF Space | Not supported on free web service | Paid worker required |
| **Setup Complexity** | Medium (Docker on Linux) | Low-Medium (Multi-service) | Low | Low |
| **Code Changes Required** | **None** | None to minimal config | Requires removing Playwright | None |
| **Reliability for Price Tracking** | ⭐⭐⭐⭐⭐ (99.9%) | ⭐⭐⭐⭐ (98%) | ⭐⭐ (Sleeps after 15m) | ⭐⭐⭐ |

---

## 5. Step-by-Step Implementation Guide for Option 1 (Oracle Cloud Free Tier)

### Step 1: Account Creation & Instance Provisioning
1. Sign up at [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/).
2. Select your nearest home region (e.g., Mumbai, Hyderabad for low latency to Indian e-commerce sites).
3. Navigate to **Compute > Instances > Create Instance**:
   - **OS**: Ubuntu 24.04 LTS (or Ubuntu 22.04 LTS).
   - **Shape**: Change Shape -> Select **Ampere (ARM)** -> `VM.Standard.A1.Flex`.
   - Allocate: **2 to 4 OCPUs** and **12 to 24 GB RAM**.
   - Assign a public IPv4 address.
   - Download and save the SSH private key (`ssh-key.key`).

### Step 2: Server Security & Ingress Configuration
In the Oracle Cloud Console:
1. Navigate to **Networking > Virtual Cloud Networks > Default VCN > Security Lists**.
2. Add Ingress Rules to allow web traffic:
   - **Port 80 (HTTP)**: Source `0.0.0.0/0`, Protocol `TCP`, Port `80`.
   - **Port 443 (HTTPS)**: Source `0.0.0.0/0`, Protocol `TCP`, Port `443`.
   - **Port 22 (SSH)**: Default allowed.

On the Ubuntu instance (via SSH):
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

### Step 3: Install Docker & Docker Compose
```bash
# Update and install Docker
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

### Step 4: Clone Repository & Configure Environment
```bash
# Clone the codebase
git clone <YOUR_GITHUB_REPOSITORY_URL> /home/ubuntu/PricePing
cd /home/ubuntu/PricePing

# Create production .env file
cp .env.example .env
```

Edit `.env` for production values:
```ini
POSTGRES_USER=pricewatch_prod
POSTGRES_PASSWORD=generate_strong_unique_password_here
POSTGRES_DB=pricewatch_db
DATABASE_URL=postgresql://pricewatch_prod:generate_strong_unique_password_here@db:5432/pricewatch_db
REDIS_URL=redis://redis:6379/0

SECRET_KEY=generate_64_char_cryptographic_secret_here
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "http://your-server-ip"]

# Free SMTP Alerts (e.g. Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME=PricePing Alerts
```

### Step 5: Launch Production Containers
```bash
# Build frontend production bundle and launch all services in background
docker compose build
docker compose up -d
```

Verify service health:
```bash
docker compose ps
docker compose logs -f backend
```

### Step 6: Free SSL Setup with Cloudflare or Certbot
1. Point your domain DNS `A record` to your Oracle instance's Public IP.
2. In **Cloudflare** (Free Tier):
   - Set SSL/TLS encryption mode to **Full**.
   - Enable **Always Use HTTPS** and **Auto Minify**.
   - Cloudflare provides instant DDoS protection, free edge caching, and automated SSL without requiring any local Certbot configuration.

---

## 6. Step-by-Step Implementation Guide for Option 2 (Vercel + Supabase + HF Space)

If you prefer completely managed serverless platforms without maintaining a virtual machine:

### 1. Database on Supabase (5 mins)
1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Navigate to **Project Settings > Database > Connection Strings**.
3. Copy the **URI** connection string:
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
4. In Supabase SQL Editor, run initial migrations or let the backend start up with SQLAlchemy's `Base.metadata.create_all()`.

### 2. Redis on Upstash (3 mins)
1. Go to [upstash.com](https://upstash.com) and create a free Redis database (choose your region).
2. Copy the **Redis Connection String (TLS)**:
   ```text
   rediss://default:[YOUR-PASSWORD]@[YOUR-ENDPOINT].upstash.io:6379
   ```

### 3. Backend & Worker on Hugging Face Docker Space (10 mins)
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select **Docker** SDK, Space hardware: **CPU basic (2 vCPU, 16 GB RAM - Free)**.
3. In **Settings > Repository secrets**, add your environment variables:
   - `DATABASE_URL`: Supabase connection URI
   - `REDIS_URL`: Upstash connection URI
   - `SECRET_KEY`: Random 64-character secret
   - `BACKEND_CORS_ORIGINS`: `["*"]` or your Vercel frontend URL
4. Hugging Face builds your `Dockerfile`, installs Playwright Chromium, and gives you a free HTTPS public URL (e.g., `https://princesingh-priceping-api.hf.space`).

### 4. Frontend on Vercel (5 mins)
1. Go to [vercel.com](https://vercel.com) and connect your GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Framework Preset: **Vite**.
4. Add Environment Variable:
   - `VITE_API_URL`: `https://princesingh-priceping-api.hf.space` (or your backend domain).
5. Click **Deploy**. Vercel will build the React SPA and serve it on a global edge CDN with free automatic SSL.

---

## 7. Cost & Quota Management Checklist (Staying $0.00 Forever)

To ensure zero accidental charges across your deployment lifetime:

| Service | Free Tier Boundary | Safety Rule |
| :--- | :--- | :--- |
| **Oracle Cloud** | Up to 4 OCPU, 24 GB RAM, 200 GB Storage | Set an Oracle Cloud Budget Alert at **$0.01** to receive instant alerts if you ever touch paid resources. |
| **Supabase** | 500 MB DB size | Set an Alembic retention script to purge raw price history points older than 180 days (or downsample to 1 data point/day). |
| **Upstash Redis** | 10,000 commands / day | Maintain scraper cache TTL at **1 to 2 hours** to avoid excessive write operations. |
| **Vercel** | 100 GB bandwidth / month | Enable asset caching in `vite.config.ts` so static images and JS bundles are cached by the browser. |
| **Gmail SMTP** | 500 emails / day | Aggregate price drop notifications so users receive a single alert per day per item rather than on every check. |

---

## 8. Summary of Choice

- If you want **the best performance, zero architectural changes, and total freedom to run Playwright scrapers at full speed**, choose **Option 1: Oracle Cloud Always Free**.
- If you want **zero server management and click-to-deploy continuous integration**, choose **Option 2: Vercel + Supabase + Hugging Face Spaces**.
