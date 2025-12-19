# System Requirements
## The Hive - Community TimeBank Platform

**Date:** December 18, 2025  
**Author:** M. Zeynep Çakmakcı  
**Project:** SWE 573 - Software Development Practice

---

## Table of Contents
1. [Overview](#1-overview)
2. [Server Requirements](#2-server-requirements)
3. [Client Requirements](#3-client-requirements)
4. [Development Environment Requirements](#4-development-environment-requirements)
5. [Software Dependencies](#5-software-dependencies)
6. [Deployment Configurations](#6-deployment-configurations)
7. [Installation Size](#7-installation-size)
8. [Verification](#8-verification)

---

## 1. Overview

### 1.1 Purpose
This document specifies the hardware, software, and network requirements necessary to deploy, develop, and use The Hive Community TimeBank Platform.

### 1.2 Scope
Requirements are provided for:
- **Production Deployment**: Running the application for end users
- **Development Environment**: Setting up for development and testing
- **Client Access**: End user browser and device requirements

### 1.3 Deployment Options
The Hive supports two deployment methods:
1. **Docker Deployment** (Recommended): Containerized deployment with minimal dependencies
2. **Manual Deployment**: Native installation on host system

---

## 2. Server Requirements

### 2.1 Operating System Requirements

#### Supported Operating Systems

| Operating System | Version | Status | Notes |
|------------------|---------|--------|-------|
| **Ubuntu Linux** | 20.04 LTS or higher | ✅ Fully Supported | Recommended for production |
| **Ubuntu Linux** | 22.04 LTS | ✅ Fully Supported | Tested and verified |
| **Debian Linux** | 11 (Bullseye) or higher | ✅ Supported | Compatible |
| **macOS** | 12 (Monterey) or higher | ✅ Supported | Development and testing |
| **macOS** | 13 (Ventura) | ✅ Fully Supported | Tested |
| **macOS** | 14 (Sonoma) | ✅ Fully Supported | Tested |
| **CentOS/RHEL** | 8.x or higher | ⚠️ Compatible | Not extensively tested |
| **Windows** | 10/11 with WSL2 | ⚠️ Compatible | Via Docker Desktop or WSL2 |
| **Windows** | Native | ❌ Not Supported | Use Docker Desktop instead |


### 2.2 Hardware Requirements

#### Minimum Requirements (Development/Testing)
| Component | Specification |
|-----------|---------------|
| **CPU** | 2 cores, 2.0 GHz |
| **RAM** | 2 GB |
| **Storage** | 10 GB free space |
| **Network** | 10 Mbps internet connection |

#### Recommended Requirements (Production - Small Community)
| Component | Specification |
|-----------|---------------|
| **CPU** | 4 cores, 2.5 GHz or higher |
| **RAM** | 4 GB or higher |
| **Storage** | 50 GB SSD |
| **Network** | 100 Mbps internet connection |

#### Recommended Requirements (Production - Large Community)
| Component | Specification |
|-----------|---------------|
| **CPU** | 8+ cores, 3.0 GHz or higher |
| **RAM** | 8 GB or higher |
| **Storage** | 100 GB SSD (NVMe preferred) |
| **Network** | 1 Gbps internet connection |

#### Storage Breakdown
- **Application Code**: ~200 MB
- **Python Dependencies**: ~500 MB
- **Database (PostgreSQL)**: ~100 MB (base) + growth based on usage
  - Estimated: 1 MB per 100 users
  - Estimated: 500 KB per 100 services
  - Estimated: 2 MB per 1000 transactions
- **Logs**: 10-100 MB per month (depending on traffic)
- **Docker Images**: ~1.5 GB (if using Docker)

#### Scalability Guidelines
| Community Size | Users | Services | CPU | RAM | Storage |
|----------------|-------|----------|-----|-----|---------|
| Small | 10-100 | 50-500 | 2 cores | 2 GB | 10 GB |
| Medium | 100-500 | 500-2000 | 4 cores | 4 GB | 50 GB |
| Large | 500-2000 | 2000-10000 | 8 cores | 8 GB | 100 GB |
| Very Large | 2000+ | 10000+ | 16+ cores | 16+ GB | 200+ GB |

### 2.3 Server Software Requirements

#### Core Requirements (Manual Deployment)

**Python**
- **Required Version**: Python 3.10 or higher
- **Recommended Version**: Python 3.11 or 3.12
- **Package Manager**: pip 23.0 or higher

**Database**
- **Required**: PostgreSQL 14 or higher
- **Recommended**: PostgreSQL 15 or 16
- **Extensions**: None required (standard installation sufficient)

**Additional System Tools**
- **git**: Version control (2.30 or higher)
- **curl** or **wget**: For downloading dependencies
- **build-essential** (Linux) or **Xcode Command Line Tools** (macOS): For compiling Python packages

#### Docker Deployment Requirements

If using Docker deployment (recommended):

**Docker**
- **Required Version**: Docker 20.10 or higher
- **Recommended Version**: Docker 24.0 or higher
- **Platform**: Docker Engine (Linux) or Docker Desktop (macOS/Windows)

**Docker Compose**
- **Required Version**: Docker Compose 1.29 or higher
- **Recommended Version**: Docker Compose 2.20 or higher
- **Note**: Included with Docker Desktop

#### Optional Components

**Web Server (Production)**
- **Nginx**: 1.18 or higher (for reverse proxy)
- **Apache**: 2.4 or higher (alternative)

**Process Manager (Production)**
- **Gunicorn**: 20.1 or higher (WSGI server)
- **Supervisor**: 4.2 or higher (process control)

**SSL/TLS Certificate**
- **Let's Encrypt** (free, recommended for production)
- **Certbot**: For automatic certificate management

---

## 3. Client Requirements

### 3.1 Web Browser Requirements

#### Supported Browsers

| Browser | Minimum Version | Recommended Version | Status |
|---------|----------------|---------------------|--------|
| **Google Chrome** | 90 | 120+ (latest) | ✅ Fully Supported |
| **Mozilla Firefox** | 88 | 121+ (latest) | ✅ Fully Supported |
| **Safari** | 14 | 17+ (latest) | ✅ Supported |
| **Microsoft Edge** | 90 | 120+ (latest) | ✅ Fully Supported |
| **Opera** | 76 | Latest | ⚠️ Compatible |
| **Brave** | Latest | Latest | ⚠️ Compatible |
| **Internet Explorer** | Any | N/A | ❌ Not Supported |

#### Browser Features Required
- **JavaScript**: Must be enabled
- **Cookies**: Must be enabled
- **Local Storage**: Must be enabled (for session management)
- **Geolocation API**: Optional (for map centering, fallback available)
- **Modern CSS**: CSS3 support required
- **Fetch API**: For AJAX requests

### 3.2 Device Requirements

#### Desktop/Laptop
| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10+, macOS 10.15+, or Linux |
| **Screen Resolution** | 1280x720 minimum, 1920x1080 recommended |
| **RAM** | 4 GB minimum |
| **Network** | Broadband internet connection (5 Mbps minimum) |

#### Tablet
| Component | Requirement |
|-----------|-------------|
| **Operating System** | iOS 14+, Android 10+, or iPadOS 14+ |
| **Screen Size** | 7 inches or larger |
| **Browser** | Safari (iOS) or Chrome (Android) |
| **Network** | WiFi or 4G/5G connection |
| **Note** | Responsive design works but not extensively tested |

#### Mobile Phone
| Component | Requirement |
|-----------|-------------|
| **Operating System** | iOS 14+, Android 10+ |
| **Screen Size** | 5 inches or larger recommended |
| **Browser** | Safari (iOS) or Chrome (Android) |
| **Network** | WiFi or 4G/5G connection |
| **Note** | Responsive design works but not extensively tested |

### 3.3 Network Requirements (Client)
- **Minimum Bandwidth**: 5 Mbps download, 1 Mbps upload
- **Recommended Bandwidth**: 25 Mbps download, 5 Mbps upload
- **Latency**: <200ms to server
- **Connection**: Stable internet connection required

---

## 4. Development Environment Requirements

### 4.1 Operating System (Development)
- **macOS**: 12 (Monterey) or higher ✅ Recommended
- **Linux**: Ubuntu 20.04 LTS or higher ✅ Recommended
- **Windows**: 10/11 with WSL2 ⚠️ Requires WSL2 setup

### 4.2 Required Development Tools

**Code Editor / IDE**
- **VS Code**: 1.75 or higher (recommended)
- **PyCharm**: 2023.1 or higher (professional or community)
- **Vim/Emacs**: Latest versions (for advanced users)

**Version Control**
- **Git**: 2.30 or higher
- **GitHub CLI** (optional): Latest version

**Python Development**
- **Python**: 3.10, 3.11, or 3.12
- **pip**: 23.0 or higher
- **virtualenv** or **venv**: For virtual environments
- **pipenv** or **poetry** (optional): Alternative package managers

**Database Tools**
- **PostgreSQL**: 14 or higher
- **psql**: Command-line interface
- **pgAdmin** (optional): GUI for database management
- **DBeaver** (optional): Universal database tool

**Testing Tools**
- **pytest**: 7.0 or higher
- **requests**: 2.28 or higher (for API testing)

**Container Tools (Optional but Recommended)**
- **Docker Desktop**: Latest version
- **Docker Compose**: Latest version

### 4.3 Development Dependencies

All Python dependencies are managed in `requirements.txt`:

```
Flask==3.0.0
Flask-Migrate==4.0.5
Flask-Bcrypt==1.0.1
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
pytest==7.4.3
Werkzeug==3.0.1
```

---

## 5. Software Dependencies

### 5.1 Backend Dependencies

#### Core Framework
| Package | Version | Purpose |
|---------|---------|---------|
| **Flask** | 3.0.0 | Web application framework |
| **Werkzeug** | 3.0.1 | WSGI utility library (included with Flask) |

#### Database
| Package | Version | Purpose |
|---------|---------|---------|
| **psycopg2-binary** | 2.9.9 | PostgreSQL adapter for Python |

#### Authentication & Security
| Package | Version | Purpose |
|---------|---------|---------|
| **Flask-Bcrypt** | 1.0.1 | Password hashing |

#### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| **python-dotenv** | 1.0.0 | Environment variable management |
| **requests** | 2.31.0 | HTTP library for external API calls |

#### Testing
| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | 7.4.3 | Testing framework |

#### Production Server
| Package | Version | Purpose |
|---------|---------|---------|
| **gunicorn** | 21.2.0 | WSGI HTTP server (production) |


### 5.2 External Service Dependencies
#### Optional Services
- **Wikibase/Wikidata API**: For semantic tag suggestions
  - Graceful degradation if unavailable
  - No API key required


### 5.3 System Libraries

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    build-essential \
    git \
    curl
```

#### macOS
```bash
# Using Homebrew
brew install python@3.10 postgresql git
```


---

## 6. Deployment Configurations

### 6.1 Docker Deployment (Recommended)

#### Requirements
```yaml
System:
  - Docker: 20.10+
  - Docker Compose: 1.29+
  - Disk Space: 5 GB (for images and volumes)
  - RAM: 2 GB minimum

Configuration Files:
  - docker-compose.yml
  - Dockerfile
  - .env (from .env.example)
```

### 6.2 Manual Deployment

#### Requirements
```
System:
  - Python 3.10+
  - PostgreSQL 14+
  - pip 23.0+
  - virtualenv or venv
  - 2 GB RAM minimum
  - 10 GB disk space

Optional (Production):
  - Nginx or Apache
  - Gunicorn
  - Supervisor
  - SSL certificate
```

#### Advantages
- ✅ Direct control over all components
- ✅ Lower resource overhead
- ✅ No Docker dependency
- ✅ Easier debugging for Python developers

#### Disadvantages
- ❌ More complex setup
- ❌ Manual dependency management
- ❌ Platform-specific configurations
- ❌ Requires separate PostgreSQL installation

### 6.4 Cloud Deployment Options

#### DigitalOcean
- **Droplet**: 2 GB RAM, 2 vCPU 
- **Managed Database**: PostgreSQL 14+


#### Self-Hosted (VPS)
- **Provider**: DigitalOcean, Linode, Vultr, etc.
- **Specs**: 2 GB RAM, 2 vCPU, 50 GB SSD

### 6.5 Environment Configuration

Required environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hive_db

# Application
FLASK_APP=app.py
FLASK_ENV=production  # or development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

```

---

## 7. Installation Size

### 7.1 Disk Space Requirements

**Docker Deployment**:
- Docker images: ~1.5 GB
- Application code: ~200 MB
- Python dependencies: ~500 MB
- Database volume: ~100 MB (initial)
- **Total**: ~2.5 GB minimum

**Manual Deployment**:
- Application code: ~200 MB
- Python virtual environment: ~500 MB
- PostgreSQL data: ~100 MB (initial)
- **Total**: ~1 GB minimum


---

## 8. Verification

### 8.1 System Requirements Check

**Check Python Version**:
```bash
python3 --version
# Should be 3.10 or higher
```

**Check PostgreSQL**:
```bash
psql --version
# Should be 14 or higher
```

**Check Docker** (if using Docker):
```bash
docker --version
docker-compose --version
```

**Check Disk Space**:
```bash
df -h
# Ensure at least 10 GB free
```

**Check Memory**:
```bash
free -h  # Linux
# or
vm_stat  # macOS
# Ensure at least 2 GB free
```


For detailed installation instructions, refer to [INSTALL.md](../the-hive/INSTALL.md).



**End of System Requirements Document**
