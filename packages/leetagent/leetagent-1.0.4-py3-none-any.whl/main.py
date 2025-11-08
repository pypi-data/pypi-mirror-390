"""
Main entry point for LeetCode Agent Automation
Orchestrates the complete automation workflow
"""

import sys
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import logger
from core.utils import sanitize_filename, format_duration
from config import settings

from modules import (
    LeetCodeScraper,
    GeminiSolutionGenerator,
    CodeFormatter,
    TelegramNotifier,
    LeetCodeAuth
)

from agents.decision_agent import DecisionAgent

try:
    from cli import (
        display_welcome,
        display_auto_welcome,
        display_menu,
        display_config,
        display_problem_info,
        display_progress,
        display_success,
        display_error,
        display_warning,
        prompt_problem_url,
        prompt_language,
        confirm_action,
        display_code_preview,
        display_submission_result,
        create_spinner_context,
        clear_screen,
        pause
    )
    CLI_AVAILABLE = True
except ImportError:
    logger.warning("Rich library not installed. Running in basic mode.")
    CLI_AVAILABLE = False


class LeetCodeAutomation:
    """Main automation orchestrator"""
    
    def __init__(self):
        logger.info("Initializing LeetCode Automation")
        
        # Initialize components
        self.scraper = LeetCodeScraper()
        self.ai_generator = GeminiSolutionGenerator()
        self.formatter = CodeFormatter(language="C#")
        self.notifier = TelegramNotifier()
        self.auth = LeetCodeAuth()
        self.decision_agent = DecisionAgent()
        
        # Configuration
        self.max_attempts = settings.MAX_AI_ATTEMPTS
        self.wait_time = settings.WAIT_TIME
        self.keep_browser_open = settings.KEEP_BROWSER_OPEN
        
        # State tracking
        self.notification_log = []
        self.feedback = []
        
        logger.info("All components initialized")
    
    def log_notification(self, message: str):
        """Add message to the notification log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.notification_log.append(f"[{timestamp}] {message}")
        logger.info(f"📝 {message}")
    
    def send_final_notification(self):
        """Send a single comprehensive notification with all logs"""
        from datetime import datetime
        
        if not self.notifier.bot_token or not self.notifier.chat_ids:
            logger.warning("Telegram credentials not configured. Skipping notification.")
            return
        
        date_str = datetime.now().strftime("%B %d, %Y")
        
        header = f"""{'='*30}
🤖 LeetCode Automation Report
{'='*30}
📅 Date: {date_str}

"""
        
        logs = "\n".join(self.notification_log) if self.notification_log else "No logs recorded."
        footer = f"\n\n{'='*30}"
        full_message = header + logs + footer
        
        self.notifier.broadcast_message(full_message)
        logger.info("✅ Final notification sent to Telegram!")
    
    def run_full_automation_with_selenium(self, problem_url: str, language: str = "C#") -> bool:
        """
        Complete automation workflow using Selenium
        Based on the working Self.py script
        """
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
        from webdriver_manager.chrome import ChromeDriverManager
        
        self.log_notification("🚀 Starting automation workflow")
        driver = None
        
        try:
            # Initialize WebDriver
            logger.info("Starting Chrome WebDriver...")
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Load LeetCode and apply cookies
            logger.info("Loading LeetCode...")
            driver.get(settings.LEETCODE_BASE_URL)
            time.sleep(self.wait_time)
            
            # Load and apply cookies if available
            cookies = self.auth.load_cookies()
            if cookies:
                try:
                    self.auth.apply_cookies_to_driver(driver, cookies)
                    logger.info("✅ Logged in using saved cookies")
                    self.log_notification("✅ Cookies loaded successfully")
                    driver.refresh()
                    time.sleep(self.wait_time)
                except Exception as e:
                    error_msg = f"❌ Cookie authentication failed: {str(e)}"
                    logger.error(error_msg)
                    self.log_notification(error_msg)
                    self.send_final_notification()
                    return False
            else:
                error_msg = "⚠️ No cookies found! Please login to LeetCode and save cookies first."
                logger.error(error_msg)
                self.log_notification(error_msg)
                self.send_final_notification()
                return False
            
            # Fetch problem metadata
            logger.info(f"Fetching problem metadata for: {problem_url}")
            problem = self.scraper.get_problem_metadata()
            
            if not problem:
                logger.error("Failed to fetch problem metadata")
                self.log_notification("❌ Failed to fetch problem metadata")
                return False
            
            self.log_notification(f"📝 Problem: {problem.get('title')}")
            
            # Open problem page
            logger.info(f"Opening problem page: {problem_url}")
            driver.get(problem_url)
            time.sleep(self.wait_time)
            
            # Select language
            if not self._select_language_selenium(driver, language):
                logger.error("Failed to select language")
                self.log_notification("❌ Failed to select language")
                return False
            
            self.log_notification(f"✅ Language selected: {language}")
            
            # Generate and test solutions
            final_solution = None
            
            for attempt in range(1, self.max_attempts + 1):
                logger.info(f"🤖 Generating solution (attempt {attempt}/{self.max_attempts})...")
                
                # Combine feedback list into a single string
                feedback_str = "\n".join(self.feedback) if self.feedback else None
                
                candidate = self.ai_generator.generate_solution(
                    problem=problem,
                    language=language,
                    feedback=feedback_str,
                    attempt_num=attempt
                )
                
                if not candidate:
                    self.feedback.append(f"Attempt {attempt}: Failed to generate solution")
                    continue
                
                # Paste code
                if not self._paste_code_selenium(driver, candidate):
                    self.feedback.append(f"Attempt {attempt}: Failed to paste code")
                    continue
                
                # Run sample tests
                samples_ok, status_text = self._run_sample_tests_selenium(driver)
                
                if samples_ok:
                    final_solution = candidate
                    self.log_notification(f"✅ Solution passed sample tests (attempt {attempt})")
                    logger.info(f"✅ Solution passed on attempt {attempt}")
                    break
                else:
                    self.feedback.append(f"Attempt {attempt}: Sample tests failed - {status_text}")
                    logger.warning(f"⚠️ Attempt {attempt} failed: {status_text}")
                    self.log_notification(f"⚠️ Attempt {attempt} failed: {status_text}")
            
            # Try community solution if AI failed
            if not final_solution:
                logger.info("🔄 Trying community solution fallback...")
                self.log_notification("🔄 Trying community solution fallback")
                
                scraped = self._scrape_community_solution(problem)
                if scraped:
                    self._paste_code_selenium(driver, scraped)
                    samples_ok, status_text = self._run_sample_tests_selenium(driver)
                    
                    if samples_ok:
                        final_solution = scraped
                        self.log_notification("✅ Community solution passed tests")
                    else:
                        self.log_notification(f"❌ Community solution failed: {status_text}")
            
            # Submit solution
            if final_solution:
                logger.info("🚀 Submitting solution...")
                if self._submit_solution_selenium(driver, problem):
                    self.log_notification("🎉 Submission successful!")
                    logger.info("✅ Automation completed successfully")
                    return True
                else:
                    self.log_notification("❌ Submission failed")
                    return False
            else:
                logger.error("❌ No passing solution found")
                self.log_notification("❌ No passing solution found")
                return False
                
        except Exception as e:
            logger.error(f"Fatal error in automation: {e}", exc_info=True)
            self.log_notification(f"❌ Critical error: {str(e)}")
            return False
            
        finally:
            if driver:
                logger.info(f"Keeping browser open for {self.keep_browser_open} seconds...")
                time.sleep(self.keep_browser_open)
                driver.quit()
            
            self.send_final_notification()
    
    def _select_language_selenium(self, driver, target_language: str = "C#") -> bool:
        """Select programming language in LeetCode editor"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(driver, 30)
        max_retries = 3
        
        for retry in range(1, max_retries + 1):
            try:
                logger.info(f"Selecting language: {target_language} (attempt {retry}/{max_retries})...")
                time.sleep(5)
                
                # Find language button
                language_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'rounded') and contains(., 'C++') or contains(., 'Python') or contains(., 'Java') or contains(., 'C#')]")
                    )
                )
                
                driver.execute_script("arguments[0].click();", language_button)
                logger.info("Clicked language button")
                time.sleep(3)
                
                # Wait for popup
                popup = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[role='dialog'][data-state='open']"))
                )
                
                # Select target language
                option = popup.find_element(By.XPATH, f".//div[normalize-space(text())='{target_language}']")
                driver.execute_script("arguments[0].click();", option)
                logger.info(f"✅ Selected {target_language}")
                time.sleep(3)
                return True
                
            except Exception as e:
                if retry < max_retries:
                    logger.warning(f"Retry {retry}/{max_retries}: {e}")
                    time.sleep(self.wait_time)
                else:
                    logger.error(f"Failed to select language: {e}")
                    return False
        
        return False
    
    def _paste_code_selenium(self, driver, code: str) -> bool:
        """Paste code into Monaco editor"""
        import json
        
        try:
            safe_code = json.dumps(code)
            js_code = f"""
            const editor = window.monaco?.editor?.getModels?.()[0];
            if (editor) {{
                editor.pushEditOperations([], [{{
                    range: editor.getFullModelRange(),
                    text: {safe_code}
                }}], () => null);
            }} else {{
                const textarea = document.querySelector('.monaco-editor textarea');
                if (textarea) {{
                    textarea.focus();
                    textarea.value = {safe_code};
                    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }}
            """
            driver.execute_script(js_code)
            time.sleep(2)
            logger.info("✅ Code pasted in editor")
            return True
        except Exception as e:
            logger.error(f"Failed to paste code: {e}")
            return False
    
    def _run_sample_tests_selenium(self, driver) -> tuple:
        """Run sample tests and return (success, status_text)"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import ElementClickInterceptedException
        
        wait = WebDriverWait(driver, 60)
        
        try:
            logger.info("▶️ Running sample tests...")
            run_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e-locator='console-run-button']"))
            )
            
            try:
                run_button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", run_button)
            
            # Wait for result
            result = wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//*[contains(text(), 'Accepted')] | "
                    "//*[contains(text(), 'Wrong Answer')] | "
                    "//*[contains(text(), 'Time Limit Exceeded')] | "
                    "//*[contains(text(), 'Runtime Error')] | "
                    "//*[contains(text(), 'Compile Error')]"
                ))
            )
            
            status_text = (result.text or "").strip()
            logger.info(f"🧪 Sample test result: {status_text}")
            
            if "Accepted" in status_text:
                return True, status_text
            return False, status_text
            
        except Exception as e:
            logger.error(f"Failed to run sample tests: {e}")
            return False, str(e)
    
    def _submit_solution_selenium(self, driver, problem: dict) -> bool:
        """Submit the solution"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        
        wait = WebDriverWait(driver, 90)
        max_retries = 3
        
        for retry in range(1, max_retries + 1):
            try:
                logger.info(f"🚀 Submitting solution (attempt {retry}/{max_retries})...")
                
                button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e-locator='console-submit-button']"))
                )
                
                # Remove disabled attributes
                driver.execute_script("""
                    arguments[0].removeAttribute('disabled');
                    arguments[0].removeAttribute('aria-disabled');
                """, button)
                
                time.sleep(1)
                driver.execute_script("arguments[0].click();", button)
                logger.info("✅ Submit button clicked")
                
                # Wait for submission result
                result = wait.until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'Accepted')] | "
                        "//*[contains(text(), 'Wrong Answer')] | "
                        "//*[contains(text(), 'Time Limit Exceeded')] | "
                        "//*[contains(text(), 'Runtime Error')] | "
                        "//*[contains(text(), 'Memory Limit Exceeded')]"
                    ))
                )
                
                status_text = result.text
                logger.info(f"🎉 Submission result: {status_text}")
                self.log_notification(f"🎉 Submission Result: {status_text}")
                
                if "Accepted" in status_text:
                    self.log_notification("🏆 LeetCode streak maintained!")
                    return True
                else:
                    self.log_notification(f"❌ Submission not accepted: {status_text}")
                    return False
                    
            except TimeoutException:
                if retry < max_retries:
                    logger.warning(f"Submit timeout, retrying...")
                    time.sleep(self.wait_time)
                else:
                    logger.error("Submit button timeout after all retries")
                    return False
            except Exception as e:
                logger.error(f"Submit error: {e}")
                if retry >= max_retries:
                    return False
                time.sleep(self.wait_time)
        
        return False
    
    def _scrape_community_solution(self, problem: dict) -> Optional[str]:
        """Scrape a C# solution from community solutions"""
        import re
        import html
        import requests
        
        slug = problem.get('slug') or problem.get('titleSlug')
        if not slug:
            return None
        
        logger.info("Attempting to scrape community solution...")
        
        try:
            # Load cookies for authenticated scraping
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://leetcode.com",
                "Content-Type": "application/json",
            })
            
            query = {
                "query": """
                query questionSolutionArticles($questionSlug: String!, $skip: Int!, $first: Int!) {
                    questionSolutionArticles(questionSlug: $questionSlug, skip: $skip, first: $first) {
                        edges {
                            node {
                                title
                                content
                            }
                        }
                    }
                }
                """,
                "variables": {"questionSlug": slug, "skip": 0, "first": 20},
            }
            
            response = session.post("https://leetcode.com/graphql", json=query, timeout=20)
            response.raise_for_status()
            edges = response.json().get("data", {}).get("questionSolutionArticles", {}).get("edges", [])
            
            # Look for C# code in solutions
            C_SHARP_CODE_RE = re.compile(
                r'<code[^>]*class="[^"]*language-csharp[^"]*"[^>]*>(.*?)</code>',
                re.IGNORECASE | re.DOTALL
            )
            
            for edge in edges:
                node = edge.get("node") or {}
                content = node.get("content") or ""
                match = C_SHARP_CODE_RE.search(content)
                
                if match:
                    code_html = match.group(1)
                    code = html.unescape(code_html)
                    cleaned = self.formatter.format_code(code)
                    
                    if cleaned and "class Solution" in cleaned:
                        logger.info(f"📥 Found community solution: {node.get('title')}")
                        return cleaned
            
            logger.warning("No C# community solution found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to scrape community solution: {e}")
            return None


def main_interactive():
    """Interactive CLI mode"""
    
    if not CLI_AVAILABLE:
        print("Error: Rich library not installed. Install with: pip install rich")
        return
    
    from cli.main_cli import login_command
    
    clear_screen()
    display_welcome()
    
    automation = LeetCodeAutomation()
    
    while True:
        display_menu()
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            # Login to LeetCode
            clear_screen()
            login_command()
            pause()
            clear_screen()
            
        elif choice == "2":
            # Auto-solve problem
            url = prompt_problem_url()
            language = prompt_language()
            
            clear_screen()
            display_progress("Starting automation...")
            
            success = automation.run_full_automation_with_selenium(url, language)
            
            pause()
            clear_screen()
            
        elif choice == "3":
            # Fetch problem details
            url = prompt_problem_url()
            problem = automation.scraper.fetch_problem_by_url(url)
            
            if problem:
                display_problem_info(problem)
            else:
                display_error("Failed to fetch problem")
            
            pause()
            clear_screen()
            
        elif choice == "4":
            # Test AI generator
            display_progress("Testing Gemini connection...")
            
            try:
                automation.ai_generator._initialize_model()
                display_success("Gemini API connected successfully")
            except Exception as e:
                display_error(f"Gemini test failed: {e}")
            
            pause()
            clear_screen()
            
        elif choice == "5":
            # View config
            display_config()
            pause()
            clear_screen()
            
        elif choice == "6":
            # Test notifications
            display_progress("Testing Telegram notifications...")
            
            if automation.notifier.test_connection():
                display_success("Telegram bot connected")
                
                if confirm_action("Send test message to all chats?"):
                    count = automation.notifier.broadcast_message("🧪 Test message from LeetCode Agent")
                    display_success(f"Test message sent to {count} chat(s)")
            else:
                display_error("Telegram connection failed")
            
            pause()
            clear_screen()
            
        elif choice == "7":
            # Exit
            display_success("Goodbye! 👋")
            break
        
        else:
            display_error("Invalid choice. Please select 1-7.")
            time.sleep(1)
            clear_screen()


def main_direct(problem_url: str, language: str = "C#"):
    """Direct execution mode (no CLI)"""
    
    logger.info("Running in direct mode")
    
    automation = LeetCodeAutomation()
    success = automation.run_full_automation_with_selenium(problem_url, language)
    
    if success:
        logger.info("Automation completed successfully")
        return 0
    else:
        logger.error("Automation failed")
        return 1


def main_auto() -> int:
    """
    Automatic mode - directly start automation like the original Self.py script
    Fetches today's LeetCode daily challenge and automates the complete workflow
    """
    logger.info("===>>> LeetCode Automation Started - Auto Mode")
    
    # Show full welcome banner
    if CLI_AVAILABLE:
        display_welcome()
    else:
        print("LeetCode Agent Automation")
        print("Starting automatic daily challenge solver...")
        
    try:
        # Initialize automation
        automation = LeetCodeAutomation()
        
        # Fetch today's daily challenge
        logger.info("Fetching today's LeetCode daily challenge...")
        problem = automation.scraper.get_problem_metadata()
        
        if not problem:
            logger.error("Failed to fetch daily challenge")
            return 1
        
        problem_url = f"{settings.LEETCODE_BASE_URL}/problems/{problem['titleSlug']}/"
        logger.info(f"Today's problem: {problem['title']}")
        logger.info(f"Problem URL: {problem_url}")
        
        # Run full automation with Selenium
        success = automation.run_full_automation_with_selenium(problem_url, "C#")
        
        if success:
            logger.info("✅ Automation completed successfully")
            return 0
        else:
            logger.error("❌ Automation failed")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error in auto mode: {e}")
        return 1


if __name__ == "__main__":
    try:
        # Validate configuration
        settings.validate()
        
        # Check command-line arguments
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            
            # Check for login command
            if arg in ['login', '--login', '-l']:
                if CLI_AVAILABLE:
                    from cli.main_cli import login_command
                    login_command()
                else:
                    print("Rich library not installed. Install with: pip install rich")
                    sys.exit(1)
            
            # Check if user wants interactive mode
            elif arg in ['--interactive', '-i', 'interactive', 'menu']:
                if CLI_AVAILABLE:
                    main_interactive()
                else:
                    print("Rich library not installed. Install with: pip install rich")
                    sys.exit(1)
            
            # Check if user provided a URL
            elif arg.startswith('http'):
                problem_url = sys.argv[1]
                language = sys.argv[2] if len(sys.argv) > 2 else "C#"
                exit_code = main_direct(problem_url, language)
                sys.exit(exit_code)
            
            else:
                print("Usage:")
                print("  python main.py                    # Auto mode (fetch & solve daily challenge)")
                print("  python main.py login              # Login and save cookies")
                print("  python main.py --interactive      # Interactive menu")
                print("  python main.py <url> [language]   # Solve specific problem")
                sys.exit(1)
        else:
            # Default: Auto mode - directly start automation
            exit_code = main_auto()
            sys.exit(exit_code)
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nFatal error: {e}")
        sys.exit(1)


def cli_app():
    """Entry point for Typer CLI (used by setup.py)"""
    from cli.main_cli import app
    app()
