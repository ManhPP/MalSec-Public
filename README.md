# 🛡️ MalSec LMS — Malware Analysis Lab Management System

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/backend-FastAPI%20%7C%20Python%203.11-009688.svg)
![React](https://img.shields.io/badge/frontend-React%2018%20%7C%20Vite-61DAFB.svg)
![Proxmox](https://img.shields.io/badge/hypervisor-Proxmox%20VE-E57000.svg)
![Guacamole](https://img.shields.io/badge/VDI-Apache%20Guacamole-green.svg)
![Docker](https://img.shields.io/badge/deployment-Docker%20Compose-2496ED.svg)

**A secure, modern Learning Management System (LMS) designed specifically for Malware Analysis & Cybersecurity Labs.**

*Seamless on-demand VM provisioning, in-browser zero-client VDI, multi-layer submission security scanning, and high-efficiency Speed Grader.*

</div>

---

## 🌟 Key Features

### 🖥️ On-Demand VDI Sandbox Orchestration
- **Instant Browser VDI (<1s latency)**: Students access dedicated isolated virtual machines directly in the browser via Apache Guacamole without installing any client software.
- **Automated Full-Clone Provisioning**: Dynamically clones student sandboxes from Master Templates on **Proxmox VE** with unique local-administered MAC addresses and DHCP IPs.
- **Fast Rollback & Reset**: Revert compromised malware environments to their clean baseline state with a single click.
- **Multi-Protocol Support**: Transparently handles RDP (Windows), VNC, and SSH (Linux) sessions with encrypted JSON SSO tokens.

### 🛡️ Multi-Layer Submission Security & Inspection
- **Strict File Safety Pipeline**: Validates uploaded student submissions before storage.
- **Magic Bytes & Format Verification**: Enforces valid file signatures for PCAPs, PDFs, images, and text logs.
- **DOCX Macro & OLE Inspection**: Scans Word document submissions for hidden malicious VBA macros or suspicious OLE objects before instructors open them.
- **Encrypted ZIP Handling**: Automatically manages password-protected malware sample packages (`.zip`) with anti-zipbomb checks.

### 📊 Modern Cyberpunk LMS & Speed Grader
- **Interactive Speed Grader**: Side-by-side grading workflow with a **Fast Student Switcher** dropdown for rapid evaluation without page reloads.
- **In-Browser Document Previewer**: Native preview of Word (`.docx`) reports rendered with a realistic A4 paper layout, alongside built-in PDF and image previewers.
- **Comprehensive Gradebook**: Matrix view of all student submissions, category-based weighted tags (*Assignment, Lab, Midterm*), and one-click CSV export.
- **Centralized Academic Semesters**: Filter labs, students, and performance metrics by active or archived academic terms.
- **Deadline Extension Engine**: Grant customized individual deadlines per student.

### 📈 Built-in Observability & Monitoring
- **Prometheus & Grafana**: Pre-configured dashboards for real-time tracking of container metrics and Proxmox VE hypervisor health.
- **Loki & Promtail**: Centralized log aggregation for fast incident triage and audit trail inspection.

---

## 🏛️ System Architecture

```text
       ┌────────────────────────────────────────────────────────┐
       │                 Student / Instructor                   │
       │                   Web Browser                          │
       └───────────┬────────────────────────────────┬───────────┘
                   │ HTTPS / WebSocket              │ Web VDI Session
                   ▼                                ▼
       ┌────────────────────────┐      ┌────────────────────────┐
       │   Nginx Reverse Proxy  │      │ Apache Guacamole 1.6.0 │
       │   (malsec-frontend)    │      │ (guacamole-auth-json)  │
       └─────┬────────────┬─────┘      └────────────┬───────────┘
             │            │                         │
      Static │            │ API Reverse Proxy       │ RDP / SSH
      Assets │            ▼                         ▼
             │   ┌───────────────────┐      ┌───────────────────┐
             │   │  FastAPI Backend  │      │   Sandboxed VMs   │
             │   │ (malsec-backend)  │      │   (VLAN Sandbox)  │
             │   └─────┬───────┬─────┘      └───────────────────┘
             │         │       │                      ▲
             ▼         ▼       │                      │
       ┌───────────┐ ┌──────┐  │ Proxmoxer API        │ Clone / Reset
       │ React SPA │ │  DB  │  └──────────────────────┘
       │ (Vite 18) │ │Postgr│       Proxmox VE Hypervisor
       └───────────┘ └──────┘
```

---

## 🚀 Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | React 18, Vite, Lucide Icons, Vanilla CSS | Sleek Cyberpunk dark theme UI, responsive, zero heavy UI frameworks |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Pydantic v2 | High-performance asynchronous REST API, JWT auth, Proxmoxer API |
| **Database** | PostgreSQL 16 | Relational persistence for users, classes, labs, and submissions |
| **Hypervisor** | Proxmox VE (QEMU) | Full-clone VM lifecycle management and resource isolation |
| **VDI Proxy** | Apache Guacamole | Clientless remote desktop gateway using encrypted HMAC/JSON auth |
| **Monitoring** | Grafana, Prometheus, Loki, Promtail | Complete system metrics and log analytics stack |

---

## 🛠️ Quick Start

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (24.0+) and [Docker Compose](https://docs.docker.com/compose/) (v2+)
- A running **Proxmox VE** instance with API token configured
- A running **Apache Guacamole** instance with the `guacamole-auth-json` extension enabled

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/malsec-lms.git
cd malsec-lms
```

### 3. Configure Environment Variables
Copy the sample environment file and configure your parameters:
```bash
cp .env.example .env
```

Open `.env` and fill in:
- `DB_USER`, `DB_PASSWORD`, `DB_NAME`: PostgreSQL credentials
- `JWT_SECRET`: Random 256-bit secret key for authentication
- `INITIAL_ADMIN_USERNAME`, `INITIAL_ADMIN_PASSWORD`: Credentials for the initial bootstrap admin
- `PVE_API_HOST`, `PVE_API_USER`, `PVE_TOKEN_NAME`, `PVE_TOKEN_VALUE`: Proxmox VE connection details
- `GUAC_BASE_URL`, `GUAC_JSON_SECRET`: Guacamole encrypted JSON secret key

### 4. Launch Services
Start the main LMS application:
```bash
docker compose up -d --build
```

Access the application in your browser:
- **LMS Web Application**: `http://localhost:80` (or your configured domain)
- **API Documentation (Swagger)**: `http://localhost:80/docs`

### 5. Launch Monitoring (Optional)
To run the observability stack alongside MalSec:
```bash
docker compose -f docker-compose.monitoring.yml up -d
```
- **Grafana Dashboard**: `http://localhost:3000` (Default: `admin` / `admin`)
- **Prometheus**: `http://localhost:9090`

---

## 📁 Repository Structure

```text
malsec-lms/
├── docker-compose.yml              # Core production stack (Frontend, Backend, Postgres)
├── docker-compose.monitoring.yml   # Monitoring stack (Grafana, Loki, Prometheus, Promtail)
├── .env.example                    # Template environment configuration
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entrypoint & middleware
│   │   ├── config.py               # Fail-fast settings & environment validation
│   │   ├── database.py             # Database engine & session maker
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   ├── security.py             # Password hashing & JWT token generators
│   │   ├── routers/                # REST endpoints (auth, users, classes, labs, submissions)
│   │   └── services/
│   │       ├── vm_service.py       # Proxmox API integration & Guacamole token builder
│   │       ├── file_service.py     # Multi-layer file security validation & ZIP handlers
│   │       └── plagiarism.py       # Similarity and plagiarism analysis helpers
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main React router & global auth context
│   │   ├── index.css               # Cyberpunk design system & CSS variables
│   │   └── pages/
│   │       ├── Login.jsx           # Authentication portal
│   │       ├── StudentDashboard.jsx# Student workspace, markdown guide, VDI iframe
│   │       ├── InstructorDashboard.jsx # Speed Grader, Gradebook, Class & Lab builder
│   │       └── AdminDashboard.jsx  # User management, Semester manager, System audit
│   ├── nginx.conf.template         # Nginx reverse proxy configuration
│   └── package.json
└── monitoring/                     # Grafana dashboards & log scraping configs
```

---

## 🔒 Security & Privacy Notice

- **Malware Handling**: Sandboxes must be placed on an isolated Virtual LAN (e.g., VLAN 30) with strict egress firewall rules to prevent accidental malware infection of university or home networks.
- **Production Credentials**: Always generate strong random secrets for `JWT_SECRET`, `GUAC_JSON_SECRET`, and database passwords before running in production. Never commit `.env` files into source control.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
