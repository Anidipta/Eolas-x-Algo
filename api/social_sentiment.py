
# api/social_sentiment.py
import os
import requests
import pandas as pd
from datetime import datetime
import time
import re
from textblob import TextBlob

class SocialSentiment:
    def __init__(self):
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    def get_reddit_token(self):
        auth = requests.auth.HTTPBasicAuth(self.reddit_client_id, self.reddit_client_secret)
        data = {
            'grant_type': 'client_credentials',
            'username': os.getenv("REDDIT_USERNAME", ""),
            'password': os.getenv("REDDIT_PASSWORD", "")
        }
        headers = {'User-Agent': 'GridTrader/0.1'}
        response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
        return response.json().get('access_token')
    
    def get_reddit_sentiment(self, token_symbol):
        try:
            access_token = self.get_reddit_token()
            headers = {'User-Agent': 'GridTrader/0.1', 'Authorization': f'bearer {access_token}'}
            
            # Search for token in CryptoCurrency subreddit
            response = requests.get(
                f"https://oauth.reddit.com/r/CryptoCurrency/search.json?q={token_symbol}&restrict_sr=1&sort=new&limit=50",
                headers=headers
            )
            
            if response.status_code != 200:
                return []
            
            posts = response.json().get('data', {}).get('children', [])
            results = []
            
            for post in posts:
                post_data = post.get('data', {})
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                created = post_data.get('created_utc', 0)
                
                # Perform sentiment analysis
                blob = TextBlob(f"{title} {selftext}")
                sentiment_score = blob.sentiment.polarity
                
                results.append({
                    'title': title,
                    'created': created,
                    'sentiment': sentiment_score,
                    'source': 'reddit',
                    'url': f"https://reddit.com{post_data.get('permalink', '')}"
                })
            
            return results
        except Exception as e:
            print(f"Error fetching Reddit sentiment: {e}")
            return []
    
    def get_twitter_sentiment(self, token_symbol):
        """Simulated Twitter sentiment analysis (due to API limitations)"""
        # Instead of actual API call, we'll generate simulated data
        import random
        from datetime import datetime, timedelta
        
        results = []
        sentiments = [-0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8]
        
        # Generate 20 simulated tweets
        for i in range(20):
            created_at = datetime.now() - timedelta(hours=random.randint(0, 24))
            sentiment = random.choice(sentiments)
            
            results.append({
                'text': f"Simulated tweet about ${token_symbol} #{token_symbol} #crypto",
                'created': created_at.timestamp(),
                'sentiment': sentiment,
                'source': 'twitter',
                'url': ''
            })
        
        return results

def analyze_social_sentiment(token_symbol):
    sentiment_analyzer = SocialSentiment()
    
    # Get sentiment from Reddit
    reddit_data = sentiment_analyzer.get_reddit_sentiment(token_symbol)
    
    # Get sentiment from Twitter (simulated)
    twitter_data = sentiment_analyzer.get_twitter_sentiment(token_symbol)
    
    # Combine data
    all_data = reddit_data + twitter_data
    
    # Sort by creation time
    all_data = sorted(all_data, key=lambda x: x['created'], reverse=True)
    
    # Calculate average sentiment
    sentiments = [item['sentiment'] for item in all_data]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    
    # Determine sentiment trend
    recent_sentiments = [item['sentiment'] for item in all_data[:10]]
    older_sentiments = [item['sentiment'] for item in all_data[10:]]
    
    recent_avg = sum(recent_sentiments) / len(recent_sentiments) if recent_sentiments else 0
    older_avg = sum(older_sentiments) / len(older_sentiments) if older_sentiments else 0
    
    trend = "neutral"
    if recent_avg > older_avg + 0.1:
        trend = "bullish"
    elif recent_avg < older_avg - 0.1:
        trend = "bearish"
    
    return {
        'token': token_symbol,
        'data': all_data,
        'average_sentiment': avg_sentiment,
        'sentiment_trend': trend,
        'total_mentions': len(all_data),
        'timestamp': datetime.now().timestamp()
    }
