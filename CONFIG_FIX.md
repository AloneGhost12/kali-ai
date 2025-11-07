# Configuration Fix

## Issue
The API key was not persisting between commands because it was only set as an environment variable.

## Solution
Implemented a `ConfigManager` that saves configuration to a JSON file at `~/.kaliagent/config.json`.

## How to Use

### Configure API Key (Now Persists!)
```bash
kaliagent configure --api-key YOUR_API_KEY
```

### Show Current Configuration
```bash
kaliagent configure --show
```

### Update Model
```bash
kaliagent configure --model gpt-4
kaliagent configure --model gpt-3.5-turbo
```

### Update Safe Mode
```bash
kaliagent configure --no-safe-mode    # Allow command execution
kaliagent configure --safe-mode       # Disable command execution (default)
```

### Update Confirmation Settings
```bash
kaliagent configure --no-confirm     # Don't ask before executing
kaliagent configure --confirm        # Ask before executing (default)
```

## Configuration File Location

Your configuration is stored at:
- **Linux/Mac**: `~/.kaliagent/config.json`
- **Windows**: `C:\Users\USERNAME\.kaliagent\config.json`

## What Gets Saved

```json
{
  "OPENAI_API_KEY": "sk-...",
  "MODEL_ID": "gpt-3.5-turbo",
  "SAFE_MODE": true,
  "REQUIRE_CONFIRMATION": true
}
```

## Testing

1. **Set API Key:**
   ```bash
   kaliagent configure --api-key YOUR_KEY
   ```

2. **Verify it persists:**
   ```bash
   kaliagent configure --show
   ```

3. **Try interactive mode:**
   ```bash
   kaliagent interactive
   ```

The API key should now work across all commands! ✅
