from transformers import pipeline

intent_classifier = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection", return_all_scores=False)
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

def detect_intent(text):
    """Detect intent for a single text (e.g., spam/ham)."""
    if not text:
        return "ham"
    
    # Summarize if too long
    processed_text = summarize_text(text)
    
    try:
        result = intent_classifier(processed_text)
        return result[0]['label']
    except Exception as e:
        print(f"Error in intent detection: {e}")
        return "ham"

def detect_intent_batch(texts, batch_size=32):
    """Detect intent for a list of texts (batch processing)."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # Process each text in the batch
        processed_batch = []
        for text in batch:
            if not text:
                processed_batch.append("ham")
                continue
            processed_text = summarize_text(text)
            processed_batch.append(processed_text)
        
        try:
            batch_results = intent_classifier(processed_batch)
            results.extend([r[0]['label'] for r in batch_results])
        except Exception as e:
            print(f"Error in batch intent detection: {e}")
            results.extend(["ham"] * len(processed_batch))
    return results