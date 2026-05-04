# Kognitiv Python SDK — Easy Integration for Institutions

**Version:** v2.7.1  
**Package:** `kognitiv core`  
**License:** Proprietary (Educational)

The Kognitiv Python SDK provides a simple, Pythonic interface to the Kognitiv Core API. Perfect for educational institutions, data scientists, and developers.

---

## 📦 Installation

### From PyPI (When Available)

```bash
pip install kognitiv
```

### Local Development

```bash
# Clone repo
git clone https://github.com//Kognitiv-Analytica/kognitiv-core-python-sdk.git
cd kognitiv-core-python-sdk

# Install with development dependencies
pip install -e ".[dev]"
```

---

##  Quick Start

### Basic Usage

```python
from kognitiv import Kognitiv

# Initialize client with your API key
client = Kognitiv(api_key="sk_edu_xxxxx")

# Ask a question
response = client.chat("What is machine learning?")
print(response.text)

# Check usage
stats = client.usage()
print(f"Used {stats.quota_used} of {stats.quota_limit} requests")

# Close client
client.close()
```

### Context Manager (Recommended)

```python
from kognitiv import Kognitiv

# Automatically handles cleanup
with Kognitiv(api_key="sk_edu_xxxxx") as client:
    response = client.chat("Explain neural networks")
    print(response.text)
```

---

##  Chat Completions

### Simple Question

```python
response = client.chat("What is Python?")
print(response.text)
print(f"Tokens used: {response.usage.total_tokens}")
```

### Customize Response

```python
response = client.chat(
    query="Explain quantum computing",
    temperature=0.5,  # More focused (0.0=deterministic, 2.0=creative)
    max_tokens=500,   # Limit response length
    top_p=0.9,        # Nucleus sampling
)
```

### Stream Response (Real-Time)

```python
print("Streaming response:", end=" ", flush=True)
for chunk in client.chat_stream("Tell me a story"):
    print(chunk, end="", flush=True)
print()
```

---

##  Data Analysis

### Statistical Analysis

```python
data = [10, 15, 20, 25, 30, 35, 40]

response = client.analyze(
    data=data,
    column_name="test_scores",
    analysis_type="statistical"  # mean, median, std, outliers
)

print(f"Insights: {response.choices}")
```

### Trend Analysis

```python
monthly_revenue = [1000, 1200, 1500, 1400, 1600, 1900]

response = client.analyze(
    data=monthly_revenue,
    column_name="revenue",
    analysis_type="trends"  # trend direction, growth rate
)
```

### Forecast

```python
temperature_data = [20.5, 21.2, 19.8, 22.1, 23.0]

response = client.analyze(
    data=temperature_data,
    column_name="daily_temperature",
    analysis_type="forecast"  # predict next values
)
```

---

## Workflows (Multi-Agent)

### Execute Complex Workflows

```python
response = client.workflow(
    query="Analyze sales data and recommend growth strategies",
    context={
        "current_revenue": 100000,
        "growth_rate": "15% YoY",
        "market": "European universities"
    }
)

print(response.text)
```

---

##  Monitoring

### Check API Quota

```python
stats = client.usage()

print(f"Organization: {stats.tier}")
print(f"Used: {stats.quota_used}/{stats.quota_limit}")
print(f"Remaining: {stats.quota_remaining}")
print(f"% Used: {stats.percent_used:.1f}%")
print(f"Resets on: {stats.reset_date}")
```

### List Available Models

```python
models = client.models()
for model in models:
    print(f"- {model}")
```

### Health Check (No Auth Required)

```python
health = client.health()
print(f"API Status: {health['status']}")
print(f"Uptime: {health['uptime']} seconds")
```

---

## ⚡ Async/Await Support

For high-concurrency applications:

```python
import asyncio
from kognitiv import Kognitiv

async def main():
    client = Kognitiv(api_key="sk_edu_xxxxx")
    
    try:
        # Async chat
        response = await client.chat_async(
            "What is async programming?"
        )
        print(response.text)
        
        # Async analysis
        analysis = await client.analyze_async(
            data=[1, 2, 3, 4, 5],
            analysis_type="statistical"
        )
        print(analysis.choices)
    finally:
        client.close()

# Run async
asyncio.run(main())
```

---

##  Error Handling

```python
from kognitiv import (
    Kognitiv,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    KognitivError,
)

try:
    client = Kognitiv(api_key="sk_edu_xxxxx")
    response = client.chat("Hello!")
    
except AuthenticationError:
    print("Invalid API key or expired token")
    
except QuotaExceededError:
    print("Monthly quota exceeded. Please upgrade.")
    
except RateLimitError:
    print("Rate limit reached. Wait 60 seconds before retry.")
    
except KognitivError as e:
    print(f"API Error: {e}")
```

---

##  Configuration

### Custom Base URL (For Self-Hosted)

```python
client = Kognitiv(
    api_key="sk_edu_xxxxx",
    base_url="https://api.my-institution.edu",  # Custom domain
    timeout=60.0  # Request timeout in seconds
)
```

### Environment Variables

```bash
export KOGNITIV_API_KEY="sk_edu_xxxxx"
```

```python
import os
from kognitiv import Kognitiv

api_key = os.getenv("KOGNITIV_API_KEY")
client = Kognitiv(api_key=api_key)
```

---

## Real-World Examples

### Example 1: Academic Q&A System

```python
from kognitiv import Kognitiv

def academic_qa(api_key: str, question: str) -> str:
    """Ask an academic question and get detailed answer."""
    with Kognitiv(api_key=api_key) as client:
        response = client.chat(
            query=question,
            temperature=0.3,  # Factual, less creative
            max_tokens=1000
        )
        return response.text

# Usage
answer = academic_qa(
    api_key="sk_edu_xxxxx",
    question="Explain photosynthesis in detail"
)
print(answer)
```

### Example 2: Assessment Data Analysis

```python
from kognitiv import Kognitiv

def analyze_test_scores(api_key: str, scores: list[float]):
    """Analyze student test scores."""
    with Kognitiv(api_key=api_key) as client:
        # Statistical analysis
        analysis = client.analyze(
            data=scores,
            column_name="test_scores",
            analysis_type="statistical"
        )
        
        # Get recommendations
        workflow = client.workflow(
            query="Based on this score distribution, what interventions would help struggling students?",
            context={"scores": scores}
        )
        
        return analysis.choices, workflow.text

# Usage
scores = [45, 52, 68, 75, 82, 88, 92, 95]
insights, recommendations = analyze_test_scores(
    api_key="sk_edu_xxxxx",
    scores=scores
)
print(f"Insights: {insights}")
print(f"Recommendations: {recommendations}")
```

### Example 3: Batch Processing

```python
import asyncio
from kognitiv import Kognitiv

async def batch_analysis(api_key: str, documents: list[str]):
    """Analyze multiple documents concurrently."""
    client = Kognitiv(api_key=api_key)
    
    try:
        tasks = [
            client.chat_async(f"Summarize: {doc[:500]}")
            for doc in documents
        ]
        
        results = await asyncio.gather(*tasks)
        return [r.text for r in results]
        
    finally:
        client.close()

# Usage
docs = [
    "Document 1 content...",
    "Document 2 content...",
    "Document 3 content...",
]
summaries = asyncio.run(batch_analysis(
    api_key="sk_edu_xxxxx",
    documents=docs
))
```

### Example 4: Integration with Flask

```python
from flask import Flask, jsonify, request
from kognitiv import Kognitiv, KognitivError

app = Flask(__name__)
client = Kognitiv(api_key="sk_edu_xxxxx")

@app.route("/ask", methods=["POST"])
def ask_question():
    """Flask endpoint that uses Kognitiv."""
    data = request.json
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "Question required"}), 400
    
    try:
        response = client.chat(question)
        return jsonify({
            "question": question,
            "answer": response.text,
            "tokens_used": response.usage.total_tokens
        })
    except KognitivError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
```

---

## Testing

### Unit Tests with SDK

```python
import pytest
from kognitiv import Kognitiv

@pytest.fixture
def client():
    """Create test client."""
    return Kognitiv(api_key="sk_edu_test_xxxxx")

def test_chat(client):
    """Test chat endpoint."""
    response = client.chat("Hello")
    assert response.text
    assert response.usage.total_tokens > 0

def test_usage(client):
    """Test usage tracking."""
    stats = client.usage()
    assert stats.quota_limit > 0
    assert stats.quota_used >= 0
    assert stats.quota_remaining >= 0

def test_models(client):
    """Test models list."""
    models = client.models()
    assert isinstance(models, list)
    assert len(models) > 0
```

---

## Troubleshooting

### Issue: "AuthenticationError: Invalid API key"

**Solution:**
- Verify your API key is correct
- Check it hasn't expired
- Generate new key from dashboard: https://dashboard.kognitiv.ai/api-keys

### Issue: "QuotaExceededError: Monthly quota exceeded"

**Solution:**
- Check your usage: `client.usage()`
- Upgrade to higher tier
- Wait for quota reset (typically on the 1st of month)

### Issue: "RateLimitError: Rate limit exceeded"

**Solution:**
- You're sending >100 requests/minute
- Implement exponential backoff retry logic
- Use async for concurrent requests (up to limits)

### Issue: "Timeout waiting for response"

**Solution:**
- Increase timeout: `Kognitiv(..., timeout=60.0)`
- Check your network connection
- API might be experiencing high load

---

## Full API Reference

### Class: `Kognitiv`

```python
Kognitiv(
    api_key: str,                    # Your API key (required)
    base_url: str = "https://api.kognitiv.ai",
    timeout: float = 30.0            # Request timeout in seconds
)
```

### Methods

#### `chat(query, model, temperature, max_tokens, top_p) -> ChatResponse`
- `query` (str): Question or prompt
- `model` (str): Model name (default: kognitiv-core-v2.7)
- `temperature` (float): 0.0-2.0 (default: 0.7)
- `max_tokens` (int): Max response length
- `top_p` (float): 0.0-1.0 (default: 1.0)

#### `analyze(data, column_name, analysis_type) -> AnalysisResponse`
- `data` (list[float]): Numeric values
- `column_name` (str): Label for data
- `analysis_type` (str): "full", "statistical", "trends", "forecast"

#### `workflow(query, model, context) -> ChatResponse`
- `query` (str): Workflow description
- `model` (str): Model to use
- `context` (dict): Additional context

#### `usage() -> UsageStats`
Returns quota information

#### `models() -> List[str]`
Returns available models

#### `close()`
Close HTTP client

---

##  Support

- **Documentation:** https://docs.kognitiv.ai
- **API Reference:** https://api.kognitiv.ai/docs
- **Support Email:** support@kognitiv.ai
- **Status Page:** https://status.kognitiv.ai

---

**Happy integrating! 🚀**
