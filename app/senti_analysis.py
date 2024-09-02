from transformers import pipeline

senti_model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

def senti_analysis(content):
    result = senti_model(content)
    label_map = {
        'LABEL_0': 'Negative',
        'LABEL_1': 'Neutral',
        'LABEL_2': 'Positive'
    }
    label = label_map[result[0]['label']]
    score = round(result[0]['score'], 3)
    return label, score

