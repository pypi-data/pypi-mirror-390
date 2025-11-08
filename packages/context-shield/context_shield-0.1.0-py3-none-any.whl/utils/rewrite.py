from utils.detect import is_toxic
from textblob import TextBlob

def clean_rewrite(text):
    blob = TextBlob(text)
    rewrite = blob.correct().string

    toxic, _ = is_toxic(rewrite)
    if toxic:
        return "This message may be hurtful. Please express it kindly."

    return rewrite

if __name__ == "__main__":
    txt = input("Text to rewrite: ")
    safe = clean_rewrite(txt)
    print("\nRewritten:")
    print(safe)
