# Runlayer CLI

The Runlayer CLI enables secure execution of trusted MCP servers with enterprise-grade security, auditing, and permission management. Run Model Context Protocol servers through an authenticated proxy that enforces access controls, maintains audit logs, and manages permissions - allowing AI agents to safely connect to internal systems without exposing credentials or running unvetted code locally.

## Quick Start

The easiest way to get started is to **copy the complete command from the server overview page in your Runlayer app** - it includes all the required parameters pre-filled for your server.

Alternatively, you can construct the command manually:

```bash
uvx runlayer <server_uuid> --secret <your_api_key> --host <runlayer_url>
```

## Usage

### Command Arguments

- `server_uuid`: UUID of your MCP server (found in your Runlayer deployment)

### Command Options

- `--secret`, `-s`: Your Runlayer API key (found under your user settings)
- `--host`: Your Runlayer instance URL (e.g., https://runlayer.example.com)
