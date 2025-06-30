from transformers import pipeline

summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

def do_summarize(text, chunk_max_size=1024):
    chunks = [text[i:i+chunk_max_size] for i in range(0, len(text), chunk_max_size)]
    summary = []
    for chunk in chunks:
        results = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary.append(results[0]['summary_text'])
    return ' '.join(summary)

with open('output.txt', 'r') as f:
    print(do_summarize(f.read()))
