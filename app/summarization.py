from transformers import BartTokenizer, BartForConditionalGeneration
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
summary_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

def generate_summary(content, max_count, min_count):
    inputs = tokenizer.encode("summarize: " + content, return_tensors="pt",
                              max_length=1024, truncation=True)
    summary_ids = summary_model.generate(inputs, max_length=max_count, min_length=min_count,
                                        num_beams=5, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary