from transformers import pipeline

# Use sentiment analysis as a simple sarcasm proxy
sarcasm_classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest", return_all_scores=False)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", max_length=130, min_length=30)

def summarize_text(text, max_length=400):
    """Summarize text if it's too long, otherwise return as is."""
    if not text or len(text) <= max_length:
        return text
    
    try:
        # Split into chunks if very long
        if len(text) > 1000:
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            summaries = []
            for chunk in chunks[:3]:  # Limit to first 3 chunks
                summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
                summaries.append(summary[0]['summary_text'])
            return " ".join(summaries)
        else:
            summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
            return summary[0]['summary_text']
    except Exception as e:
        print(f"Error in summarization: {e}")
        # Fallback to truncation
        return text[:max_length] + "..."

def is_sarcastic(text):
    """Detect sarcasm for a single text."""
    if not text:
        return False
    
    # Summarize if too long
    processed_text = summarize_text(text)
    
    try:
        result = sarcasm_classifier(processed_text)
        # Use negative sentiment as a proxy for sarcasm
        return result[0]['label'] == 'negative'
    except Exception as e:
        print(f"Error in sarcasm detection: {e}")
        return False

def is_sarcastic_batch(texts, batch_size=32):
    """Detect sarcasm for a list of texts (batch processing)."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # Process each text in the batch
        processed_batch = []
        for text in batch:
            if not text:
                processed_batch.append("neutral")
                continue
            processed_text = summarize_text(text)
            processed_batch.append(processed_text)
        
        try:
            batch_results = sarcasm_classifier(processed_batch)
            results.extend([r[0]['label'] == 'negative' for r in batch_results])
        except Exception as e:
            print(f"Error in batch sarcasm detection: {e}")
            results.extend([False] * len(processed_batch))
    return results