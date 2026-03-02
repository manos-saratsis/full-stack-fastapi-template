I'll fetch the key source files in parallel to build accurate documentation.Let me explore the repository structure to find the relevant files.Now I have enough information from the actual repository to produce accurate, user-facing documentation for OrchestrAI. Here is the complete document:

---

# System Requirements & Prerequisites

Before you start using OrchestrAI, take a few minutes to confirm you meet the requirements below. This will help you connect your repositories and get productive right away — without running into unexpected roadblocks during setup.

---

## Supported Source Code Hosting Platforms

OrchestrAI works with repositories hosted on **GitHub**. You can connect:

- Public GitHub repositories (free, no special settings required)
- Private GitHub repositories (requires a Personal Access Token or OAuth authorization during connection)

> **GitHub is the primary supported platform.** If you use GitLab or Bitbucket, check back — platform support is actively evolving.

---

## Required Account Types & Permissions

### GitHub

To connect a repository and use OrchestrAI effectively, your GitHub account must have:

| Scenario | Minimum Permission Required |
|---|---|
| Public repository | Read access (any GitHub account) |
| Private repository | **Repository Owner** or **Admin** access to authorize OAuth or generate a Personal Access Token |
| Organization repository | At least **Member** role with **Read** access to the specific repository; Owners or Admins can grant this |

> **Why do permissions matter?** OrchestrAI reads your repository contents to generate documentation. It cannot proceed if your account does not have at least read access to the repository you want to analyze.

**What you'll need to have ready:**
- A GitHub account (free accounts are supported)
- Access to the specific repository you want to connect
- If it's a private repository: ability to create a **Personal Access Token** from your GitHub account settings

---

## Browser Requirements

OrchestrAI is a web-based application. For the best experience, use a modern, up-to-date browser:

| Browser | Supported |
|---|---|
| Google Chrome (latest) | ✅ Recommended |
| Mozilla Firefox (latest) | ✅ Supported |
| Microsoft Edge (latest) | ✅ Supported |
| Apple Safari (latest) | ✅ Supported |
| Internet Explorer | ❌ Not supported |

**JavaScript must be enabled** in your browser — OrchestrAI's interface relies on it to function.

---

## Network Requirements

- A **stable internet connection** is required. OrchestrAI connects to GitHub's servers to read your repository in real time.
- No special firewall rules or VPN configurations are required for public repositories.
- If your organization uses a **corporate firewall or proxy**, ensure that outbound HTTPS traffic (port 443) to `github.com` is permitted.

---

## Supported Programming Languages & Frameworks

OrchestrAI is designed to work across a broad range of technology stacks. The following languages and frameworks are well-supported for documentation generation:

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

> OrchestrAI can analyze repositories using other languages and frameworks too — coverage and depth of documentation may vary based on the project's structure and file types.

---

## Team & Workspace Requirements

If you are setting up OrchestrAI for a **team or organization**, keep the following in mind:

- **Each team member** who wants to connect or manage repositories must have their own OrchestrAI account.
- For **organization-owned GitHub repositories**, at least one team member with repository admin rights must authorize the connection initially.
- OrchestrAI supports collaboration — once a repository is connected, documentation generated from it can be shared with teammates within your OrchestrAI workspace.
- There are no hard limits on the number of repositories you can connect, though seat or workspace-level limits may apply depending on your subscription plan. Check the Pricing page for details relevant to your team size.

---

## Quick Pre-Signup Checklist

Before creating your OrchestrAI account or connecting your first repository, confirm the following:

- [ ] I have a GitHub account
- [ ] I have access (at minimum, read access) to the repository I want to analyze
- [ ] For private repositories: I can generate a GitHub Personal Access Token
- [ ] I am using a modern, up-to-date web browser with JavaScript enabled
- [ ] My internet connection allows outbound HTTPS traffic to `github.com`
- [ ] (For teams) At least one team member has admin access to the organization repository

Once you've checked all the boxes above, you're ready to sign up and connect your first repository. Head to the **Sign Up** page to get started.