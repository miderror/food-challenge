# Food Challenge Bot ✨

A Telegram bot to help users track their dietary diversity through the "400 Food Challenge". This project includes a user-facing bot built with **aiogram** and a powerful admin panel powered by **Django**.

## Features

-   **User Bot**:
    -   Easy registration process.
    -   Add products via categories or a fast inline search.
    -   View personal profile with progress stats (eaten count, days in challenge, BMI).
    -   Export the full list of eaten products to a `.txt` file.
    -   Suggest new products to be added to the database.

-   **Admin Panel**:
    -   Manage users and view their statistics.
    -   Full CRUD (Create, Read, Update, Delete) for products and categories.
    -   Moderate user-suggested products.
    -   Edit all bot content (static texts, FAQ, "About" section).
    -   Schedule and send mass broadcasts to all users.

## Tech Stack

-   **Backend**: Django
-   **Telegram Bot**: aiogram 3
-   **Database**: PostgreSQL
-   **Task Queue**: Celery
-   **Broker / Cache**: Redis
-   **Containerization**: Docker, Docker Compose
-   **Web Server (Prod)**: Nginx + Gunicorn

## Getting Started

### 1. Prerequisites

-   Docker and Docker Compose must be installed.
-   Clone the repository: `git clone <your-repo-link>`
-   Navigate to the project directory: `cd food-challenge`

### 2. Configuration

Create a `.env` file in the project root and fill it with your credentials.

```env
# Django
DJANGO_SECRET_KEY=your_strong_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL
POSTGRES_DB=food_challenge_db
POSTGRES_USER=food_challenge_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Telegram Bot
BOT_TOKEN=your_telegram_bot_token
```

### 3. Running the Project

The project uses a `Makefile` for convenient command execution.

#### Development

1.  **Build and run all services:**
    ```bash
    make dev-up
    ```
2.  **Apply database migrations:**
    ```bash
    make dev-migrate
    ```
3.  **Create an admin user:**
    ```bash
    make dev-superuser
    ```
    *The admin panel will be available at `http://localhost/admin/`.*

4.  **(Optional) Seed the database with products:**
    ```bash
    make dev-seed-products
    ```

---

#### Other useful commands:
-   `make dev-logs s=bot`: View real-time logs for a service (e.g., `bot`, `backend`).
-   `make dev-down`: Stop and remove all running containers.

#### Production

For production deployment, use the `prod-*` commands (`make prod-up`, `make prod-migrate`, etc.), which use `Gunicorn` and optimized Docker settings.
