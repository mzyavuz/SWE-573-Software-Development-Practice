# Hive - Installation Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Manual Installation](#manual-installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)

---

## Prerequisites

Before installing The Hive, ensure you have the following installed on your system:

### Required
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)

### Optional (for manual installation)
- **Python** (version 3.10 or higher)
- **PostgreSQL** (version 14 or higher)
- **pip** (Python package manager)

### Verify Installation
```bash
docker --version
docker-compose --version
python3 --version
git --version
```

---

## Quick Start with Docker

This is the **recommended** method for running The Hive application.

### 1. Clone the Repository

```bash
git clone https://github.com/mzyavuz/SWE-573-Software-Development-Practice/
cd the-hive
```

### 2. Create Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Or create a new `.env` file in the `the-hive/` directory with the following content:

```env
# Database Configuration
POSTGRES_USER=hiveuser
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=hive_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_SSLMODE=disable

# Application Configuration
BASE_URL=http://localhost:5001
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Build and Start the Application

```bash
# Build the Docker images
docker-compose build

# Start the containers in detached mode
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:5001
- **Backend API**: http://localhost:5001/api
- **Database**: localhost:5433 (PostgreSQL)

### 5. Stop the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

---

## Manual Installation

If you prefer to run the application without Docker:

### 1. Clone the Repository

```bash
git clone https://github.com/mzyavuz/SWE-573-Software-Development-Practice/
cd the-hive
```

### 2. Install PostgreSQL

#### macOS (using Homebrew)
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Windows
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

### 3. Create Database

```bash
# Access PostgreSQL
psql postgres

# Create user and database
CREATE USER hiveuser WITH PASSWORD 'secure_password_here';
CREATE DATABASE hive_db OWNER hiveuser;
GRANT ALL PRIVILEGES ON DATABASE hive_db TO hiveuser;
\q
```

### 4. Install Python Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Configure Environment

Create a `.env` file in the `the-hive/` directory:

```env
POSTGRES_USER=hiveuser
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=hive_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_SSLMODE=disable
BASE_URL=http://localhost:5001
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 6. Run the Application

```bash
# From the backend directory
cd backend
python3 app.py
```

The application will be available at http://localhost:5001

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `hiveuser` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `secure_password` |
| `POSTGRES_DB` | Database name | `hive_db` |
| `POSTGRES_HOST` | Database host | `db` (Docker) or `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `BASE_URL` | Application base URL | `http://localhost:5001` |
| `SECRET_KEY` | Flask secret key for sessions | Random string |

### Generating a Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
---

## Database Setup

### Initialize Database Schema

The application automatically creates the necessary tables on first run. However, you can manually initialize the database:

```bash
# Using Docker
docker-compose exec backend python3 reset_db.py

# Manual installation
cd backend
python3 reset_db.py
```

### Database Reset (Caution: Deletes All Data)

```bash
# Using Docker
docker-compose exec backend python3 reset_db.py

# Manual installation
cd backend
python3 reset_db.py
```

### Seed Forum Categories (Optional)

To populate initial forum categories:

```bash
# From the Helper directory
cd Helper/the-hive-helpers/pythons
python3 seed_forum_categories.py
```

---

## Running the Application

### Development Mode

#### Using Docker
```bash
docker-compose up
```

#### Manual
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python3 app.py
```

