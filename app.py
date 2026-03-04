# app.py

import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/news')
def get_news():
    try:
        response = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY')
        response.raise_for_status()  # Raise an error for bad status codes
        articles = response.json().get('articles', [])
        summaries = [summarize_article(article) for article in articles]
        return jsonify({'summaries': summaries})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


def summarize_article(article):
    # Placeholder for AI summary generation logic
    return {'title': article['title'], 'description': article['description']}

if __name__ == '__main__':
    app.run(debug=True)