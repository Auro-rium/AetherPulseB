from transformers import pipeline

# Load once at module level for efficiency
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=False)
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

def detect_emotion(text):
    """Detect emotion for a single text."""
    if not text:
        return "neutral"
    
    # Summarize if too long
    processed_text = summarize_text(text)
    
    try:
        result = emotion_classifier(processed_text)
        return result[0]['label']
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return "neutral"

def detect_emotion_batch(texts, batch_size=32):
    """Detect emotion for a list of texts (batch processing)."""
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
            batch_results = emotion_classifier(processed_batch)
            results.extend([r[0]['label'] for r in batch_results])
        except Exception as e:
            print(f"Error in batch emotion detection: {e}")
            results.extend(["neutral"] * len(processed_batch))
    return results