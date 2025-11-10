# AgentOS SDK

Unified Python SDK for AgentOS platform (the Firewall for AI Agents). All policy checks and telemetry route through the AgentOS Platform API (default: https://app.agentosai.org).

## Install

```bash
pip install agentos-client
```

After installing, you can log in to the platform (assuming you have created an account in https://app.agentosai.org):

```bash
agentos login
```

## CLI Usage

```bash
# Init a starter agent project
agentos init my-agent --template llm

# Build a tarball to deploy
cd my-agent
agentos build . -o my-agent.tar.gz

# Deploy to the platform
agentos deploy my-agent.tar.gz --name my-agent

# List and invoke
agentos list
agentos invoke <agent-id> --payload '{"message": "hello"}'
agentos logs <invocation-id> --follow
```

## SDK Usage

```python
from agentos.sdk import Agent, PolicyDeniedError

agent = Agent(
    agent_id="my-remote-agent",
    tags=["pii_strict"],
)

try:
    text = agent.llm("Summarize our Q3 performance.")
finally:
    agent.complete(result={"ok": True})
```


