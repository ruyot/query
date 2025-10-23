"""
SerpAPI client with pagination support for real Google search results.
"""
from serpapi import GoogleSearch
from typing import List, Dict, Any
from config import SERPAPI_KEY, RESULTS_PER_PAGE


class GoogleSearchClient:
    """Client for interacting with SerpAPI to get real Google search results."""

    def __init__(self):
        self.api_key = SERPAPI_KEY

    def fetch_google_results(self, query: str, num_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch search results from Google via SerpAPI with pagination.
        Extracts both organic results and inline videos to match actual Google display.

        Args:
            query: Search query string
            num_pages: Number of pages to fetch (default: 5)

        Returns:
            List of structured search result items matching Google's format

        Raises:
            ValueError: If no results found or API error occurs
        """
        all_results = []
        global_position = 1  # Track global position across all pages

        for page in range(num_pages):
            start_index = page * RESULTS_PER_PAGE

            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": RESULTS_PER_PAGE,
                "start": start_index,
            }

            try:
                print(f"Fetching page {page + 1} (start={start_index})...")
                search = GoogleSearch(params)
                results = search.get_dict()

                # Check for errors
                if "error" in results:
                    print(f"API Error: {results['error']}")
                    break

                # Extract organic results and inline videos
                organic_results = results.get("organic_results", [])
                inline_videos = results.get("inline_videos", [])

                if not organic_results and not inline_videos:
                    print(f"No more results found at page {page + 1}")
                    break

                print(f"  Found {len(organic_results)} organic results and {len(inline_videos)} inline videos")

                # Process inline videos first (they usually appear near the top on page 1)
                if inline_videos and page == 0:  # Videos typically only on first page
                    for video in inline_videos:
                        structured_video = self._convert_inline_video(video, global_position)
                        all_results.append(structured_video)
                        global_position += 1

                # Process organic results
                for result in organic_results:
                    structured_result = self._convert_serpapi_result(result, global_position)
                    all_results.append(structured_result)
                    global_position += 1

            except Exception as e:
                print(f"Error fetching page {page + 1}: {e}")
                break

        if not all_results:
            raise ValueError(f"No search results found for query: '{query}'")

        print(f"Successfully fetched {len(all_results)} total results")
        return all_results

    def _convert_serpapi_result(self, result: Dict[str, Any], position: int) -> Dict[str, Any]:
        """
        Convert SerpAPI result format to match expected internal format.

        Args:
            result: SerpAPI result object
            position: Position in search results

        Returns:
            Structured result matching expected format
        """
        # Build pagemap structure to match existing parser expectations
        pagemap = {}

        # Detect if it's a video
        if result.get("rich_snippet", {}).get("top", {}).get("detected_extensions", {}).get("video"):
            pagemap["videoobject"] = [
                {
                    "name": result.get("title", ""),
                    "description": result.get("snippet", ""),
                    "thumbnailurl": result.get("thumbnail", ""),
                }
            ]

        # Add metadata
        pagemap["metatags"] = [
            {
                "og:image": result.get("thumbnail"),
                "author": result.get("source"),
            }
        ]

        return {
            "title": result.get("title", "No title available"),
            "link": result.get("link", ""),
            "snippet": result.get("snippet", "No description available"),
            "pagemap": pagemap,
            "position": position,
        }

    def _convert_inline_video(self, video: Dict[str, Any], position: int) -> Dict[str, Any]:
        """
        Convert SerpAPI inline video to match expected format.

        Args:
            video: SerpAPI inline video object
            position: Position in search results

        Returns:
            Structured video result
        """
        pagemap = {
            "videoobject": [
                {
                    "name": video.get("title", ""),
                    "description": video.get("snippet", ""),
                    "thumbnailurl": video.get("thumbnail", ""),
                }
            ],
            "metatags": [
                {
                    "og:image": video.get("thumbnail"),
                    "author": video.get("channel", {}).get("name") if isinstance(video.get("channel"), dict) else video.get("source"),
                }
            ]
        }

        return {
            "title": video.get("title", "No title available"),
            "link": video.get("link", ""),
            "snippet": video.get("snippet", "No description available"),
            "pagemap": pagemap,
            "position": position,
        }

    def test_connection(self) -> bool:
        """
        Test the SerpAPI connection with a simple query.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_results = self.fetch_google_results("test", num_pages=1)
            return len(test_results) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


def fetch_google_results(query: str, num_pages: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch Google search results.

    Args:
        query: Search query string
        num_pages: Number of pages to fetch

    Returns:
        List of structured search result items
    """
    client = GoogleSearchClient()
    return client.fetch_google_results(query, num_pages)
