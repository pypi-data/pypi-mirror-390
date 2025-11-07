# Simultaneous CLI

Command line interface for Simultaneous SDK.

## Installation

### Install from PyPI (Recommended)

```bash
pip install simultaneous-cli
```

### Install from source (Development)

```bash
# Install CLI separately
pip install -e ./cli

# Or install with CLI extras from SDK repo
pip install -e ".[cli]"
```

## Configuration

The CLI uses the hosted API at `https://simultaneous-api.fly.dev` by default. You can override this with:

```bash
export SIMULTANEOUS_API_URL=https://your-api-url.com
export SIMULTANEOUS_FRONTEND_URL=https://your-frontend-url.com
```

### Local Development

To use a locally running API:

```bash
# Linux/Mac
export SIMULTANEOUS_API_URL="http://localhost:8000"

# Windows (PowerShell)
$env:SIMULTANEOUS_API_URL="http://localhost:8000"

# Windows (CMD)
set SIMULTANEOUS_API_URL=http://localhost:8000
```

Then start the API locally:
```bash
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

See `LOCAL_DEV_SETUP.md` in the project root for detailed local development setup.

## Usage

### Authentication

```bash
# Sign up
sim auth signup

# Sign in (prompts for credentials)
sim auth signin

# Sign in via web browser (opens browser for OAuth redirect flow)
sim auth signin --web

# Or simply run without credentials to use web flow
sim auth signin

# Check auth status
sim auth status

# Show current user
sim auth whoami

# Sign out
sim auth signout
```

### Organization Management

```bash
# Create organization
sim orgs create <org-name>

# List organizations
sim orgs list
```

### Project Management

```bash
# Create project
sim projects create <project-name> [--slug <slug>]

# List projects
sim projects list [--archived]

# Get project details
sim projects get <project-id>

# Delete project
sim projects delete <project-id>
```

### Agent Management

```bash
# Create agent
sim agents create <project-id> \
  --name <agent-name> \
  --script <script-content> \
  --script-file <path-to-script> \
  --provider-project-id <browserbase-project-id> \
  [--description <description>] \
  [--env-vars <json-encoded-env-vars>] \
  [--context-id <context-id>] \
  [--extension-id <extension-id>] \
  [--region <region>] \
  [--timeout-sec <seconds>]

# List agents in a project
sim agents list <project-id> [--active-only]

# Get agent details
sim agents get <project-id> <agent-id>

# Delete agent
sim agents delete <project-id> <agent-id>
```

### Running Agents

```bash
# Run an agent
sim run <agent-name> \
  --project-id <project-id> \
  --agent-id <agent-id> \
  --params '{"key": "value"}'
```

### Marketplace

```bash
# Publish agent to marketplace
sim marketplace publish <agent-id> [--project-id <project-id>] [--public/--private]

# List marketplace agents
sim marketplace list

# Deploy agent from marketplace
sim marketplace deploy <marketplace-agent-id> <project-id>
```

### Deployment

```bash
# Deploy agent to cloud (Modal - placeholder for future implementation)
sim deploy agent <project-id> <agent-id>
```

## Setup

No environment variables are required! The CLI works out of the box.

**Optional:** For local development, you can override the API URLs:

```bash
export SIMULTANEOUS_API_URL="http://localhost:8000"
export SIMULTANEOUS_FRONTEND_URL="http://localhost:3000"
```

The CLI uses hardcoded Supabase credentials (anon key) for authentication, so it works on any user's computer without configuration.

## Development

```bash
# Run CLI in development mode
python -m cli.main
```

