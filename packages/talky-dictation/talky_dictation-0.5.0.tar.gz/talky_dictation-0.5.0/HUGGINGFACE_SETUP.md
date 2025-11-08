# Hugging Face Setup for Talky

## The Issue

Talky needs to download the Whisper model from Hugging Face on first run. You're seeing this error:

```
401 Client Error: Unauthorized
Invalid credentials in Authorization header
```

This happens when there's an **invalid or expired token** in your environment.

## Quick Fix (Recommended)

**Good News**: The Whisper models are **public and don't require authentication**. You just need to clear any invalid tokens.

### Step 1: Check for Existing Tokens

```bash
# Check environment variables
env | grep HF

# Check for token file
ls -la ~/.huggingface/token
cat ~/.cache/huggingface/token  # Alternative location
```

### Step 2: Clear Invalid Tokens

```bash
# Clear environment variables
unset HF_TOKEN
unset HUGGINGFACE_TOKEN
unset HUGGING_FACE_HUB_TOKEN

# Remove token files (if they exist)
rm -f ~/.huggingface/token
rm -f ~/.cache/huggingface/token

# Clear any conda/shell config
# Check ~/.bashrc, ~/.zshrc for HF_TOKEN exports
```

### Step 3: Test Download

```bash
cd /home/h3r0/code/tmp/talky

# Try downloading the model
python -c "from faster_whisper import WhisperModel; model = WhisperModel('base', device='cpu'); print('✓ Model downloaded!')"
```

If successful, you'll see:
```
Downloading model...
✓ Model downloaded!
```

## Alternative: Set Up Proper Authentication (Optional)

If clearing tokens doesn't work, or you want to authenticate properly:

### Option A: Create a New Token

1. **Go to Hugging Face**:
   - Visit: https://huggingface.co/settings/tokens
   - Create account if needed (free)

2. **Create New Token**:
   - Click "New token"
   - Name: `talky-whisper`
   - Type: **Read** (not Write)
   - Click "Generate"
   - **Copy the token** (starts with `hf_...`)

3. **Set the Token**:

   ```bash
   # Option 1: Using huggingface-cli (recommended)
   pip install huggingface-hub
   huggingface-cli login
   # Paste your token when prompted

   # Option 2: Manual environment variable
   export HF_TOKEN="hf_YourTokenHere"

   # Option 3: Add to shell config (permanent)
   echo 'export HF_TOKEN="hf_YourTokenHere"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Option B: Use huggingface-cli

```bash
# Install CLI
pip install huggingface-hub

# Login interactively
huggingface-cli login

# Follow prompts:
# 1. Paste your token
# 2. Choose to add to git credentials (optional)

# Verify login
huggingface-cli whoami
```

## Verify Setup

After clearing tokens or setting up authentication:

```bash
cd /home/h3r0/code/tmp/talky

# Run Talky test
python tests/test_integration.py

# Or run Talky directly
python -m talky.main
```

## Troubleshooting

### Still Getting 401 Errors?

1. **Check for hidden token files**:
   ```bash
   find ~ -name "*huggingface*" -type f 2>/dev/null
   ```

2. **Check shell config files**:
   ```bash
   grep -r "HF_TOKEN" ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null
   ```

3. **Try with explicit no-token**:
   ```bash
   # Temporarily rename config
   mv ~/.huggingface ~/.huggingface.bak

   # Try again
   python -m talky.main

   # Restore if needed
   mv ~/.huggingface.bak ~/.huggingface
   ```

### Download Stuck or Slow?

The first download takes time (base model is ~140MB):

```bash
# Monitor download progress
watch -n 1 'ls -lh ~/.cache/talky/models/'

# Or check HF cache
ls -lh ~/.cache/huggingface/hub/
```

### Alternative: Manual Download

If automatic download fails, download manually:

1. **Download from Hugging Face**:
   - Go to: https://huggingface.co/Systran/faster-whisper-base
   - Click "Files and versions"
   - Download: `config.json`, `model.bin`, `vocabulary.txt`, `tokenizer.json`

2. **Place in cache**:
   ```bash
   mkdir -p ~/.cache/talky/models/faster-whisper-base
   # Copy downloaded files there
   ```

3. **Test**:
   ```bash
   python -m talky.main
   ```

## Expected Behavior

### First Run
```
Loading Whisper model: base
  Device: cuda
  Compute Type: float16
Downloading model from Hugging Face... (this may take a moment)
✓ Model loaded successfully
```

### Subsequent Runs
```
Loading Whisper model: base
  Device: cuda
  Compute Type: float16
✓ Model loaded successfully (from cache)
```

## Summary

**Most likely solution**: Just clear invalid tokens
```bash
unset HF_TOKEN
unset HUGGINGFACE_TOKEN
rm -f ~/.huggingface/token
python -m talky.main
```

**If that doesn't work**: Set up proper authentication with a new token from https://huggingface.co/settings/tokens

**Model Location**: Models are cached in `~/.cache/talky/models/` for reuse

---

Need more help? The error message will guide you:
- `401 Unauthorized` → Clear/reset token
- `403 Forbidden` → Check token permissions (should be Read)
- `404 Not Found` → Check model name (should be "base", "small", etc.)
- Network errors → Check internet connection
