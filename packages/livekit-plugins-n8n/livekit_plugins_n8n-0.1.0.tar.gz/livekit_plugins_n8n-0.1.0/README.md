# LiveKit N8n Plugin

Integrate [n8n](https://n8n.io/) webhooks with [LiveKit](https://livekit.io/) voice AI agents for seamless conversational AI experiences.

## Developer: Haitham Ramdan

- [GitHub](https://github.com/haitham-ramadan)
- [LinkedIn](https://www.linkedin.com/in/haitham-ramadan-alyamani)

## Features

- 🎙️ **Voice AI Integration**: Connect n8n workflows directly to LiveKit voice agents
- 🔄 **Session Management**: Automatic conversation tracking with session IDs
- 👤 **User Identity**: Pass participant information to your n8n workflows
- 🚀 **Simple API**: Easy-to-use interface following LiveKit plugin conventions
- 📝 **Full Logging**: Comprehensive logging for debugging and monitoring
- 🌐 **Flexible Configuration**: Support for both direct URLs and environment variables

## Installation

```bash
pip install livekit-plugins-n8n
```

## Quick Start

### 1. Set up your n8n webhook

Create a webhook in n8n that accepts POST requests with this payload:

```json
{
  "query": "user's message",
  "session_id": "unique_session_id",
  "user_identity": "user_identifier"
}
```

Your webhook should return one of these formats:

**Format 1 (Array):**
```json
[
  {
    "output": "AI response text"
  }
]
```

**Format 2 (Object):**
```json
{
  "output": "AI response text"
}
```

### 2. Use in your LiveKit agent

```python
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, WorkerOptions
from livekit.plugins import n8n, deepgram, silero, elevenlabs
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful voice AI assistant."
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    # Get participant information
    participant_identity = "unknown_user"
    if ctx.room.remote_participants:
        first_participant = next(iter(ctx.room.remote_participants.values()))
        participant_identity = first_participant.identity

    # Initialize n8n LLM
    llm = n8n.LLM(
        webhook_url="https://your-n8n.cloud/webhook/livekit",
        session_id=ctx.room.name,
        participant_identity=participant_identity
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=llm,
        tts=elevenlabs.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    assistant = Assistant()
    
    await session.start(room=ctx.room, agent=assistant)
    
    # Optional: Say a greeting
    await session.say(
        "Hello! How can I help you today?", 
        allow_interruptions=True
    )


if __name__ == "__main__":
    agents.cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```env
# Required
N8N_WEBHOOK_URL=https://your-n8n.cloud/webhook/livekit

# LiveKit credentials
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Plugin API keys
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### LLM Initialization Options

**Option 1: Direct URL**
```python
llm = n8n.LLM(
    webhook_url="https://your-n8n.com/webhook/livekit")
```


## Example n8n Workflow

Here's a basic n8n workflow structure:

### Workflow Nodes

1. **Webhook Node** (Trigger)
   - Method: POST
   - Path: `/webhook/livekit`
   - Receive these fields: `query`, `session_id`, `user_identity`

2. **Process Node** (Your AI Logic)
   - Examples:
     - Call OpenAI/Anthropic API
     - Query your database
     - Run custom business logic
     - Use n8n AI nodes

3. **Respond to Webhook Node**
   - Return JSON:
   ```json
   [
     {
       "output": "{{ $json.ai_response }}"
     }
   ]
   ```


## Advanced Usage

### Session-Based Conversations

The plugin automatically tracks conversations using `session_id`. Use this in your n8n workflow to:
- Store conversation history in a database
- Maintain context across multiple messages
- Implement custom memory/RAG systems

```python
# The session_id is automatically set to the room name
llm = n8n.LLM(
    webhook_url="https://your-n8n.com/webhook/livekit",
    session_id=ctx.room.name  # Unique per room
)
```

### User-Specific Responses

Use `participant_identity` to personalize responses:

```python
llm = n8n.LLM(
    webhook_url="https://your-n8n.com/webhook/livekit",
    participant_identity=participant.identity
)
```

In your n8n workflow, access this via `{{ $json.user_identity }}` to:
- Fetch user preferences
- Load user-specific data
- Implement authorization logic

## Troubleshooting

### Common Issues

**1. Webhook timeout**
```
APIConnectionError: n8n Webhook API error
```
- Ensure your n8n webhook responds within 30 seconds
- Check n8n workflow execution logs
- Verify webhook URL is correct

**2. Invalid response format**
```
ValueError: Unexpected response format from n8n
```
- Ensure response contains `output` field
- Check response format matches one of the supported formats
- Test webhook directly with curl/Postman

**3. Missing environment variables**
```
ValueError: webhook_url or N8N_WEBHOOK_URL environment variable is required
```
- Set `N8N_WEBHOOK_URL` in your `.env` file
- Or pass `webhook_url` directly to `n8n.LLM()`

### Testing Your Webhook

Test with curl:

```bash
curl -X POST https://your-n8n.com/webhook/livekit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello",
    "session_id": "test_123",
    "user_identity": "test_user"
  }'
```

Expected response:
```json
[{"output": "Hello! How can I help you?"}]
```

## Requirements

- Python 3.9+
- LiveKit Agents SDK
- aiohttp
- n8n instance (self-hosted or cloud)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

- 📧 Issues: [GitHub Issues](https://github.com/haitham-ramadan/livekit-plugins-n8n/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/haitham-ramadan/livekit-plugins-n8n/discussions)
- 📖 LiveKit Docs: [docs.livekit.io](https://docs.livekit.io)
- 🔧 n8n Docs: [docs.n8n.io](https://docs.n8n.io)

## Related Projects

- [LiveKit](https://livekit.io/) - Real-time communication platform
- [n8n](https://n8n.io/) - Workflow automation platform
- [LiveKit Agents](https://github.com/livekit/agents) - Agent framework for LiveKit

---

Made with ❤️ by [Haitham Ramdan](https://github.com/haitham-ramadan)# livekit-plugins-n8n
