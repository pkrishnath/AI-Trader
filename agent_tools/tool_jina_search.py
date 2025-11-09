import logging
import os
import random
import re
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.general_tools import get_config_value

load_dotenv()
logger = logging.getLogger(__name__)


def parse_date_to_standard(date_str: str) -> str:  # noqa: C901
    """
    Convert various date formats to standard format (YYYY-MM-DD HH:MM:SS)
    """
    if not date_str or date_str == "unknown":
        return "unknown"

    if "ago" in date_str.lower():
        try:
            now = datetime.now()
            if "hour" in date_str.lower():
                hours = int(re.findall(r"\d+", date_str)[0])
                target_date = now - timedelta(hours=hours)
            elif "day" in date_str.lower():
                days = int(re.findall(r"\d+", date_str)[0])
                target_date = now - timedelta(days=days)
            elif "week" in date_str.lower():
                weeks = int(re.findall(r"\d+", date_str)[0])
                target_date = now - timedelta(weeks=weeks)
            elif "month" in date_str.lower():
                months = int(re.findall(r"\d+", date_str)[0])
                target_date = now - timedelta(days=months * 30)
            else:
                return "unknown"
            return target_date.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    try:
        if "T" in date_str and ("+" in date_str or "Z" in date_str or date_str.endswith("00:00")):
            if "+" in date_str:
                date_part = date_str.split("+")[0]
            elif "Z" in date_str:
                date_part = date_str.replace("Z", "")
            else:
                date_part = date_str

            if "." in date_part:
                parsed_date = datetime.strptime(date_part.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            else:
                parsed_date = datetime.strptime(date_part, "%Y-%m-%dT%H:%M:%S")
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    try:
        if "," in date_str and len(date_str.split()) >= 3:
            parsed_date = datetime.strptime(date_str, "%b %d, %Y")
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    try:
        if re.match(r"\d{4}-\d{2}-\d{2}$", date_str):
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    return date_str


class WebScrapingJinaTool:
    def __init__(self):
        self.api_key = os.environ.get("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("Jina API key not provided! Please set JINA_API_KEY environment variable.")

    def __call__(self, query: str) -> List[Dict[str, Any]]:
        print(f"Searching for {query}")
        all_urls = self._jina_search(query)
        return_content = []
        print(f"Found {len(all_urls)} URLs")
        if len(all_urls) > 1:
            all_urls = random.sample(all_urls, 1)
        for url in all_urls:
            print(f"Scraping {url}")
            return_content.append(self._jina_scrape(url))
            print(f"Scraped {url}")
        return return_content

    def _jina_scrape(self, url: str) -> Dict[str, Any]:
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                "Accept": "application/json",
                "Authorization": self.api_key,
                "X-Timeout": "10",
                "X-With-Generated-Alt": "true",
            }
            response = requests.get(jina_url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Jina AI Reader Failed for {url}: {response.status_code}")
            response_dict = response.json()
            return {
                "url": response_dict["data"]["url"],
                "title": response_dict["data"]["title"],
                "description": response_dict["data"]["description"],
                "content": response_dict["data"]["content"],
                "publish_time": response_dict["data"].get("publishedTime", "unknown"),
            }
        except Exception as e:
            logger.error(str(e))
            return {"url": url, "content": "", "error": str(e)}

    def _jina_search(self, query: str) -> List[str]:  # noqa: C901
        url = f"https://s.jina.ai/?q={query}&n=1"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "X-Respond-With": "no-content",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            if json_data is None:
                print(f"⚠️ Jina API returned empty data, query: {query}")
                return []
            if "data" not in json_data:
                print(f"⚠️ Jina API response format abnormal, query: {query}, response: {json_data}")
                return []
            filtered_urls = []
            for item in json_data.get("data", []):
                if "url" not in item:
                    continue
                raw_date = item.get("date", "unknown")
                standardized_date = parse_date_to_standard(raw_date)
                if standardized_date == "unknown" or standardized_date == raw_date:
                    filtered_urls.append(item["url"])
                    continue
                today_date = get_config_value("TODAY_DATE")
                if today_date:
                    if today_date > standardized_date:
                        filtered_urls.append(item["url"])
                else:
                    filtered_urls.append(item["url"])
            print(f"Found {len(filtered_urls)} URLs after filtering")
            return filtered_urls
        except requests.exceptions.RequestException as e:
            print(f"❌ Jina API request failed: {e}")
            return []
        except ValueError as e:
            print(f"❌ Jina API response parsing failed: {e}")
            return []
        except Exception as e:
            print(f"❌ Jina search unknown error: {e}")
            return []


mcp = FastMCP("Search")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.tool()
def get_information(query: str) -> str:
    """
    Use search tool to scrape and return main content information related to specified query in a structured way.
    """
    try:
        tool = WebScrapingJinaTool()
        results = tool(query)
        if not results:
            return f"⚠️ Search query '{query}' found no results. May be network issue or API limitation."
        formatted_results = []
        for result in results:
            if "error" in result:
                formatted_results.append(f"Error: {result['error']}")
            else:
                formatted_results.append(
                    f"""
URL: {result['url']}
Title: {result['title']}
Description: {result['description']}
Publish Time: {result['publish_time']}
Content: {result['content'][:1000]}...\n"""
                )
        if not formatted_results:
            return f"⚠️ Search query '{query}' returned empty results."
        return "\n".join(formatted_results)
    except Exception as e:
        return f"❌ Search tool execution failed: {str(e)}"


if __name__ == "__main__":
    port = int(os.getenv("SEARCH_HTTP_PORT", "8001"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)