# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Nova S2S (Speech-to-Speech) workshop demonstrating Amazon Nova Sonic integration with multiple architectures:

1. **Python WebSocket Server + React Client**: Main workshop implementation with bidirectional streaming
2. **LiveKit Integration**: Alternative architecture using LiveKit for voice/video applications
3. **Integration Patterns**: Examples for Bedrock Knowledge Bases (RAG), MCP, Bedrock Agents, and Strands Agent

## Development Commands

### Python Server (python-server/)
```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start server (various modes)
python server.py                    # Basic mode
python server.py --agent mcp        # With MCP integration
python server.py --agent strands    # With Strands Agent
```

### React Client (react-client/)
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### LiveKit UI (livekit/ui/)
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production  
npm run build

# Run tests
npm test
```

### LiveKit Agent (livekit/)
```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run basic agent
uv run python agent.py connect --room my-first-room

# Run agent with tools
uv run python agent-tool.py connect --room my-first-room
```

## Architecture Components

### Core WebSocket Implementation
- `python-server/server.py`: Main entry point for WebSocket server
- `python-server/s2s_session_manager.py`: Handles Nova Sonic bidirectional streaming
- `python-server/s2s_events.py`: Utility class for constructing Nova Sonic events
- `react-client/src/s2s.js`: Main React component for S2S interface
- `react-client/src/helper/audioHelper.js`: Audio utilities for encoding/decoding

### Integration Patterns
- `python-server/integration/bedrock_knowledge_bases.py`: RAG implementation
- `python-server/integration/mcp_client.py`: Model Context Protocol integration  
- `python-server/integration/inline_agent.py`: Bedrock Agents integration
- `python-server/integration/strands_agent.py`: Strands Agent orchestration

### LiveKit Components
- `livekit/agent.py`: Basic LiveKit agent for Nova Sonic
- `livekit/agent-tool.py`: LiveKit agent with tool definitions
- `livekit/ui/`: Custom React UI for LiveKit integration

## Environment Configuration

### Required AWS Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"  
export AWS_DEFAULT_REGION="us-east-1"
```

### Optional WebSocket Configuration
```bash
export HOST="localhost"          # Default: localhost
export WS_PORT=8081             # Default: 8081
export HEALTH_PORT=8082         # Optional: for container deployments
```

### Feature-Specific Environment Variables
```bash
# Bedrock Knowledge Bases
export KB_ID="your_knowledge_base_id"
export KB_REGION="your_kb_region"

# MCP Integration  
export AWS_PROFILE="your_aws_profile"

# Bedrock Agents
export BOOKING_LAMBDA_ARN="your_lambda_arn"

# LiveKit
export LIVEKIT_API_KEY="devkey"
export LIVEKIT_API_SECRET="secret"
```

## Key Technical Details

### Nova Sonic Integration
- Uses AWS SDK Bedrock Runtime with bidirectional streaming
- Handles real-time audio processing with WebSocket connections
- Supports multiple agent frameworks (MCP, Strands, Bedrock Agents)
- Audio format: PCM 16-bit, 8kHz sampling rate

### React Client Architecture
- WebSocket communication with Python server
- Real-time audio capture and playback
- Event-driven architecture for S2S events
- Component structure: App.js → s2s.js → audio helpers

### LiveKit Architecture  
- Separate server/agent/UI components
- WebRTC-based communication
- Token-based authentication system
- Custom React UI components for voice interactions

## Development Notes

- The React clients use `homepage: "/proxy/3000/"` for workshop environments - change to `"."` for standalone deployment
- LiveKit requires Homebrew installation and UV package manager
- Python server supports health check endpoints for container deployments
- Workshop includes CloudFormation templates for Bedrock Agents setup

## Prerequisites

- Python 3.12+
- Node.js 14+ with npm
- AWS account with Bedrock access
- Required AWS Bedrock models: Titan text embedding v2, Nova Lite/Micro/Pro/Sonic
- For LiveKit: Homebrew, UV package manager