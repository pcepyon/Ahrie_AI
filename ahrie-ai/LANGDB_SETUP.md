# LangDB Monitoring Setup for Ahrie AI

This guide explains how to set up LangDB monitoring for the Ahrie AI team orchestrator.

## What is LangDB?

LangDB is a monitoring and analytics platform for AI agents that provides:
- Real-time tracing of agent interactions
- Performance monitoring
- Cost tracking
- Conversation analytics
- Debug capabilities

## Setup Instructions

### 1. Get LangDB Credentials

1. Sign up at [https://app.langdb.ai](https://app.langdb.ai)
2. Create a new project
3. Get your API Key and Project ID from the project settings

### 2. Configure Environment Variables

Set the following environment variables:

```bash
export LANGDB_API_KEY="your-langdb-api-key"
export LANGDB_PROJECT_ID="your-project-id"
```

Or add them to your `.env` file:

```env
LANGDB_API_KEY=your-langdb-api-key
LANGDB_PROJECT_ID=your-project-id
```

### 3. How It Works

The team orchestrator (`team_orchestrator_v2.py`) automatically detects LangDB credentials:

- **With LangDB**: Uses `LangDB` model wrapper that sends traces to LangDB platform
- **Without LangDB**: Falls back to standard `OpenAIChat` model (no monitoring)

### 4. Features When LangDB is Enabled

1. **Automatic Tracing**: All agent interactions are logged
2. **Team Coordination Visibility**: See how agents collaborate
3. **Tool Usage Tracking**: Monitor which tools are being used
4. **Performance Metrics**: Track response times and costs
5. **Debug Information**: Access full conversation context

### 5. Viewing Traces

When LangDB is enabled, you can view your traces at:
```
https://app.langdb.ai/projects/{your-project-id}
```

The orchestrator logs this URL when initialized.

### 6. Testing

Run the test script to verify LangDB integration:

```bash
python test_team_orchestrator_v2.py
```

If LangDB is configured, you'll see:
```
✅ LangDB monitoring is enabled!
📊 View traces at: https://app.langdb.ai/projects/your-project-id
```

### 7. Optional: Install pylangdb

For enhanced tracing features, you can install pylangdb (optional):

```bash
pip install pylangdb[agno]  # When available
```

This adds additional tracing capabilities but is not required for basic LangDB model usage.

## Troubleshooting

### LangDB not working?

1. Check credentials are set correctly:
   ```bash
   echo $LANGDB_API_KEY
   echo $LANGDB_PROJECT_ID
   ```

2. Verify initialization in logs:
   ```
   Using LangDB for model and monitoring
   ```

3. Check the monitoring URL in session insights:
   ```python
   insights = orchestrator.get_session_insights()
   print(insights['monitoring'])
   ```

### Fallback to OpenAI

If LangDB credentials are not found, the system automatically falls back to OpenAI:
```
LangDB not configured, using OpenAI directly
```

This ensures the system works even without LangDB monitoring.

## Benefits

1. **No Code Changes**: Just set environment variables
2. **Zero Performance Impact**: Async tracing
3. **Team Insights**: See how your multi-agent system collaborates
4. **Cost Tracking**: Monitor API usage and costs
5. **Debug Production**: Access full traces of production conversations