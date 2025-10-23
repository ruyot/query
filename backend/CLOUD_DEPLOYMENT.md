# Elastic Cloud Deployment Guide

This guide will help you deploy your data ingestion pipeline to Elastic Cloud.

## Quick Start

### 1. Prerequisites

- Python 3.8+ installed
- Elastic Cloud account (free 14-day trial available)
- SerpAPI account (free tier: 250 searches/month)

### 2. Setup Elastic Cloud

1. **Create Account**: Go to [Elastic Cloud](https://cloud.elastic.co/) and sign up
2. **Create Deployment**: 
   - Click "Create deployment"
   - Choose "Serverless" for cost efficiency
   - Select your preferred region
   - Note down your Cloud ID and generate an API key

### 3. Configure Your Environment

1. **Copy the example file**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```env
   # SerpAPI (required)
   SERPAPI_KEY=your_serpapi_key_here
   
   # Elastic Cloud
   ELASTIC_URL=https://your-deployment-id.region.aws.found.io:9243
   ELASTIC_API_KEY=your_api_key_here
   ```

### 4. Test Your Setup

```bash
# Validate your configuration
python deploy_cloud.py

# Or use the built-in validation
python main.py --validate-cloud
```

### 5. Run Your First Query

```bash
python main.py "machine learning tutorials"
```

## Configuration

### Direct URL Method

```env
ELASTIC_URL=https://your-deployment-id.region.aws.found.io:9243
ELASTIC_API_KEY=your_api_key_here
```

**Benefits**: 
- Simple and explicit
- Easy to understand
- Direct connection to your deployment

## Getting Your Credentials

### Elasticsearch URL
1. Go to your Elastic Cloud deployment
2. Click on your deployment name
3. Find "Elasticsearch endpoint" in the overview section
4. Copy the URL (e.g., `https://your-deployment-id.region.aws.found.io:9243`)

### Elastic API Key
1. In your deployment, go to **Security** → **API Keys**
2. Click **Create API Key**
3. Give it a name (e.g., "search-pipeline")
4. Copy the generated key (you won't see it again!)

### SerpAPI Key
1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for a free account
3. Go to your dashboard
4. Copy your API key

## Troubleshooting

### Connection Issues

```bash
# Test basic configuration
python main.py --validate-config

# Test cloud connection specifically
python main.py --validate-cloud
```

### Common Problems

1. **"Missing required environment variables"**
   - Check your `.env` file exists
   - Ensure all required variables are set
   - No spaces around the `=` sign

2. **"Elasticsearch connection failed"**
   - Verify your API key is correct
   - Check your Elasticsearch URL is correct
   - Ensure your deployment is active

3. **"Index creation failed"**
   - Your API key might not have sufficient permissions
   - Try regenerating your API key with full permissions

### Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Elastic Cloud documentation: [Elastic Cloud Docs](https://www.elastic.co/guide/en/cloud/current/index.html)
- SerpAPI documentation: [SerpAPI Docs](https://serpapi.com/search-api)

## Cost Optimization

### Serverless Benefits
- Pay only for what you use
- Automatic scaling
- No infrastructure management

### Usage Tips
- Start with small queries to test
- Monitor your usage in the Elastic Cloud dashboard
- Use the free tier limits effectively

## Next Steps

Once your pipeline is working:

1. **Scale up**: Increase `--pages` parameter for more results
2. **Automate**: Set up scheduled runs with cron jobs
3. **Monitor**: Use Elastic Cloud's monitoring features
4. **Extend**: Add custom processing logic to the pipeline

## Security Best Practices

1. **Never commit your `.env` file** to version control
2. **Use environment-specific API keys** for different deployments
3. **Rotate API keys regularly**
4. **Monitor usage** in your Elastic Cloud dashboard
