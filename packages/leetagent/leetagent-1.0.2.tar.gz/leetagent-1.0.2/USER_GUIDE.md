# LeetAgent User Guide

Welcome to **LeetAgent** - Your AI-powered LeetCode automation tool! 🚀

## Quick Start

### 1. Installation

```bash
pip install leetagent
```

### 2. Configuration

Run the interactive configuration wizard:

```bash
leetagent config
```

This wizard will guide you through setting up:
- **Gemini API Key** (Required) - For AI-powered code generation
- **Preferred Language** (Required) - Python, Java, C++, C#, JavaScript, etc.
- **Telegram Notifications** (Optional) - Get notified when solutions are submitted

### 3. Authenticate with LeetCode

```bash
leetagent login
```

This opens LeetCode in your browser. Simply log in manually, and LeetAgent will save your session automatically.

### 4. Start Solving!

Solve today's daily challenge:
```bash
leetagent auto
```

Or solve a specific problem:
```bash
leetagent direct https://leetcode.com/problems/two-sum/
```

---

## Configuration Management

### Interactive Wizard (Recommended)

```bash
leetagent config
```

This is the easiest way to configure LeetAgent. It walks you through each setting step-by-step.

### Quick Commands

Set individual values:
```bash
leetagent config-set GEMINI_API_KEY your_api_key_here
leetagent config-set PREFERRED_LANGUAGE Python
leetagent config-set TELEGRAM_TOKEN your_bot_token
leetagent config-set CHAT_ID your_chat_id
```

View your configuration:
```bash
leetagent config-show
```

### Secure Storage (Advanced)

Store credentials in your OS keyring for extra security:
```bash
leetagent secret-set GEMINI_API_KEY
leetagent secret-set TELEGRAM_TOKEN
```

This stores credentials securely using Windows Credential Manager (Windows), Keychain (macOS), or Secret Service (Linux).

---

## Configuration Options

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for AI code generation | `AIzaSy...` |
| `PREFERRED_LANGUAGE` | Programming language for solutions | `Python`, `Java`, `C++`, etc. |

### Optional Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `TELEGRAM_TOKEN` | Telegram bot token for notifications | `123456:ABC...` |
| `CHAT_ID` | Your Telegram chat ID | `987654321` |

### Supported Languages

- Python
- Java
- C++
- C
- C#
- JavaScript
- TypeScript
- Go
- Rust
- Swift
- Kotlin
- Ruby
- PHP
- Scala

---

## Commands Reference

### Configuration Commands

```bash
leetagent config              # Interactive configuration wizard
leetagent setup               # Alias for 'config'
leetagent config-set KEY VAL  # Set a specific configuration value
leetagent config-show         # Display current configuration
leetagent secret-set KEY      # Securely store credential in OS keyring
```

### Authentication Commands

```bash
leetagent login               # Login to LeetCode (saves cookies)
leetagent logout              # Logout (deletes saved cookies)
leetagent session-status      # Check authentication & credential status
```

### Problem Solving Commands

```bash
leetagent auto                        # Solve today's daily challenge
leetagent direct URL                  # Solve specific problem by URL
leetagent direct URL -l Python        # Solve with specific language
leetagent interactive                 # Interactive menu mode
```

### Utility Commands

```bash
leetagent version             # Show version info
leetagent update              # Update to latest version
leetagent --help              # Show help
```

---

## Where are my settings stored?

All configuration is stored in: `~/.leetagent/config.json`

This file contains:
- API keys and tokens
- Preferred language
- Other settings

**Important:** This file contains sensitive information. Do NOT commit it to Git or share it publicly!

If using `secret-set`, credentials are stored in:
- **Windows:** Windows Credential Manager
- **macOS:** Keychain
- **Linux:** Secret Service / Keyring

---

## Getting Your API Keys

### Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and run:
   ```bash
   leetagent config-set GEMINI_API_KEY your_key_here
   ```

### Telegram Bot (Optional)

1. **Create a Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Get Your Chat ID:**
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find your `chat.id` in the response

3. **Configure:**
   ```bash
   leetagent config-set TELEGRAM_TOKEN your_bot_token
   leetagent config-set CHAT_ID your_chat_id
   ```

---

## Troubleshooting

### "GEMINI_API_KEY is required"

Run the configuration wizard:
```bash
leetagent config
```

Or set it directly:
```bash
leetagent config-set GEMINI_API_KEY your_key_here
```

### "No cookies found" or Login Issues

Re-authenticate with LeetCode:
```bash
leetagent logout
leetagent login
```

### Check Your Setup

Run a complete status check:
```bash
leetagent session-status --check-online
```

This will:
- Show all configured credentials
- Test API connectivity
- Check LeetCode authentication
- Display helpful error messages

### View Configuration

See what's configured:
```bash
leetagent config-show
```

---

## Security Best Practices

1. **Never commit config files to Git**
   - Add `~/.leetagent/` to your global `.gitignore`
   - Never share your `config.json` file

2. **Use OS keyring for extra security**
   ```bash
   leetagent secret-set GEMINI_API_KEY
   ```

3. **Rotate API keys regularly**
   - Generate new keys every few months
   - Update using `leetagent config-set` or `secret-set`

4. **Limit API key permissions**
   - Only grant necessary permissions to your API keys
   - Use separate keys for different tools

---

## Example Workflow

Here's a typical daily workflow:

```bash
# First time setup
leetagent config                    # Configure credentials
leetagent login                     # Authenticate with LeetCode

# Daily usage
leetagent auto                      # Solve today's challenge

# Specific problems
leetagent direct https://leetcode.com/problems/two-sum/ -l Python

# Check status
leetagent config-show               # View settings
leetagent session-status            # Check authentication
```

---

## Getting Help

- **General Help:** `leetagent --help`
- **Command Help:** `leetagent <command> --help`
- **View Configuration:** `leetagent config-show`
- **Check Status:** `leetagent session-status`

---

## Pro Tips

1. **Use the wizard:** `leetagent config` is the easiest way to set up
2. **Check before solving:** Run `leetagent session-status` to verify everything is working
3. **Save time:** Set your preferred language once, use it everywhere
4. **Stay notified:** Configure Telegram to get instant notifications
5. **Stay updated:** Run `leetagent update` occasionally

---

Happy coding! 🎯
