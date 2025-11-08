from transformers import pipeline

# Load toxicity classifier
classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert"
)

def is_toxic(text: str):
    """
    Returns (True/False, score)
    toxic -> True
    safe  -> False
    """
    result = classifier(text)[0]
    label = result["label"]
    score = result["score"]

    return (label == "toxic", score)

if __name__ == "__main__":
    txt = input("Text: ")
    bad, score = is_toxic(txt)
    print("Toxic:", bad, "| Score:", round(score, 3))
