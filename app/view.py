import os
from app import app, db
from newsplease import NewsPlease
from app.form import (UrlForm, WordCountForm, LoginForm, RegistrationForm, StoreForm, FolderForm, EditArticleForm,
                      SearchForm)
from flask import render_template, redirect, url_for, request, session, flash, jsonify
import requests
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from app.summarization import generate_summary
from app.senti_analysis import senti_analysis
from app.tags import generate_tags
from app.models import User, Article, Folder

API_URL = 'https://newsapi.org/v2/everything?apiKey={api_key}&sources={sources}&q={keyword}'

API_KEY = os.getenv("API_KEY")

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('summarization'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('summarization'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('summarization'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data,
                            password_hash=generate_password_hash(form.password.data, salt_length=32))
        db.session.add(new_user)
        try:
            db.session.commit()
            flash(f'Registration for {form.username.data} received', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
    return render_template('register.html', title='Register', form=form)


@app.route('/summarization', methods=['GET', 'POST'])
@login_required
def summarization():
    urlform = UrlForm()
    count_form = WordCountForm()
    urls = []
    results = []
    news_data = []
    error_message = None
    searchform = SearchForm()

    if urlform.validate_on_submit():
        url1 = urlform.url1.data
        url2 = urlform.url2.data
        url3 = urlform.url3.data
        url4 = urlform.url4.data
        url5 = urlform.url5.data
        urls.append(url1)
        if url2:
            urls.append(url2)
        if url3:
            urls.append(url3)
        if url4:
            urls.append(url4)
        if url5:
            urls.append(url5)

        max_count = count_form.max_count.data
        min_count = count_form.min_count.data
        for url in urls:
            article = NewsPlease.from_url(url)
            title = article.title
            author = article.authors
            the_author = author[0] if author else 'Unknown'
            date = article.date_publish
            content = article.maintext
            summary = generate_summary(content, max_count, min_count)
            tags = generate_tags(content)
            label, score = senti_analysis(summary)
            try:
                results.append({
                    'url': url,
                    'title': title,
                    'author': the_author,
                    'date': date,
                    'summary': summary,
                    'senti_score': score,
                    'senti_label': label,
                    'tags': tags
                })
            except Exception as e:
                flash(f'A result error occurred: {str(e)}', 'danger')

        session['results'] = results
        return redirect(url_for('result'))

    elif searchform.validate_on_submit():

        keyword = searchform.search.data
        selected_sources = request.form.getlist('sources')

        sources_str = ','.join(selected_sources)

        api_url = API_URL.format(api_key=API_KEY, sources=sources_str, keyword=keyword or "")

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type')

            if 'application/json' in content_type:
                articles = response.json().get('articles', [])
                if articles:
                    news_data = sorted(articles, key=lambda x: x['publishedAt'], reverse=True)
                else:
                    error_message = 'No articles found for the keyword.'
            else:
                error_message = f'Invalid content type: {content_type}'
                news_data = [{'title': 'Error', 'description': error_message, 'url': '#'}]
        except requests.exceptions.RequestException as e:
            error_message = f'Error retrieving news: {str(e)}'
            news_data = [{'title': 'Error', 'description': error_message, 'url': '#'}]
        except ValueError as e:
            error_message = f'Error parsing JSON: {str(e)}'
            news_data = [{'title': 'Error', 'description': error_message, 'url': '#'}]

    return render_template('summarization.html', urlform=urlform, count_form=count_form, news=news_data,
                           error_message=error_message, searchform=searchform)


@app.route('/result', methods=['GET', "POST"])
@login_required
def result():
    results = session.get('results', [])
    form = StoreForm()
    replace_articles = []
    save_articles = []
    form.folder.choices = [(folder.id, folder.name) for folder in Folder.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        selected_articles = request.form.getlist('articles')
        folder_id = form.folder.data

        for index in selected_articles:
            article = results[int(index)]
            article['folder_id'] = folder_id
            exist_article = Article.query.filter_by(url=article['url'], user_id=current_user.id, folder_id=folder_id).first()
            if exist_article:
                replace_articles.append({'new': article, 'old_id': exist_article.id})
            else:
                save_articles.append(article)

        try:
            for article in save_articles:
                new_article = Article(
                    url=article['url'],
                    title=article['title'],
                    author=article['author'],
                    date=article['date'],
                    summary=article['summary'],
                    senti_score=article['senti_score'],
                    senti_label=article['senti_label'],
                    tags=article['tags'],
                    user_id=current_user.id,
                    folder_id=folder_id
                )
                db.session.add(new_article)
            db.session.commit()
            if save_articles:
                flash(f'Selected new articles:{article['title']} have been stored successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while storing new articles: {str(e)}', 'danger')

        if replace_articles:
            session['replace_articles'] = replace_articles
            return redirect(url_for('confirm_replace'))

        return redirect(url_for('result'))
    return render_template('result.html', form=form, results=results)

@app.route('/confirm_replace', methods=['GET', 'POST'])
@login_required
def confirm_replace():
    replace_articles = session.get('replace_articles', [])
    for item in replace_articles:
        item['old'] = Article.query.get(item['old_id'])
        item['new_folder_name'] = Folder.query.get(item['new']['folder_id']).name

    if request.method == 'POST':
        current_article = replace_articles[0]
        old_article = Article.query.get(current_article['old_id'])
        new_article = current_article['new']
        confirm_key = f'confirm_{replace_articles.index(current_article)}'

        if confirm_key in request.form:
            old_article.title = new_article['title']
            old_article.author = new_article['author']
            old_article.date = new_article['date']
            old_article.summary = new_article['summary']
            old_article.senti_score = new_article['senti_score']
            old_article.senti_label = new_article['senti_label']
            old_article.tags = new_article['tags']
            old_article.folder_id = new_article['folder_id']

            db.session.add(old_article)

            try:
                db.session.commit()
                flash(f'Article "{old_article.title}" has been updated', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error occurred: {str(e)}', 'danger')

        else:
            flash(f'Article "{old_article.title}" was not replaced', 'info')

        replace_articles.pop(0)

        if replace_articles:
            session['replace_articles'] = [{'new': item['new'], 'old_id': item['old_id']} for item in replace_articles]
            return redirect(url_for('confirm_replace'))
        else:
            session.pop('replace_articles', None)
            return redirect(url_for('result'))

    return render_template('replace.html', replace_articles=replace_articles)

@app.route('/myarticle', methods=['GET', 'POST'])
@login_required
def my_article():
    form = FolderForm()

    if form.validate_on_submit():
        new_folder = Folder(name=form.name.data, user_id=current_user.id)
        db.session.add(new_folder)
        try:
            db.session.commit()
            flash('Folder created successfully!', 'success')
            return redirect(url_for('my_article'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')


    folders = Folder.query.filter_by(user_id=current_user.id).all()

    return render_template('myarticle.html', folders=folders, form=form)

@app.route('/folder/<int:folder_id>', methods=['GET'])
@login_required
def view_folder(folder_id):
    folder = Folder.query.get(folder_id)

    if folder.user_id != current_user.id:
        flash('You do not have access to this folder.', 'danger')
        return redirect(url_for('my_article'))

    articles = Article.query.filter_by(folder_id=folder.id).all()

    return render_template('view_folder.html', folder=folder, articles=articles)

@app.route('/delete_folder/<int:folder_id>', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.get(folder_id)
    try:
        db.session.delete(folder)
        db.session.commit()
        flash('Folder deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('my_article'))

@app.route('/delete_articles', methods=['POST'])
@login_required
def delete_article():
    article_ids = request.form.getlist('article_ids')
    if article_ids:
        articles_to_delete = Article.query.filter(Article.id.in_(article_ids)).all()
        for article in articles_to_delete:
            db.session.delete(article)
        try:
            db.session.commit()
            flash(f'Successfully deleted', 'success')
            return redirect(url_for('view_folder', folder_id=article.folder_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred while deleting articles: {str(e)}', 'danger')
    return redirect(url_for('my_article'))

@app.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get(article_id)
    form = EditArticleForm(tags=article.tags)
    if form.validate_on_submit():
        article.tags = form.tags.data
        db.session.commit()
        flash('Article tags updated.', 'success')
        return redirect(url_for('view_folder', folder_id=article.folder_id))
    return render_template('edit.html', form=form, article=article)

@app.route('/compare_articles', methods=['POST'])
@login_required
def compare_articles():
    article_ids = request.form.getlist('article_ids')
    if article_ids:
        articles = Article.query.filter(Article.id.in_(article_ids)).all()
        positive_articles = sorted([article for article in articles if article.senti_label == 'Positive'], key=lambda x: x.senti_score, reverse=True)
        negative_articles = sorted([article for article in articles if article.senti_label == 'Negative'], key=lambda x: x.senti_score, reverse=True)
        neutral_articles = sorted([article for article in articles if article.senti_label == 'Neutral'], key=lambda x: x.senti_score, reverse=True)

    return render_template('compare.html', positive_articles=positive_articles,
                           negative_articles=negative_articles, neutral_articles=neutral_articles)







