# 🚀 LeetAgent - AI-Powered LeetCode Automation

**Automate your LeetCode daily challenges with AI-generated solutions in one command.**

LeetAgent is an intelligent automation tool that fetches, solves, and submits LeetCode problems using Google Gemini AI. Perfect for maintaining your coding streak, practicing different approaches, and learning from AI-generated solutions with detailed explanations.

**Features:** AI-powered solution generation • Browser automation with Selenium • Multi-language support (Python, C#, Java, JavaScript) • Telegram notifications • Interactive CLI with Rich UI • Robust retry logic • Session management

## 🎯 Quick Start

```bash
# Install
pip install leetagent

# Configure (interactive wizard)
leetagent config

# Solve today's daily challenge
leetagent solve

# Login to LeetCode (one-time setup)
leetagent login
```

## 📦 What You Get

- **One-command automation** - `leetagent solve` handles everything
- **AI-powered solutions** - Google Gemini generates optimized code
- **5 submission strategies** - Multiple fallback methods for reliability
- **Smart notifications** - Success/failure alerts via Telegram
- **Beautiful CLI** - Rich terminal UI with progress indicators
- **Session persistence** - Login once, use forever

## 🔑 Requirements

- Python 3.10+
- Google Chrome browser
- [Gemini API key](https://makersuite.google.com/app/apikey) (free)
- [Telegram bot token](https://t.me/BotFather) (optional, for notifications)

## 📖 Documentation

**Full documentation:** [github.com/satyamyadav/leetagent](https://github.com/satyamyadav/leetagent)

- [Complete Setup Guide](https://github.com/satyamyadav/leetagent/blob/main/docs/SETUP.md)
- [Usage Examples](https://github.com/satyamyadav/leetagent/blob/main/docs/USAGE.md)
- [Configuration Reference](https://github.com/satyamyadav/leetagent/blob/main/docs/CONFIG.md)
- [Troubleshooting](https://github.com/satyamyadav/leetagent/blob/main/docs/TROUBLESHOOTING.md)

## 🎨 Usage Examples

```bash
# Solve specific problem
leetagent solve https://leetcode.com/problems/two-sum/

# Use different language
leetagent solve --language python

# Interactive mode with menu
leetagent --interactive

# View configuration
leetagent config-show

# Check status
leetagent status
```

## 🏗️ Architecture

Modular design with clean separation:
- **Core modules**: Scraper, AI generator, formatter, notifier
- **Browser automation**: Selenium with 5 submission strategies
- **AI agents**: Decision agent for approach analysis
- **CLI**: Interactive Typer-based interface

## 🤝 Contributing

Contributions welcome! Visit [GitHub repository](https://github.com/satyamyadav/leetagent) for:
- Source code
- Issue reporting
- Feature requests
- Development guide

## 📄 License

MIT License - see [LICENSE](https://github.com/satyamyadav/leetagent/blob/main/LICENSE) for details.

## 🙏 Credits

Built with: Google Gemini AI • Selenium WebDriver • Rich UI • Typer CLI

---

**⭐ [Star on GitHub](https://github.com/satyamyadav/leetagent) if you find this useful!**
