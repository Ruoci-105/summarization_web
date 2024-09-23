# summarization_web
This is a web application integrated with multiple NLP models to assist users in quickly filtering enormous amounts of information, generating news summaries, and performing sentiment analysis.

# How to run this project
Here you should:
git clone git https://github.com/Ruoci-105/summarization_web.git
set .flaskenv 
set News API 
-pip install -r requirements.txt
-flask db upgrade
-run flask

# Usage
1. Users must register an account and log in to use the features of the web.
2. Paste URLs
After logging in, users can enter multiple URLs in URL boxs or use search for news on the web directly with an external API. 
The web will fetch the articles, summarize the content, analyze the sentiment, and auto-generate relevant tags.
3. Present result
After generation task is completed, The result will be presented on the result page. 
4. Saving and Organizing Articles
Users can create folders to save the generated articles.
Users can edit article tags or delete articles or folders.
5. Compare Articles
Users can compare articles based on sentiment scores and labels to view the positive, negative, and neutral articles.