# Security Threat Assessment Report - Finance Tracker App

This report outlines the security vulnerabilities identified during the analysis of the Finance Tracker codebase.

## 1. Critical Threats

### 1.1 Broken Access Control / Lack of API Authentication
*   **Location:** `web_app/stats.py`
*   **Description:** The FastAPI endpoints (e.g., `/stats/summary/{telegram_id}`) do not implement any authentication or authorization.
*   **Impact:** Any person with knowledge of a user's Telegram ID can access their private financial data (income, expenses, trends).
*   **Recommendation:** Implement authentication middleware. For Telegram Web Apps, the backend should validate the `initData` hash sent from the frontend.

### 1.2 Missing Telegram Web App Data Validation
*   **Location:** `web_app/static/index.html` and Backend API
*   **Description:** The frontend uses `Telegram.WebApp.initDataUnsafe` to get the user's ID and sends it to the API. The API accepts this ID blindly without verifying the cryptographic signature provided by Telegram.
*   **Impact:** Users can easily spoof their identity by modifying the client-side code or sending direct API requests with a different `telegram_id`.
*   **Recommendation:** Pass the full `initData` string to the backend in an `Authorization` header and verify it using the `BOT_TOKEN` on every request.

## 2. High Severity Threats

### 2.1 Stored Cross-Site Scripting (XSS)
*   **Location:** `web_app/static/index.html` (frontend rendering)
*   **Description:** User-supplied data (e.g., income/expense source names) is rendered using `.innerHTML` without sanitization.
*   **Impact:** A malicious user can enter a script as a source name via the Telegram bot. When they (or an admin) view the statistics page, the script will execute in the browser, potentially stealing session data or performing actions on behalf of the user.
*   **Recommendation:** Use `.textContent` instead of `.innerHTML` for rendering user-provided text, or use a sanitization library.

### 2.2 Sensitive Information Disclosure
*   **Location:** `.env`
*   **Description:** The environment file contains a live `BOT_TOKEN` and full database credentials (including passwords) for a Railway-hosted PostgreSQL instance.
*   **Impact:** If this file is committed to version control or otherwise exposed, attackers gain full control over the bot and the entire database.
*   **Recommendation:** Ensure `.env` is in `.gitignore`. Use secret management services in production. Rotate the leaked credentials immediately.

## 3. Medium Severity Threats

### 3.1 Insecure CORS Policy
*   **Location:** `web_app/engine.py`
*   **Description:** `allow_origins=["*"]` is configured in `CORSMiddleware`.
*   **Impact:** Allows any website to interact with the API. While the API is currently unauthenticated, this wide-open policy is dangerous if authentication is added without narrowing the origins.
*   **Recommendation:** Restrict `allow_origins` to the specific domain where the web app is hosted.

### 3.2 Information Disclosure in Error Messages
*   **Location:** `database/db_query.py`
*   **Description:** Database exceptions are caught and printed using `str(er)`.
*   **Impact:** In some configurations, these logs might be exposed, revealing internal database schema, table names, or query logic to attackers.
*   **Recommendation:** Use structured logging and avoid exposing raw exception messages to users or insecure logs.

## 4. Low Severity / Best Practice Findings

### 4.1 Hardcoded Administrative Data
*   **Location:** `config.py`
*   **Description:** `ADMIN_TELEGRAM_ID` is hardcoded in the configuration file.
*   **Recommendation:** Move administrative IDs to environment variables.

### 4.2 Lack of Input Validation
*   **Location:** `handlers/user_main_menu.py`
*   **Description:** Minimum validation on length and content for custom income/expense sources.
*   **Recommendation:** Implement strict input validation and rate limiting to prevent database bloat or UI breakage.
