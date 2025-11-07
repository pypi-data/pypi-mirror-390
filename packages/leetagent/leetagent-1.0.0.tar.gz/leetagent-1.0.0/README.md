# 🚀 LeetCode Agent Automation

**Enterprise-grade automated LeetCode problem solver powered by Google Gemini AI**

Automates the complete workflow of fetching, solving, and submitting LeetCode problems with AI-generated solutions, multi-recipient notifications, and browser automation. **Just run one command to solve today's daily challenge!**

## ✨ Features

- 🤖 **AI-Powered Solutions**: Google Gemini API integration with retry logic
- ⚡ **Auto Daily Challenge**: Automatically fetches and solves today's problem
- 🌐 **Full Browser Automation**: Selenium WebDriver with 5 submission strategies
- 🎯 **Intelligent Problem Analysis**: Decision agent for approach recommendation
- 📱 **Multi-Recipient Notifications**: Telegram bot broadcasts to multiple chats
- 🎨 **Beautiful CLI**: Rich library for optional interactive mode
- 🔄 **Retry Logic**: Robust error handling with automatic retries
- 📦 **Modular Architecture**: Clean separation of concerns for maintainability
- 🔮 **AI Agent Ready**: Prepared for LangChain integration

## 📋 Prerequisites

- Python 3.9 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by `webdriver-manager`)
- Google Gemini API key
- Telegram bot token (for notifications)

## ⚡ Quick Start (3 Steps!)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment** (create `.env` file)
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   CHAT_ID1=your_first_chat_id
   CHAT_ID2=your_second_chat_id
   ```

3. **Run the script!**
   ```bash
   python main.py    # Automatically solves today's daily challenge!
   ```

**That's it!** The script will:
- ✅ Fetch today's LeetCode daily challenge
- ✅ Open Chrome and authenticate
- ✅ Generate solution with Gemini AI
- ✅ Run tests and submit automatically
- ✅ Send success notification to Telegram

For detailed setup, see [QUICKSTART.md](QUICKSTART.md).

## 🛠️ Full Installation

1. **Clone the repository**
   ```bash
   cd LeetcodeAgentAutomation
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory (use `.env.example` as template):
   ```env
   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL_NAME=gemini-2.0-flash-exp
   
   # Telegram Bot
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   CHAT_ID1=your_first_chat_id
   CHAT_ID2=your_second_chat_id
   
   # LeetCode
   LEETCODE_COOKIES_PATH=./leetcode_cookies.json
   
   # Settings
   MAX_AI_ATTEMPTS=3
   LOG_LEVEL=INFO
   ```

## 🚀 Usage

### **Login First (Required)**

Before running any automation, you need to log in to LeetCode and save cookies:

```bash
python main.py login
```

This will:
- 🔐 Open LeetCode login page in Chrome
- ⏳ Wait for you to manually log in (30 seconds)
- 💾 Automatically extract and save cookies
- ✅ Show confirmation with save location

**You only need to do this once!** Cookies will be saved in `data/cookies.json` and reused for all future runs.

---

### **Auto Mode (Default - Recommended)**

**Automatically fetches and solves today's LeetCode daily challenge with browser automation!**

```bash
python main.py
```

This is the **fastest way to maintain your streak**:
- ✅ Fetches today's daily challenge
- ✅ Opens Chrome browser automatically  
- ✅ Generates solution with AI
- ✅ Runs tests and submits
- ✅ Sends notifications to Telegram
- ✅ **Just like the original script - no menu needed!**

---

### **Interactive Mode**

Shows beautiful CLI menu with testing options:

```bash
python main.py --interactive
# or
python main.py -i
```

Features interactive menu with options to:
- 🔐 Login to LeetCode (save cookies)
- 🚀 Auto-solve problems from URL
- 🔍 Fetch problem details
- 🧪 Test AI generator
- 📊 View configuration
- 🔔 Test notifications

---

### **Direct Mode**

Solve specific problem directly:

```bash
python main.py https://leetcode.com/problems/two-sum/ C#
```

Arguments:
- `problem_url`: LeetCode problem URL (required)
- `language`: Programming language (optional, default: C#)

Supported languages: C#, Python, Java, JavaScript

**See [docs/USAGE.md](docs/USAGE.md) for detailed usage guide with examples.**

## 📁 Project Structure

```
LeetcodeAgentAutomation/
├── main.py                    # Entry point
├── config.py                  # Configuration management
├── requirements.txt           # Dependencies
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Environment template
├── README.md                 # Documentation
│
├── core/                     # Core utilities
│   ├── __init__.py
│   ├── logger.py            # Centralized logging
│   └── utils.py             # Helper functions
│
├── modules/                  # Functional modules
│   ├── __init__.py
│   ├── scraper.py           # LeetCode GraphQL scraper
│   ├── ai_generator.py      # Gemini solution generator
│   ├── formatter.py         # Code formatting
│   ├── notifier.py          # Telegram notifications
│   └── auth.py              # Cookie management
│
├── agents/                   # AI agents (future LangChain)
│   ├── __init__.py
│   └── decision_agent.py    # Problem analysis agent
│
├── cli/                      # Command-line interface
│   ├── __init__.py
│   └── main_cli.py          # Rich CLI components
│
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_gemini_client.py
│
├── logs/                     # Log files (auto-created)
├── solutions/                # Saved solutions (auto-created)
└── cookies/                  # LeetCode cookies (auto-created)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `GEMINI_MODEL_NAME` | Gemini model to use | No | gemini-2.0-flash-exp |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes | - |
| `CHAT_ID1` | Primary Telegram chat ID | Yes | - |
| `CHAT_ID2` | Secondary Telegram chat ID | No | - |
| `MAX_AI_ATTEMPTS` | Max retry attempts for AI generation | No | 3 |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | No | INFO |

### Getting API Keys

**Google Gemini API:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy to `.env` file

**Telegram Bot:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy bot token to `.env`
4. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

## 📊 Modules Overview

### Core Module (`core/`)
- **logger.py**: Colored console output + file logging with rotation
- **utils.py**: File operations, string formatting, code extraction

### Modules (`modules/`)
- **scraper.py**: GraphQL queries to fetch problem metadata
- **ai_generator.py**: Gemini AI integration with retry logic
- **formatter.py**: Code cleaning, validation, formatting
- **notifier.py**: Telegram multi-recipient broadcasting
- **auth.py**: Cookie persistence and session management

### Agents (`agents/`)
- **decision_agent.py**: Problem analysis and approach recommendation
  - Future: LangChain integration for intelligent decision-making
  - Future: Vector store for similar problem retrieval
  - Future: RAG for learning from past solutions

### CLI (`cli/`)
- **main_cli.py**: Rich library interface with:
  - ASCII art welcome screen
  - Interactive menus
  - Progress spinners
  - Syntax-highlighted code preview
  - Formatted tables

## 🧪 Testing

Run test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_gemini_client.py

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 📝 Logging

Logs are automatically saved to `logs/` directory with daily rotation:
- **Console**: Colored output with timestamps
- **File**: `logs/leetcode_YYYYMMDD.log` with full details

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🔮 Future Enhancements

### Planned Features
- [ ] LangChain integration for intelligent agents
- [ ] Vector database for problem similarity search
- [ ] RAG system for learning from past solutions
- [ ] Multi-language support expansion
- [ ] Web dashboard for monitoring
- [ ] Database for submission history
- [ ] Performance metrics and analytics
- [ ] Automated testing against LeetCode test cases
- [ ] Contest mode automation

### AI Agent Roadmap
The project is structured to support future AI agent capabilities:
- **Decision Agent**: Analyze problems and recommend optimal approaches
- **Learning Agent**: Learn from submission feedback
- **Strategy Agent**: Optimize solution strategies over time
- **Memory Agent**: Store and retrieve similar problem patterns

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'rich'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `GEMINI_API_KEY not found`
- **Solution**: Create `.env` file with your API key

**Issue**: ChromeDriver errors
- **Solution**: Update Chrome browser or run: `pip install --upgrade webdriver-manager`

**Issue**: Telegram notifications not sending
- **Solution**: Verify bot token and chat IDs in `.env`

**Issue**: "Failed to fetch problem"
- **Solution**: Check internet connection and LeetCode URL format

## 📄 License

This project is provided as-is for educational purposes.

## 👤 Author

**Sirahmad Rasheed**
- Project: LeetCode Agent Automation
- Version: 1.0.0

## 🤝 Contributing

Contributions welcome! Areas for contribution:
- Selenium submission integration
- Additional language support
- Test coverage improvement
- LangChain agent implementation
- Performance optimizations

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review logs in `logs/` directory
3. Test individual components (menu options 3-5)
4. Check environment variable configuration

## 🙏 Acknowledgments

- Google Gemini API for AI-powered solutions
- Selenium for web automation
- Rich library for beautiful CLI
- LeetCode for providing the platform

---

**⭐ Star this project if you find it useful!**
