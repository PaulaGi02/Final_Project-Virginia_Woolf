# Week 1 Starter: Test if your setup works
# This uses a pre-trained model to detect toxic/biased language

from transformers import pipeline

# Load a pre-trained toxicity detection model
print("Loading model... (this may take a minute)")
classifier = pipeline("text-classification",
                     model="unitary/toxic-bert",
                     top_k=None)

# Test texts - mix of sexist and neutral examples
test_texts = [
    "Women are naturally better at nurturing children.",
    "The engineering team completed the project on time.",
    "She's too emotional to be a good leader.",
    "The candidate has extensive technical experience."
]

# Analyze each text
print("\n=== SEXISM DETECTION TEST ===\n")
for text in test_texts:
    result = classifier(text)
    print(f"Text: {text}")
    print(f"Analysis: {result[0]}")
    print("-" * 50)

print("\n✓ If you see results above, your setup works!")
print("Next step: Read NLTK book Chapter 1")