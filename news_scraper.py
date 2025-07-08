from newsapi import NewsApiClient
from langchain.document_loaders import NewsURLLoader
from transformers import pipeline

class CrisisMonitor:
    def __init__(self, api_key):
        self.newsapi = NewsApiClient(api_key=api_key)
        self.sentiment = pipeline("text-classification", model="ProsusAI/finbert")
        
    def get_crisis_insights(self, keywords, num_articles=5):
        # Get articles from NewsAPI
        news = self.newsapi.get_everything(
            q=keywords,
            language="en",
            sort_by="relevancy",
            page_size=num_articles
        )
        
        # Extract and analyze content
        insights = []
        for article in news['articles']:
            # Financial sentiment analysis
            sentiment = self.sentiment(article['title'])[0]
            insights.append({
                "title": article['title'],
                "source": article['source']['name'],
                "sentiment": sentiment['label'],
                "score": sentiment['score'],
                "url": article['url']
            })
        return insights
    
    def calculate_crisis_score(self, insights):
        """Convert news insights to 0-10 crisis score"""
        weights = {
            'NEGATIVE': 1.0,
            'NEUTRAL': 0.2,
            'POSITIVE': -0.5
        }
        return min(10, sum(i['score'] * weights[i['sentiment']] for i in insights))
