# External Service Setup Guides

This guide provides step-by-step instructions for setting up external services commonly used with KayGraph examples.

## Quick Reference

| Service | Purpose | Free Tier | Setup Time |
|---------|---------|-----------|------------|
| OpenAI | LLM, Embeddings, STT, TTS | $5 credit | 5 min |
| Anthropic | Claude LLM | No | 5 min |
| Google Cloud | Various AI services | $300 credit | 20 min |
| Groq | Fast LLM inference | Yes | 5 min |
| Serper | Web search API | 2,500 searches | 5 min |
| Voyage AI | Embeddings | 50M tokens | 5 min |

## OpenAI Setup

### 1. Create Account
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up with email or Google account
3. Verify email address

### 2. Generate API Key
1. Navigate to [API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Name your key (e.g., "kaygraph-dev")
4. Copy the key immediately (won't be shown again)

### 3. Set Environment Variable
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."

# Windows
set OPENAI_API_KEY=sk-...

# Or use .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

### 4. Test Connection
```python
# test_openai.py
import os
import requests

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not set")
    exit(1)

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
)

if response.status_code == 200:
    print("✅ OpenAI connection successful!")
    print(response.json()["choices"][0]["message"]["content"])
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
```

### 5. Available Services
- **Chat Models**: gpt-4, gpt-3.5-turbo
- **Embeddings**: text-embedding-3-small/large
- **Speech-to-Text**: whisper-1
- **Text-to-Speech**: tts-1, tts-1-hd

## Google Cloud Setup

### 1. Create Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Create Project"
3. Name your project (e.g., "kaygraph-examples")
4. Note the Project ID

### 2. Enable APIs
```bash
# Using gcloud CLI
gcloud services enable speech.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable calendar.googleapis.com
gcloud services enable translate.googleapis.com

# Or use Console UI
# APIs & Services → Enable APIs → Search and enable
```

### 3. Create Service Account
1. Go to IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: "kaygraph-service"
4. Grant roles:
   - For Speech: "Cloud Speech-to-Text User"
   - For Calendar: "Calendar API User"
5. Create key (JSON format)
6. Download the key file

### 4. Set Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 5. Test Connection
```python
# test_google.py
from google.cloud import speech

client = speech.SpeechClient()
print("✅ Google Cloud connection successful!")
```

## Anthropic (Claude) Setup

### 1. Get Access
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Request access (may have waitlist)
3. Once approved, sign in

### 2. Generate API Key
1. Go to API Keys section
2. Create new key
3. Copy immediately

### 3. Set Environment Variable
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 4. Test Connection
```python
# test_anthropic.py
import os
import requests

api_key = os.environ.get("ANTHROPIC_API_KEY")
response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    },
    json={
        "model": "claude-3-haiku-20240307",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hello"}]
    }
)

if response.status_code == 200:
    print("✅ Anthropic connection successful!")
else:
    print(f"❌ Error: {response.text}")
```

## Groq Setup

### 1. Create Account
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google or email
3. Verify email

### 2. Generate API Key
1. Navigate to API Keys
2. Create new key
3. Copy the key

### 3. Set Environment Variable
```bash
export GROQ_API_KEY="gsk_..."
```

### 4. Available Models
- **llama3-70b-8192**: Llama 3 70B
- **mixtral-8x7b-32768**: Mixtral 8x7B
- **gemma-7b-it**: Google's Gemma 7B

## Serper (Google Search) Setup

### 1. Create Account
1. Go to [serper.dev](https://serper.dev)
2. Sign up with email
3. Free tier: 2,500 searches

### 2. Get API Key
1. Dashboard → API Key
2. Copy the key

### 3. Set Environment Variable
```bash
export SERPER_API_KEY="..."
```

### 4. Test Search
```python
# test_serper.py
import os
import requests

api_key = os.environ.get("SERPER_API_KEY")
response = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": api_key},
    json={"q": "KayGraph framework"}
)

if response.status_code == 200:
    print("✅ Serper connection successful!")
    results = response.json()
    print(f"Found {len(results.get('organic', []))} results")
else:
    print(f"❌ Error: {response.text}")
```

## Voyage AI (Embeddings) Setup

### 1. Create Account
1. Go to [voyageai.com](https://www.voyageai.com)
2. Sign up for API access
3. Free tier: 50M tokens

### 2. Get API Key
1. Dashboard → API Keys
2. Create and copy key

### 3. Set Environment Variable
```bash
export VOYAGE_API_KEY="..."
```

### 4. Available Models
- **voyage-2**: General purpose embeddings
- **voyage-code-2**: Code embeddings
- **voyage-large-2**: High-quality embeddings

## PostgreSQL Setup (Local)

### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Mac with Homebrew
brew install postgresql
brew services start postgresql

# Windows
# Download installer from postgresql.org
```

### 2. Create Database
```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE kaygraph_db;
CREATE USER kaygraph_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE kaygraph_db TO kaygraph_user;
\q
```

### 3. Set Environment Variable
```bash
export DATABASE_URL="postgresql://kaygraph_user:secure_password@localhost:5432/kaygraph_db"
```

### 4. Test Connection
```python
# test_postgres.py
import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute("SELECT version()")
    print("✅ PostgreSQL connection successful!")
    print(cur.fetchone()[0])
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
```

## Environment Management Best Practices

### 1. Use .env Files
```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
ENVIRONMENT=development
```

### 2. Load with python-dotenv
```python
# main.py
from dotenv import load_dotenv
load_dotenv()

# Now os.environ has all your variables
```

### 3. Never Commit Secrets
```bash
# .gitignore
.env
.env.*
*-key.json
secrets/
```

### 4. Use Different Environments
```bash
# .env.development
OPENAI_API_KEY=sk-test-...
DATABASE_URL=postgresql://localhost/dev_db

# .env.production  
OPENAI_API_KEY=sk-prod-...
DATABASE_URL=postgresql://prod-server/prod_db
```

### 5. Validate on Startup
```python
# config.py
import os
import sys

REQUIRED_VARS = [
    "OPENAI_API_KEY",
    "DATABASE_URL",
]

missing = [var for var in REQUIRED_VARS if not os.environ.get(var)]
if missing:
    print(f"ERROR: Missing environment variables: {missing}")
    sys.exit(1)
```

## Cost Management Tips

### 1. Set Usage Limits
- OpenAI: Set monthly usage limits in billing settings
- Google Cloud: Set up budget alerts
- Monitor usage regularly

### 2. Use Cheaper Models for Development
```python
# Development
model = "gpt-3.5-turbo"  # $0.002/1K tokens

# Production
model = "gpt-4" if important else "gpt-3.5-turbo"
```

### 3. Cache Responses
```python
# Simple caching for development
cache = {}

def call_llm_cached(prompt):
    if prompt in cache:
        return cache[prompt]
    
    response = call_llm(prompt)
    cache[prompt] = response
    return response
```

### 4. Batch Operations
```python
# Instead of 100 individual calls
results = [call_api(item) for item in items]

# Make one batch call
results = call_api_batch(items)
```

## Troubleshooting Common Issues

### API Key Not Found
```bash
# Check if set
echo $OPENAI_API_KEY

# Check spelling
env | grep -i api_key

# Source your .env
source .env
```

### Rate Limiting
```python
import time

def call_with_retry(func, *args, max_retries=3):
    for i in range(max_retries):
        try:
            return func(*args)
        except RateLimitError:
            wait_time = 2 ** i
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

### SSL/Certificate Errors
```python
# Temporary fix (NOT for production)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Better: Update certificates
# pip install --upgrade certifi
```

### Timeout Issues
```python
# Increase timeout
response = requests.post(
    url,
    timeout=30,  # 30 seconds
    # ...
)
```

## Service-Specific Documentation

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google Cloud AI Docs](https://cloud.google.com/ai-platform/docs)
- [Anthropic API Docs](https://docs.anthropic.com)
- [Groq API Docs](https://console.groq.com/docs)
- [Serper API Docs](https://serper.dev/docs)
- [Voyage AI Docs](https://docs.voyageai.com)