"""
LeetCode problem scraper module
fetches the daily problem metadata and descriptions via GraphQL API
"""

import json
import requests
from typing import Optional, Dict, Any

from core.logger import logger
from config import settings
from utils.text_helpers import (
    html_to_text
)


class LeetCodeScraper:
    """Handles fetching problem data from LeetCode"""
    
    def __init__(self):
        self.graphql_url = settings.LEETCODE_GRAPHQL_URL
        self.base_url = settings.LEETCODE_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_problem_metadata(self) -> Optional[dict]:
        query = {
            "query": """
            query questionOfToday {
                activeDailyCodingChallengeQuestion {
                    date
                    link
                    question {
                        title
                        titleSlug
                        content
                        sampleTestCase
                        exampleTestcases
                        codeSnippets {
                            lang
                            code
                        }
                    }
                }
            }
            """
        }

        try:
            logger.info("Fetching today's daily challenge...")

            response = self.session.post(
                self.graphql_url, 
                json=query, 
                timeout=20
            )

            if response.status_code != 200:
                logger.error(f"GraphQL request failed: {response.status_code}")
                return None

            data = response.json()["data"]["activeDailyCodingChallengeQuestion"]

            if not data:
                logger.error("No daily challenge data found")
                return None

            question = data["question"]
            
            csharp_template = next(
                (snippet["code"] for snippet in question.get("codeSnippets", []) if snippet.get("lang", "").lower() == "c#"),
                "",
            )

            metadata = {
                "title": question.get("title"),
                "titleSlug": question.get("titleSlug"),
                "slug": question.get("titleSlug"),
                "link": f"{self.base_url}{data.get('link', '')}",
                "code_template": csharp_template,
                "content": html_to_text(question.get("content") or ""),
                "examples": question.get("exampleTestcases") or "",
                "questionFrontendId": question.get("questionFrontendId", "Unknown")
            }

            logger.info(f"Successfully fetched daily challenge: {metadata['title']}")
            logger.info(f"Daily challenge Link: {metadata['link']}")

            print(f"📅 Today's problem: {metadata['title']}")
            print(f"🔗 Link: {metadata['link']}")
            return metadata

        except Exception as exc:
            logger.error(f"Failed to fetch daily problem: {exc}")
            return None
    
    def fetch_problem_by_url(self, problem_url: str) -> Optional[dict]:
        """
        Fetch problem metadata by URL
        
        Args:
            problem_url: Full LeetCode problem URL or just the slug
            
        Returns:
            Problem metadata dictionary or None if failed
        """
        try:
            # Extract slug from URL
            # Handle formats:
            # - https://leetcode.com/problems/two-sum/
            # - https://leetcode.com/problems/two-sum/description/
            # - two-sum
            
            if "leetcode.com" in problem_url:
                parts = problem_url.split("/problems/")
                if len(parts) > 1:
                    slug = parts[1].rstrip("/").split("/")[0]
                else:
                    logger.error(f"Invalid LeetCode URL format: {problem_url}")
                    return None
            else:
                slug = problem_url.strip("/")
            
            logger.info(f"Fetching problem by slug: {slug}")
            
            query = {
                "query": """
                query getQuestionDetail($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        questionId
                        questionFrontendId
                        title
                        titleSlug
                        content
                        difficulty
                        likes
                        dislikes
                        topicTags {
                            name
                            slug
                        }
                        codeSnippets {
                            lang
                            langSlug
                            code
                        }
                        sampleTestCase
                        exampleTestcases
                    }
                }
                """,
                "variables": {
                    "titleSlug": slug
                }
            }
            
            response = self.session.post(
                self.graphql_url,
                json=query,
                timeout=20
            )
            
            if response.status_code != 200:
                logger.error(f"GraphQL request failed: {response.status_code}")
                return None
            
            result = response.json()
            
            if "errors" in result:
                logger.error(f"GraphQL errors: {result['errors']}")
                return None
            
            question = result.get("data", {}).get("question")
            
            if not question:
                logger.error(f"No problem found for slug: {slug}")
                return None
            
            # Extract C# code template
            csharp_template = next(
                (snippet["code"] for snippet in question.get("codeSnippets", []) 
                 if snippet.get("lang", "").lower() == "c#"),
                "",
            )
            
            # Get topic tags
            topics = [tag["name"] for tag in question.get("topicTags", [])]
            
            metadata = {
                "questionId": question.get("questionId"),
                "questionFrontendId": question.get("questionFrontendId"),
                "title": question.get("title"),
                "titleSlug": question.get("titleSlug"),
                "slug": question.get("titleSlug"),
                "link": f"{self.base_url}/problems/{slug}/",
                "difficulty": question.get("difficulty"),
                "content": html_to_text(question.get("content") or ""),
                "code_template": csharp_template,
                "examples": question.get("exampleTestcases") or question.get("sampleTestCase") or "",
                "topics": topics,
                "likes": question.get("likes"),
                "dislikes": question.get("dislikes")
            }
            
            logger.info(f"Successfully fetched problem: {metadata['title']} (#{metadata['questionFrontendId']})")
            logger.info(f"Difficulty: {metadata['difficulty']}")
            logger.info(f"Topics: {', '.join(topics)}")
            
            return metadata
            
        except Exception as exc:
            logger.error(f"Failed to fetch problem by URL: {exc}")
            import traceback
            traceback.print_exc()
            return None
