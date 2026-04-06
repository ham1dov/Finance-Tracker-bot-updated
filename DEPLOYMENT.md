# Deployment Guide: Zero-Budget Hosting for Finance Tracker

This guide explains how to host the Finance Tracker application (FastAPI + Telegram Bot) for free or at a very low cost, ensuring it runs 24/7 without manual intervention.

## 1. Zero-Cost Stack (Recommended)

To run this app for free permanently, you can use a combination of two services.

### Application Hosting (Bot + Web API)
**Service: [Koyeb](https://www.koyeb.com/) or [Hugging Face Spaces](https://huggingface.co/spaces)**

*   **Koyeb (Nano Tier):**
    *   **Cost:** $0/month.
    *   **Pros:** Native support for Docker and Python, easy deployment from GitHub, no "sleep" mode on the free tier (unlike Render).
    *   **Setup:** Connect your GitHub repo, select "Python" runtime, set the run command to `python main.py`, and add your `.env` variables in the Koyeb dashboard.
*   **Hugging Face Spaces (Docker/Python):**
    *   **Cost:** $0/month.
    *   **Pros:** Extremely stable, runs 24/7.
    *   **Setup:** Create a new "Space", choose "Docker" or "Blank", upload your code, and Hugging Face will provide a public URL for your WebApp and keep the bot running.

### Database Hosting (PostgreSQL)
**Service: [Neon.tech](https://neon.tech/) or [Supabase](https://supabase.com/)**

*   **Neon.tech:**
    *   **Cost:** Free (0.25 vCPU, 500MB storage).
    *   **Pros:** Modern PostgreSQL, automatic scaling, "always-on" for the primary branch.
    *   **Setup:** Create a project, get the `Connection String`, and update your `DATABASE_URL` in the environment variables.
*   **Supabase:**
    *   **Cost:** Free tier includes a managed Postgres DB.
    *   **Pros:** Very reliable.

---

## 2. Low-Budget Options ($5 - $10 / month)

If your user base grows, you might want more resources and guaranteed uptime.

*   **Hetzner / DigitalOcean / Linode:**
    *   A small VPS (Virtual Private Server) for ~$4-6/month can run the Bot, Web API, and Database all in one place.
    *   **Pros:** Full control, no limitations.
*   **Railway.app:**
    *   The current project is configured with Railway URLs. They have a "Pay-as-you-go" model that is very affordable for low-traffic apps (often <$1/month).

---

## 3. Step-by-Step Deployment (Koyeb Example)

1.  **Prepare your Repo:** Ensure your `requirements.txt` and `main.py` are in the root directory.
2.  **Create a Neon Database:**
    *   Go to [Neon.tech](https://neon.tech/) and create a DB.
    *   Run the contents of `database/create_tables.sql` in the Neon SQL Editor to set up the schema.
3.  **Setup Koyeb:**
    *   Create a Koyeb account.
    *   Click **"Create Service"** -> **"GitHub"**.
    *   Select your repository.
    *   In **Environment Variables**, add:
        *   `BOT_TOKEN`: Your Telegram Bot Token.
        *   `DATABASE_URL_TG`: Your Neon Connection String.
        *   `DATABASE_URL_WEB`: Same as above (with `+asyncpg` for SQLAlchemy).
    *   Set **Health Check** to HTTP port `8000` (FastAPI).
4.  **Launch:** Koyeb will build the app and give you a public URL (e.g., `https://myapp-user.koyeb.app`).

## 4. Keeping it Alive (Render-specific)

If you use **Render's** free tier, the app will "sleep" after 15 minutes of inactivity. To prevent this:
1.  Use a free service like [Cron-job.org](https://cron-job.org/) or [UptimeRobot](https://uptimerobot.com/).
2.  Set it to "ping" your WebApp URL every 10 minutes. This will keep the bot running continuously.

## 5. Security Note
Never commit your `.env` file to GitHub. Always use the hosting provider's "Environment Variables" or "Secrets" section to store tokens and database URLs.
