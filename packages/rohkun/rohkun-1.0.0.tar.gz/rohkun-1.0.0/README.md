# Rohkun

**Stop wasting tokens. Start fixing.**

Rohkun maps your entire codebase structure so AI knows exactly what's where. No more guessing, no more hallucinations, no more burning through API credits on wrong fixes.

## What It Does

Rohkun analyzes your codebase and generates a comprehensive report showing:

- 🎯 **All API Endpoints** - Every route, handler, and HTTP method
- 📡 **All API Calls** - Every fetch, axios, HTTP request in your frontend
- 📊 **Change Tracking** - See what changed between snapshots
- 📈 **Drift Analysis** - Monitor structural changes over time
- 🔍 **Exact Locations** - File paths and line numbers for everything

Give this report to your AI-powered IDE (Cursor, Windsurf, etc.) and watch it fix bugs on the first try instead of the tenth.

## Installation

```bash
pip install rohkun
```

## Quick Start

### 1. Login

```bash
rohkun login
```

Enter your API key from [rohkun.com](https://rohkun.com)

### 2. Analyze Your Codebase

```bash
cd /path/to/your/project
rohkun run
```

That's it! Rohkun will:
1. Zip your codebase
2. Upload to Rohkun servers for analysis
3. Generate a comprehensive report
4. Copy the report link to your clipboard

### 3. Use With AI

Paste the report link into your AI-powered IDE:

```
Here's my codebase structure: https://rohkun.com/reports/abc123

Now fix the bug where...
```

Your AI now knows:
- Every endpoint and where it's defined
- Every API call and where it's made
- How everything connects
- What changed recently

Result: **First-try fixes instead of 10 failed attempts.**

## Features

### 🚀 Server-Side Analysis

All heavy lifting happens on Rohkun servers:
- AST parsing for 10+ languages
- Pattern matching for frameworks
- Connection detection
- Report generation

Your CLI just uploads and displays results. Fast, lightweight, no heavy dependencies.

### 📊 Local Tracking (Optional)

Track changes over time with local `.rohkun/` snapshots:

```bash
# View snapshot history
rohkun history

# Compare two snapshots
rohkun compare snapshot-1 snapshot-2

# Pause tracking
rohkun pause

# Resume tracking
rohkun track
```

Snapshots are stored locally in `.rohkun/` directory. Optionally sync to server for backup.

### 🎯 What Gets Analyzed

**Backend:**
- Express, Fastify (Node.js)
- FastAPI, Flask, Django (Python)
- Laravel (PHP)
- Spring Boot (Java)
- Gin (Go)
- Rails (Ruby)
- ASP.NET (C#)

**Frontend:**
- React, Vue, Angular
- Vanilla JavaScript/TypeScript
- fetch(), axios, HTTP clients

**Other:**
- GraphQL endpoints and queries
- WebSocket connections
- REST APIs

## Commands

```bash
# Authentication
rohkun login              # Login with API key
rohkun logout             # Logout

# Analysis
rohkun run [directory]    # Analyze codebase (default: current dir)
rohkun run --no-copy      # Don't copy link to clipboard
rohkun run --format plain # Plain text output (no colors)

# Local Tracking
rohkun history            # View snapshot history
rohkun compare <id1> <id2> # Compare two snapshots
rohkun track              # Resume tracking
rohkun pause              # Pause tracking
rohkun delete             # Delete local project data

# Utility
rohkun --version          # Show version
rohkun --help             # Show help
```

## How It Saves You Money

### Without Rohkun:
```
You: "Fix the bug where users can't login"
AI: *tries random fix* ❌
You: "That didn't work, here's more context..."
AI: *tries another fix* ❌
You: "Still broken, let me explain the structure..."
AI: *tries again* ❌
...10 iterations later...
AI: *finally works* ✅

Cost: 10 API calls × 1000 tokens = 10,000 tokens
Time: 2-3 hours
```

### With Rohkun:
```
You: "Here's my codebase: [rohkun link]. Fix the bug where users can't login"
AI: *sees entire structure, fixes precisely* ✅

Cost: 1 API call × 1000 tokens = 1,000 tokens
Time: 5 minutes
```

**Savings: 90% fewer tokens, 95% less time**

## Privacy & Security

- ✅ Your code is uploaded to Rohkun servers for analysis
- ✅ Stored securely during processing
- ✅ You control data retention in your dashboard
- ✅ Delete projects anytime
- ✅ All communication over HTTPS
- ✅ API keys are encrypted

## Pricing

- **Free Tier:** 5 analyses/month
- **Pro Plan:** $12.42/month (100 credits/month)
- **Premium Plan:** $19.08/month (400 credits/month)

See [rohkun.com/pricing](https://rohkun.com/pricing) for details.

## Requirements

- Python 3.8 or higher
- Internet connection (for server communication)
- Rohkun account (free at [rohkun.com](https://rohkun.com))

## Troubleshooting

### "Command not found: rohkun"

Make sure Python's bin directory is in your PATH:

```bash
# On macOS/Linux
export PATH="$HOME/.local/bin:$PATH"

# On Windows
# Add %APPDATA%\Python\Scripts to your PATH
```

### "Clipboard not working"

On Linux, install xclip:

```bash
# Ubuntu/Debian
sudo apt-get install xclip

# Fedora/RHEL
sudo dnf install xclip
```

### "Analysis failed"

Check:
1. You're logged in: `rohkun login`
2. You have credits remaining (check dashboard)
3. Directory contains code files
4. You have internet connection

## Support

- 📧 Email: support@rohkun.com
- 🌐 Website: [rohkun.com](https://rohkun.com)
- 📚 Docs: [docs.rohkun.com](https://docs.rohkun.com)

## License

Copyright (c) 2025 Rohkun. All rights reserved.

This software is proprietary. You may use it to access Rohkun services at rohkun.com, but you may not:
- Modify or reverse engineer the software
- Use it to create competing services
- Redistribute or resell the software

See LICENSE file for full terms.

## What's Next?

1. Install: `pip install rohkun`
2. Sign up: [rohkun.com](https://rohkun.com)
3. Analyze: `rohkun run`
4. Save tokens: Give report to your AI

Stop guessing. Start fixing. 🚀
