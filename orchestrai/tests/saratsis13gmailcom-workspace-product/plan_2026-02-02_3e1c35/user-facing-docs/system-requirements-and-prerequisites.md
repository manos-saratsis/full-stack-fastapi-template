# System Requirements and Prerequisites

## Overview

Before you can start using this application, you need to have certain software installed on your computer. This guide will help you understand what's required and how to verify that your system is ready.

## Required Software

### Docker and Docker Compose

The application runs using Docker, which packages everything needed into containers. You'll need both Docker and Docker Compose installed on your system.

**Docker Compose Version:** The application uses Docker Compose with the modern configuration format (Compose V2).

**Why Docker is Required:** Docker allows the application to run consistently across different computers without worrying about conflicting software installations. Everything you need - the database, web server, and application - runs in isolated containers.

### For Advanced Users: Local Development Requirements

If you plan to work on the application code directly (without using Docker), you'll need:

**Backend Development:**
- Python 3.11 or higher
- PostgreSQL 17 database server

**Frontend Development:**
- Node.js (compatible with the versions supported by Vite 6.x and React 18.x)
- npm (Node Package Manager, included with Node.js)

## Operating System Compatibility

The application works on:

- **Linux** (all major distributions)
- **macOS** (recent versions)
- **Windows** (Windows 10/11 with WSL2 recommended for Docker)

Docker Desktop is available for all these operating systems.

## Account Prerequisites

### GitHub Account (For Deployment)

If you plan to deploy the application to a server, you'll benefit from having a GitHub account. The application includes automated deployment workflows that use GitHub Actions.

**When You Need This:** Only if you want to set up automatic deployments. Not required for local testing.

### Email Service Account (Optional)

The application can send emails for password recovery and notifications. To enable this feature, you'll need access to an email service (like Gmail, SendGrid, or any SMTP-compatible email provider).

**When You Need This:** Only if you want the password recovery feature to work. The application will function without it, but users won't be able to reset their passwords via email.

## Hardware Requirements

### Minimum Specifications

- **RAM:** 4 GB (8 GB recommended)
- **Storage:** 2 GB free disk space for Docker images and containers
- **CPU:** Any modern dual-core processor

### Recommended Specifications

- **RAM:** 8 GB or more
- **Storage:** 10 GB free disk space (allows room for data and logs)
- **CPU:** Quad-core processor or better

**Note:** Docker containers use your system's resources efficiently, but running multiple containers (database, backend, frontend) simultaneously requires adequate memory.

## Verifying Your System

### Check if Docker is Installed

Open your terminal or command prompt and run:

```bash
docker --version
```

You should see output showing Docker version 20.x or higher.

### Check if Docker Compose is Installed

Run:

```bash
docker compose version
```

You should see output showing Docker Compose version 2.x or higher.

**Important:** The command is `docker compose` (two words), not `docker-compose` (hyphenated). The hyphenated version is the older tool.

### Check if Docker is Running

Run:

```bash
docker ps
```

If Docker is running, you'll see a list of containers (possibly empty). If you see an error about Docker not running, start Docker Desktop or the Docker service.

### For Local Development: Check Python Version

Run:

```bash
python --version
```

or

```bash
python3 --version
```

You should see Python 3.11 or higher.

### For Local Development: Check Node.js Version

Run:

```bash
node --version
```

You should see Node.js version 18.x or higher.

## Common Setup Issues and Solutions

### Docker Not Starting

**Problem:** Docker Desktop won't start or shows errors.

**Solutions:**
- On Windows: Ensure WSL2 is installed and updated
- Check that virtualization is enabled in your BIOS settings
- Restart your computer after installing Docker
- Ensure you have administrator/sudo privileges

### "Permission Denied" Errors

**Problem:** Getting permission errors when running Docker commands.

**Solutions:**
- On Linux: Add your user to the docker group: `sudo usermod -aG docker $USER`, then log out and back in
- On Windows/Mac: Ensure Docker Desktop is running with appropriate permissions

### Port Already in Use

**Problem:** Error messages about ports 80, 443, 5432, or 8000 already being in use.

**Solutions:**
- Stop other applications using these ports
- Modify the application's configuration to use different ports
- On Linux: Check if Apache or nginx is running and stop them if not needed

### Insufficient Disk Space

**Problem:** Docker fails to pull images or start containers due to low disk space.

**Solutions:**
- Free up disk space on your system
- Clean up unused Docker images: `docker system prune -a`
- Move Docker's storage location to a drive with more space (in Docker Desktop settings)

### Slow Performance

**Problem:** The application runs slowly or freezes.

**Solutions:**
- Increase memory allocated to Docker (in Docker Desktop settings, increase to at least 4 GB)
- Close unnecessary applications to free up system resources
- Ensure your antivirus isn't scanning Docker files in real-time

## Network Requirements

### Internet Connection

You'll need an internet connection for:
- Initial setup (downloading Docker images)
- Installing dependencies
- Accessing the application if deployed to a server

### Firewall Considerations

If you're setting up the application on a server, ensure these ports are open:
- **Port 80:** HTTP traffic
- **Port 443:** HTTPS traffic (secure connections)
- **Port 22:** SSH access (for server management)

For local development, Docker handles port mapping automatically on localhost.

## What's Included vs. What You Need to Install

### What You Need to Install

- Docker Desktop (or Docker Engine + Docker Compose on Linux)
- A web browser (any modern browser like Chrome, Firefox, Safari, or Edge)
- A text editor (if you plan to modify configuration files)

### What's Included in the Application

The following are automatically set up in Docker containers - you don't need to install them separately:
- PostgreSQL database server
- Python and all required libraries
- Node.js and frontend dependencies
- Web server configuration
- SSL certificate management tools

## Next Steps

Once you've verified that your system meets these requirements:

1. Install any missing software (primarily Docker and Docker Compose)
2. Restart your computer if you just installed Docker
3. Verify your installation using the commands above
4. You're ready to proceed with setting up the application

If you encounter any issues not covered in the troubleshooting section, check the Docker documentation for your operating system or consult the application's community support channels.