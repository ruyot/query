# Query Backend API Specification

This document describes the API interface that the Query Chrome extension expects from the backend service.

## Endpoint

```
POST /api/search
```

## Request Format

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "query": "teach me biology"
}
```

## Response Format

### Success Response (200 OK)

```json
{
  "query": "teach me biology",
  "categories": {
    "academic": [
      {
        "title": "Understanding Biology: A Comprehensive Guide",
        "url": "https://example.com/biology-guide",
        "description": "Peer-reviewed research article covering fundamental concepts in biology, including cellular processes, genetics, and evolution.",
        "source": "Nature Journal",
        "credibility": 95,
        "publicationDate": "2024"
      }
    ],
    "videos": [
      {
        "title": "Biology 101: Complete Beginner's Course",
        "url": "https://youtube.com/watch?v=example1",
        "description": "Comprehensive video series covering all major biology topics, perfect for beginners and students.",
        "source": "Khan Academy",
        "duration": "45:30",
        "views": "2.5M",
        "credibility": 90
      }
    ],
    "courses": [
      {
        "title": "Biology: The Science of Life",
        "url": "https://coursera.org/biology-course",
        "description": "Full online course with certificates, taught by university professors.",
        "source": "Coursera",
        "rating": 4.8,
        "students": "125K",
        "credibility": 92
      }
    ],
    "websites": [
      {
        "title": "Biology Online Tutorial",
        "url": "https://biologytutorial.com",
        "description": "Interactive tutorials with quizzes and visual aids for learning biology.",
        "source": "Biology Tutorial",
        "credibility": 75
      }
    ],
    "books": [
      {
        "title": "Campbell Biology (12th Edition)",
        "url": "https://amazon.com/campbell-biology",
        "description": "The most popular biology textbook used in universities worldwide.",
        "source": "Amazon",
        "rating": 4.6,
        "credibility": 93
      }
    ]
  },
  "metadata": {
    "totalResults": 15,
    "processingTime": "0.8s",
    "searchDepth": 50
  }
}
```

## Result Object Schemas

### Common Fields (All Categories)
All result objects must include:
- `title` (string): The title of the result
- `url` (string): The URL to the source
- `description` (string): Brief description of the content
- `source` (string): The source/publisher name
- `credibility` (number, 0-100): Credibility score

### Category-Specific Fields

#### Academic
- `publicationDate` (string): Year or date published
- Optional: `authors`, `journal`, `citations`

#### Videos
- `duration` (string): Video length (e.g., "45:30")
- `views` (string): View count (e.g., "2.5M")
- Optional: `uploadDate`, `channelName`

#### Courses
- `rating` (number): Course rating (e.g., 4.8)
- `students` (string): Number of students (e.g., "125K")
- Optional: `price`, `duration`, `level`

#### Websites
- Optional: `lastUpdated`, `readTime`

#### Books
- `rating` (number): Book rating
- Optional: `author`, `publisher`, `year`, `pages`, `isbn`

## Error Response (4xx, 5xx)

```json
{
  "error": {
    "message": "Description of what went wrong",
    "code": "ERROR_CODE"
  }
}
```

## Backend Implementation Guidelines

### 1. Web Scraping
- Scrape Google search results for the given query
- Respect rate limits to avoid being blocked
- Consider using Google Custom Search API as an alternative
- Parse result titles, URLs, descriptions, and snippets

### 2. Content Classification
Use ML/AI to classify results into categories:
- **Academic**: Look for `.edu`, `.gov`, journal sites, citation patterns
- **Videos**: Identify YouTube, Vimeo, educational platforms
- **Courses**: Detect Coursera, edX, Udemy, Khan Academy
- **Websites**: General informational sites, blogs
- **Books**: Amazon, Google Books, publisher sites

### 3. Credibility Scoring
Factors to consider:
- Domain authority (Elastic could help here)
- Source reputation (academic > commercial)
- Content quality signals
- Backlinks and citations
- HTTPS usage
- Domain age
- Author expertise

### 4. Ranking Algorithm
Use Elastic Search to:
- Index scraped content
- Apply relevance scoring
- Boost high-credibility sources
- Consider freshness for time-sensitive queries
- Personalize based on query intent

### 5. Performance Targets
- Response time: < 3 seconds
- Minimum results per category: 3-5
- Total results: 15-30
- Scrape depth: 30-50 sources

### 6. Caching Strategy
- Cache popular queries (24 hour TTL)
- Use Google Cloud Memorystore/Redis
- Invalidate on demand
- Pre-cache trending topics

## Example cURL Request

```bash
curl -X POST https://your-api.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "teach me biology"}'
```

## Rate Limiting

Consider implementing:
- Per-IP rate limits
- API key authentication for production
- Throttling for expensive queries

## CORS Configuration

For development, allow:
```
Access-Control-Allow-Origin: chrome-extension://[extension-id]
```

For production, consider:
- API key authentication
- Proper CORS policies
- Request validation

## Tech Stack Recommendations

### Google Cloud Platform
- **Cloud Run**: Serverless API hosting
- **Cloud Functions**: For lightweight processing
- **Compute Engine**: For scraping workers
- **Cloud Storage**: Cache and static assets
- **Cloud CDN**: Fast delivery

### Elastic
- **Elasticsearch**: Search and ranking engine
- **Kibana**: Monitoring and analytics
- **Logstash**: Data ingestion pipeline

### Additional Services
- **Puppeteer/Playwright**: Browser automation for scraping
- **BeautifulSoup/Cheerio**: HTML parsing
- **Redis**: Fast caching layer
- **PostgreSQL**: Metadata storage

## Security Considerations

1. **Input Validation**: Sanitize all user queries
2. **Rate Limiting**: Prevent abuse
3. **API Keys**: Authenticate requests
4. **HTTPS Only**: Secure communication
5. **XSS Prevention**: Escape all output
6. **SQL Injection**: Use parameterized queries

## Monitoring & Logging

Track these metrics:
- Average response time
- Error rates by category
- Cache hit/miss ratio
- Scraping success rates
- Popular queries
- User engagement (clicks per category)

## Testing

Provide these test queries:
- Educational: "teach me biology", "learn python programming"
- Research: "climate change research papers"
- How-to: "how to bake sourdough bread"
- Complex: "best machine learning courses for beginners"

Expected behavior:
- Return at least 3 results per relevant category
- Prioritize high-credibility sources
- Complete in < 3 seconds
- Handle typos gracefully
- Return empty array for categories with no results

