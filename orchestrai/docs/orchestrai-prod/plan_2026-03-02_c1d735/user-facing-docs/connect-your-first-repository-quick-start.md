I'll read the key source files simultaneously to build accurate documentation.Let me explore the repository structure to find the correct file paths.Now let me read the existing OrchestrAI user-facing docs and the README for accurate product context:I now have excellent context about OrchestrAI — what it does, how it works, and the language used across existing documentation. I have everything I need to write a comprehensive, accurate, and consistent quick-start guide.

---

# Connect Your First Repository — Quick Start

Welcome to OrchestrAI! This guide takes you from a fresh workspace to your very first completed code analysis in under 10 minutes. By the end, you will have real, actionable insights about your codebase waiting in your dashboard.

---

## Before You Begin

Make sure you have completed two prerequisites:

1. ✅ **An active OrchestrAI account** — if you haven't signed up yet, follow the [Account Setup guide](#) first.
2. ✅ **A code repository** you want to analyse — hosted on GitHub, GitLab, or Bitbucket.

That's all you need. No installations, no pipeline changes, and no special permissions beyond access to your own repository.

---

## Overview: What You're About to Do

| Step | What happens | Time |
|---|---|---|
| **1** | Connect your GitHub, GitLab, or Bitbucket account | ~2 minutes |
| **2** | Select a repository to analyse | ~1 minute |
| **3** | Choose Code Quality as your first analysis | ~30 seconds |
| **4** | Watch the AI agent run | ~3–5 minutes |
| **5** | Read your first results | ~2 minutes |

---

## Step 1: Connect Your Code Hosting Account

After logging in, navigate to the **Code** section from the left sidebar. This is your repository connection hub — the place where OrchestrAI links to your code.

On the Code page, you will see connection options for the three most popular platforms:

- **GitHub**
- **GitLab**
- **Bitbucket**

Click the button for the platform where your code lives. OrchestrAI will redirect you to that platform's own authorisation page — this is the standard, secure way that third-party tools connect without ever storing your password.

### What the authorisation screen will ask

You will be shown a permissions screen on GitHub (or GitLab/Bitbucket). It will ask OrchestrAI for **read access** to your repositories. This allows OrchestrAI to read your code so it can analyse it — it does not push changes, open pull requests, or modify anything without your explicit instruction.

Click **Authorise** (or **Allow**) to approve the connection.

> 💡 **Tip:** If you are connecting a company or organisation repository, you may need to request access from your organisation's administrator before the repository appears in OrchestrAI. Most organisations grant this automatically — if you don't see your repository in the next step, check with your admin.

Once authorised, you are returned to OrchestrAI automatically. Your account is now connected.

---

## Step 2: Select a Repository for Analysis

After connecting your account, the Code page refreshes to display a list of all repositories OrchestrAI can see. This includes:

- Repositories you own personally
- Repositories belonging to any organisations you are a member of (subject to the permissions your organisation has approved)

**Scroll through the list** and find the repository you want to analyse first.

### Tips for choosing your first repository

| Situation | Recommendation |
|---|---|
| You have a project you actively work on | Choose that one — the results will be immediately relevant |
| You manage many repositories | Start with a small-to-medium-sized project so you can review the first results quickly |
| You are evaluating OrchestrAI | Pick a real project rather than an empty or toy repository — you will get much richer results |

Click the name of the repository you want to analyse. OrchestrAI will open that repository's analysis page.

---

## Step 3: Choose Your First Analysis — Start with Code Quality

On the repository page, you will see a menu of available analyses. These represent the different AI agents OrchestrAI can run on your code:

- **Code Quality** *(recommended for first-timers)*
- Security Analysis
- Test Generation
- Compliance Checking
- Documentation Generation
- Instrumentation

### Why start with Code Quality?

Code Quality is the ideal first analysis because:

- **Results are fast** — it typically completes in just a few minutes
- **Results are universal** — every codebase benefits from quality feedback, regardless of age or language
- **Results are easy to understand** — the findings are written in plain language, not security jargon or compliance terminology
- **It sets a baseline** — you will immediately see the strengths and improvement areas of your project

Click **Code Quality** to select it. A confirmation screen will appear summarising:

- The repository name and branch that will be analysed (usually your default/main branch)
- The type of analysis selected
- An estimated completion time

Click **Run Analysis** to start.

---

## Step 4: Understanding the Progress Indicators

Once you start the analysis, OrchestrAI hands your repository off to an AI agent that reads through your code. The page updates in real time to show you what is happening.

### What you will see during the run

The progress view shows a series of stages the agent moves through:

| Stage indicator | What's happening behind the scenes |
|---|---|
| **Connecting to repository** | OrchestrAI is fetching the latest version of your code from the selected branch |
| **Reading codebase** | The AI agent is scanning files and building an understanding of your project's structure, languages, and patterns |
| **Analysing quality** | The agent is evaluating code against quality principles — looking for maintainability issues, inconsistencies, and structural concerns |
| **Generating report** | The agent is writing up its findings in clear, actionable language |
| **Complete** | Your results are ready to view |

You do not need to stay on this page while the analysis runs. You can navigate away and return — OrchestrAI will continue working in the background and notify you when it is done.

> ⏱ **Typical run time:** Most Code Quality analyses complete in **3 to 5 minutes** for small-to-medium repositories. Larger codebases may take a little longer.

---

## Step 5: Reading Your First Results

When the analysis is complete, OrchestrAI displays your Code Quality Results page. This is your first look at what OrchestrAI found in your codebase.

### What the results page shows you

The results are organised into clear sections so you can quickly find what matters most:

#### Overall Quality Score
At the top of the page you will see a summary score for your repository. This gives you an at-a-glance measure of your codebase's current health. Don't worry if the score isn't perfect — the whole point is to identify where to improve.

#### Findings by Category
Below the summary, findings are grouped by type, for example:

- **Maintainability** — areas of the code that may become harder to work with over time (e.g. overly complex functions, code duplication)
- **Consistency** — places where coding style or patterns differ across the project
- **Structure** — architectural concerns that could affect how easy the project is to extend or test
- **Best Practices** — specific patterns that do not follow accepted standards for your language or framework

#### Individual Findings
Each finding includes:

- **A plain-English description** of the issue — what it is and why it matters
- **The location** in your codebase where it was found
- **A severity level** — typically Low, Medium, or High — so you know what to prioritise
- **A suggested improvement** explaining what to do differently

#### What to do with your results

You do not need to address every finding immediately. A good first step is to:

1. **Read the summary** to understand the overall picture
2. **Look at the High severity findings first** — these represent the most impactful improvements
3. **Pick one or two findings** that seem quick to address and make those changes in your code
4. **Run the analysis again** after making improvements to see your score update

> 💾 **Your results are saved.** You can always come back to this page later. OrchestrAI stores every analysis run so you can track how your code quality improves over time.

---

## You've Completed Your First Analysis — What's Next?

Congratulations! You have connected a repository and seen your first real AI-powered results. Here are the natural next steps:

### Run a second analysis on the same repository
Now that you have your Code Quality baseline, consider running **Security Analysis** next. It produces a detailed threat model and flags specific vulnerabilities in your code — all written in plain language, with severity ratings and remediation guidance.

### Analyse additional repositories
Go back to the Code page and connect more of your repositories. You can run analyses on as many repositories as your plan allows.

### Explore Test Generation
OrchestrAI can automatically write unit tests for your codebase — targeting comprehensive coverage across success paths, error cases, and edge conditions. Navigate to your repository's analysis page and select **Test Generation** to try it.

### Review results with your team
Share the results page with colleagues. OrchestrAI's findings are written to be understood by developers and non-developers alike, making them useful for engineering reviews, sprint planning, and conversations with stakeholders.

---

## Quick Troubleshooting

**I don't see my repository in the list after connecting.**
Your organisation may require an administrator to grant OrchestrAI access. Check your organisation's third-party app settings on GitHub/GitLab/Bitbucket, or contact your workspace admin.

**The analysis has been running for a long time.**
Large repositories can take longer to analyse. If the run appears stuck for more than 15 minutes, try refreshing the page. If the issue persists, contact support.

**I was disconnected mid-analysis.**
OrchestrAI runs analyses in the background. Navigate back to the Code page and open your repository — the analysis will either still be in progress or the results will already be waiting for you.

**I connected the wrong account or platform.**
Navigate back to the Code page and look for the option to manage or remove connected accounts. You can disconnect and reconnect with a different platform or a different account at any time.

**I don't understand one of the findings.**
Each finding includes a plain-English description. If something is still unclear, you can use the feedback option on the results page to flag it, or bring the finding to a team discussion — often another developer on your team will have immediate context.

---

## Summary

In just a few steps you have:

- ✅ Connected your GitHub, GitLab, or Bitbucket account to OrchestrAI
- ✅ Selected a repository for analysis
- ✅ Run your first Code Quality analysis
- ✅ Read and understood your results
- ✅ Identified your next steps

OrchestrAI is now set up and ready to help you ship better software. Every time you run an analysis, you get a clearer picture of your codebase — and a concrete plan for making it better.