# Demo Handbook

## Getting Started
Intro text under Getting Started.

### Overview
Overview narrative.

#### Goals
List the core goals.

#### Non-Goals
Clarify what is out of scope.

### Installation
Steps for installing the tool.

#### Requirements
Ensure `uv` and Python 3.14 are installed.

#### Steps
1. `uv sync`
2. `uv run mkat example.md 1`

## Architecture
Details on the system structure.

### Components
Breakdown of moving pieces.

#### API Gateway
Handles inbound requests.

#### Worker Pool
Processes background jobs.

### Data Flow
Signals how data moves around.

#### Sequence
1. User calls API.
2. Gateway validates request.
3. Worker executes background tasks.
