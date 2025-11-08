# Doppler Integration Documentation

## Overview

This documentation describes the Doppler integration pattern from the FastAPI + React template.
Use this as reference when transferring Doppler integration to a new codebase.

## What is Doppler?

Doppler is a secrets management platform that:
- Centralizes environment variables and secrets
- Provides secure access control
- Supports multiple environments (dev, staging, prod)
- Integrates with CI/CD pipelines
- Offers audit logging and access tracking

## Integration Pattern

### 1. File Structure

```
project/
├── config/
│   └── doppler.ts          # Doppler client initialization
├── .env.example            # Template with Doppler instructions
├── .env.local             # Local development (gitignored)
├── docker-compose.yml      # Docker with Doppler token injection
└── README.md              # Setup instructions
```

### 2. Dependencies

**NPM/Node.js:**
```json
{
  "dependencies": {
    "@dopplerhq/node-sdk": "^1.2.0",
    "dotenv": "^16.0.0"
  }
}
```

**Python (if applicable):**
```txt
doppler-sdk==1.2.0
python-dotenv==1.0.0
```

### 3. Configuration File (config/doppler.ts)

```typescript
import { Doppler } from '@dopplerhq/node-sdk';

/**
 * Initialize Doppler client for secrets management
 */
export class DopplerConfig {
  private doppler: Doppler;
  private secrets: Record<string, string> = {};

  constructor() {
    // Initialize Doppler with token from environment
    const token = process.env.DOPPLER_TOKEN;

    if (!token) {
      console.warn('DOPPLER_TOKEN not found, falling back to .env file');
      this.doppler = null;
      return;
    }

    try {
      this.doppler = new Doppler({
        token: token
      });

      console.log('✓ Doppler client initialized');
    } catch (error) {
      console.error('Failed to initialize Doppler:', error);
      this.doppler = null;
    }
  }

  /**
   * Fetch all secrets from Doppler
   */
  async fetchSecrets(): Promise<Record<string, string>> {
    if (!this.doppler) {
      // Fallback to local .env
      require('dotenv').config();
      return process.env as Record<string, string>;
    }

    try {
      const response = await this.doppler.secrets.list({
        project: process.env.DOPPLER_PROJECT || 'default',
        config: process.env.DOPPLER_CONFIG || 'dev'
      });

      this.secrets = response.secrets;
      return this.secrets;
    } catch (error) {
      console.error('Failed to fetch secrets from Doppler:', error);
      // Fallback to .env
      require('dotenv').config();
      return process.env as Record<string, string>;
    }
  }

  /**
   * Get a specific secret
   */
  async getSecret(key: string): Promise<string | undefined> {
    if (Object.keys(this.secrets).length === 0) {
      await this.fetchSecrets();
    }

    return this.secrets[key] || process.env[key];
  }
}

// Export singleton instance
export const dopplerConfig = new DopplerConfig();
```

### 4. Environment Variables (.env.example)

```bash
# Doppler Configuration
# Get your token from: https://dashboard.doppler.com/workplace/[your-workplace]/projects
DOPPLER_TOKEN=dp.st.xxxxx
DOPPLER_PROJECT=your-project-name
DOPPLER_CONFIG=dev

# Fallback values for local development (if not using Doppler)
DATABASE_URL=postgresql://localhost:5432/myapp
API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

### 5. Docker Integration (docker-compose.yml)

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      # Doppler token injection
      - DOPPLER_TOKEN=${DOPPLER_TOKEN}
      - DOPPLER_PROJECT=${DOPPLER_PROJECT}
      - DOPPLER_CONFIG=${DOPPLER_CONFIG}
    # Alternative: Use Doppler CLI to inject secrets
    # command: doppler run -- npm start
```

### 6. Application Initialization

```typescript
// main.ts or app.ts
import { dopplerConfig } from './config/doppler';

async function initializeApp() {
  // Load secrets from Doppler
  await dopplerConfig.fetchSecrets();

  // Now environment variables are available
  const dbUrl = await dopplerConfig.getSecret('DATABASE_URL');
  const apiKey = await dopplerConfig.getSecret('API_KEY');

  // Initialize your app with secrets
  // ...
}

initializeApp().catch(console.error);
```

## Setup Instructions for New Codebase

### Step 1: Install Dependencies

```bash
npm install @dopplerhq/node-sdk dotenv
# or
yarn add @dopplerhq/node-sdk dotenv
```

### Step 2: Create Doppler Account

1. Sign up at https://doppler.com
2. Create a new project
3. Add your secrets to the project
4. Generate a service token

### Step 3: Configure Locally

```bash
# Install Doppler CLI (optional but recommended)
brew install dopplerhq/tap/doppler  # macOS
# or
curl -Ls https://cli.doppler.com/install.sh | sh

# Login to Doppler
doppler login

# Setup project
doppler setup
```

### Step 4: Add Configuration File

Copy `config/doppler.ts` to your project and adapt to your framework.

### Step 5: Update Application Entry Point

Modify your app's entry point to initialize Doppler before other services.

### Step 6: Update Docker Configuration

Add Doppler token to your Docker compose or Kubernetes configs.

### Step 7: Update CI/CD

Add `DOPPLER_TOKEN` to your CI/CD secrets and inject in build/deploy steps.

## Testing

### Test Doppler Integration

```bash
# Test with Doppler
DOPPLER_TOKEN=your-token npm start

# Test fallback to .env
unset DOPPLER_TOKEN
npm start  # Should use .env file
```

### Verify Secrets Loading

```typescript
// test/doppler.test.ts
import { dopplerConfig } from '../config/doppler';

describe('Doppler Integration', () => {
  it('should load secrets from Doppler', async () => {
    await dopplerConfig.fetchSecrets();
    const secret = await dopplerConfig.getSecret('DATABASE_URL');
    expect(secret).toBeDefined();
  });

  it('should fallback to .env if Doppler unavailable', async () => {
    delete process.env.DOPPLER_TOKEN;
    const secret = await dopplerConfig.getSecret('DATABASE_URL');
    expect(secret).toBeDefined();
  });
});
```

## Error Handling

### Common Issues

**Issue**: "DOPPLER_TOKEN not found"
- **Solution**: Set the token in environment or .env file
- **Fallback**: Uses .env file automatically

**Issue**: "Failed to fetch secrets"
- **Cause**: Invalid token or network error
- **Solution**: Verify token and network connectivity
- **Fallback**: Uses cached secrets or .env file

**Issue**: "Secret not found"
- **Cause**: Secret not added to Doppler project
- **Solution**: Add secret in Doppler dashboard
- **Fallback**: Returns undefined, check .env file

## Security Best Practices

1. **Never commit `.env` files** - Always in .gitignore
2. **Use service tokens** in production, not personal tokens
3. **Rotate tokens** regularly (Doppler supports this)
4. **Limit token scope** to specific projects/configs
5. **Audit access** using Doppler's audit logs
6. **Use different tokens** for each environment

## Migration Strategy

### From .env to Doppler

1. **Copy existing secrets** to Doppler dashboard
2. **Test with Doppler** in development first
3. **Update CI/CD** with Doppler tokens
4. **Deploy to staging** and verify
5. **Deploy to production** with monitoring
6. **Keep .env as fallback** initially
7. **Remove .env** once confident in Doppler

## Additional Resources

- Doppler Docs: https://docs.doppler.com
- Node SDK: https://github.com/DopplerHQ/node-sdk
- Dashboard: https://dashboard.doppler.com
- Support: https://doppler.com/support

---

## Transfer Notes

When transferring this pattern to a new codebase:

1. **Adapt to framework**: Modify doppler.ts for your framework (Express, NestJS, FastAPI, Django, etc.)
2. **Follow conventions**: Use target codebase's config patterns
3. **Preserve fallback**: Always keep .env fallback working
4. **Update docs**: Add Doppler setup to target project's README
5. **Test thoroughly**: Verify both Doppler and fallback modes work

**Key Principle**: Integration should be **transparent** to the rest of the application - existing code using process.env should continue working.
