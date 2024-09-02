from keybert import KeyBERT

kw_model = KeyBERT(model='all-MiniLM-L6-v2')
def generate_tags(content):
    keywords = kw_model.extract_keywords(content, keyphrase_ngram_range=(1, 1),
                                         stop_words='english', top_n=3)
    tags = ', '.join([kw[0] for kw in keywords])
    return tags
