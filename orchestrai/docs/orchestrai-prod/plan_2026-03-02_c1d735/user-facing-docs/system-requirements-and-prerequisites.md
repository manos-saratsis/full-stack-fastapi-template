I'll fetch the key source files in parallel to build accurate documentation.Let me explore the actual repository structure to find the relevant files.I found a previously generated system requirements document in the repository. Let me read it along with the README for accurate details.I now have all the information needed. I have the previously generated OrchestrAI system requirements document and the full repository README confirming the technology stack. Here is the complete, refined documentation:

---

# System Requirements & Prerequisites

Before you start using OrchestrAI, take a few minutes to confirm you meet the requirements below. This will help you connect your repositories and get productive right away — without running into unexpected roadblocks during setup.

---

## Supported Source Code Hosting Platforms

OrchestrAI works with repositories hosted on **GitHub**. You can connect:

- **Public GitHub repositories** — free to connect, no special settings required.
- **Private GitHub repositories** — requires authorizing OrchestrAI via OAuth or providing a Personal Access Token during the connection process.

> **Note:** GitHub is the primary supported platform at this time. GitLab and Bitbucket support is on the roadmap — check back for updates.

---

## Required Account Types & Permissions

### GitHub

To connect a repository and use OrchestrAI effectively, your GitHub account must meet the following requirements:

| Scenario | Minimum Permission Required |
|---|---|
| Public repository | Read access (any GitHub account qualifies) |
| Private repository | **Repository Owner** or **Admin** — needed to authorize OAuth or generate a Personal Access Token |
| Organization-owned repository | At least **Member** role with **Read** access to the specific repository; an Owner or Admin must grant this if not already in place |

> **Why do permissions matter?** OrchestrAI reads your repository contents in order to generate documentation. If your account does not have at least read access to a repository, it cannot be analyzed.

**What to have ready before connecting:**
- A GitHub account (free accounts are fully supported)
- Access to the specific repository you want to analyze
- For private repositories: the ability to create a **Personal Access Token** from your GitHub account settings

---

## Browser Requirements

OrchestrAI is a web-based application — nothing to install. For the best experience, use a modern, up-to-date browser:

| Browser | Support Status |
|---|---|
| Google Chrome (latest version) | ✅ Recommended |
| Mozilla Firefox (latest version) | ✅ Supported |
| Microsoft Edge (latest version) | ✅ Supported |
| Apple Safari (latest version) | ✅ Supported |
| Internet Explorer (any version) | ❌ Not supported |

**JavaScript must be enabled** in your browser — OrchestrAI's interface depends on it to function correctly.

---

## Network Requirements

- A **stable internet connection** is required. OrchestrAI connects to GitHub in real time to read and analyze your repository.
- No special firewall rules or VPN configurations are needed for public repositories.
- If your organization uses a **corporate firewall or proxy**, ensure that outbound HTTPS traffic (port 443) to `github.com` is permitted.

---

## Supported Programming Languages & Frameworks

OrchestrAI is designed to work across a wide variety of technology stacks. The following languages and frameworks are well-supported for documentation generation:

**Languages:**
- Python
- TypeScript / JavaScript
- HTML / CSS

**Frameworks & Tools:**
- FastAPI (Python backend framework)
- React (frontend framework)
- SQLModel / SQLAlchemy (database ORM)
- PostgreSQL (relational database)
- Docker / Docker Compose (containerization)

> OrchestrAI can also analyze repositories that use other languages and frameworks. The depth and coverage of generated documentation may vary depending on your project's structure and file types.

---

## Team & Workspace Requirements

If you are setting up OrchestrAI for a **team or organization**, keep the following in mind:

- **Each team member** who wants to connect or manage repositories must have their own OrchestrAI account.
- For **organization-owned GitHub repositories**, at least one person with repository admin rights must authorize the connection the first time.
- Once a repository is connected, the documentation generated from it can be shared with teammates within your OrchestrAI workspace.
- Seat limits and workspace-level restrictions may apply depending on your subscription plan. Visit the **Pricing** page on the OrchestrAI website for details relevant to your team size.

---

## Quick Pre-Signup Checklist

Use this checklist to confirm you're ready before creating your OrchestrAI account or connecting your first repository:

- [ ] I have a GitHub account
- [ ] I have at least **read access** to the repository I want to analyze
- [ ] For private repositories: I can generate a **GitHub Personal Access Token**
- [ ] I am using a modern, up-to-date web browser with JavaScript enabled
- [ ] My internet connection allows outbound HTTPS traffic to `github.com`
- [ ] *(For teams)* At least one team member has admin access to the organization repository

Once every box is checked, you're ready to get started. Head to the **Sign Up** page on the OrchestrAI website to create your account and connect your first repository.