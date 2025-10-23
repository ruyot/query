"""
Result parsing and categorization module.
"""
from typing import Dict, List, Any, Optional


class ResultParser:
    """Parser for categorizing and structuring search results."""
    
    @staticmethod
    def categorize_results(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize search results into videos and articles based on pagemap metadata.

        Args:
            items: Raw search result items from Google API

        Returns:
            Dictionary with 'videos' and 'articles' keys, each containing all matching results
        """
        videos = []
        articles = []

        for item in items:
            category = ResultParser._classify_item(item)

            if category == 'video':
                videos.append(item)
            elif category == 'article':
                articles.append(item)
            # If category is None, treat as generic article/webpage
            elif category is None:
                articles.append(item)

        return {
            'videos': videos,
            'articles': articles
        }
    
    @staticmethod
    def _classify_item(item: Dict[str, Any]) -> Optional[str]:
        """
        Classify a single search result item based on pagemap metadata.
        
        Args:
            item: Single search result item
            
        Returns:
            'video', 'article', or None if no clear classification
        """
        pagemap = item.get('pagemap', {})
        
        # Check for video indicators
        if 'videoobject' in pagemap:
            return 'video'
        
        # Check for article indicators
        article_types = ['article', 'blogposting', 'newsarticle']
        for article_type in article_types:
            if article_type in pagemap:
                return 'article'
        
        return None
    
    @staticmethod
    def structure_json_document(item: Dict[str, Any], query: str, category: str, rank: int) -> Dict[str, Any]:
        """
        Structure a search result item into a clean JSON document.
        
        Args:
            item: Raw search result item
            query: Original search query
            category: 'video' or 'article'
            rank: Original rank from Google
            
        Returns:
            Structured JSON document
        """
        pagemap = item.get('pagemap', {})
        
        # Extract basic information
        title = item.get('title', 'No title available')
        url = item.get('link', '')
        snippet = item.get('snippet', 'No description available')
        
        # Extract optional fields
        thumbnail_url = None
        author = None
        
        # Try to get thumbnail from pagemap or image
        if 'imageobject' in pagemap:
            images = pagemap['imageobject']
            if images and len(images) > 0:
                thumbnail_url = images[0].get('url')
        elif 'metatags' in pagemap:
            metatags = pagemap['metatags']
            if metatags and len(metatags) > 0:
                thumbnail_url = metatags[0].get('og:image') or metatags[0].get('twitter:image')
        
        # Try to get author information
        if 'metatags' in pagemap:
            metatags = pagemap['metatags']
            if metatags and len(metatags) > 0:
                author = (metatags[0].get('article:author') or 
                         metatags[0].get('author') or 
                         metatags[0].get('og:site_name'))
        
        # Build structured document
        document = {
            'query': query,
            'category': category,
            'title': title,
            'url': url,
            'description': snippet,
            'source': 'google',
            'rank': rank,
            'timestamp': ResultParser._get_current_timestamp()
        }
        
        # Add optional fields if available
        if thumbnail_url:
            document['thumbnailUrl'] = thumbnail_url
        if author:
            document['author'] = author
        
        return document
    
    @staticmethod
    def _get_current_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


def categorize_results(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convenience function to categorize search results.
    
    Args:
        items: Raw search result items
        
    Returns:
        Dictionary with categorized results
    """
    parser = ResultParser()
    return parser.categorize_results(items)
