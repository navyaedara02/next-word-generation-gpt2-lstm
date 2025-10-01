# shared_project_functions.py

import os
import json
import pickle
import numpy as np
from tensorflow import keras


def get_target_subdirectory(corpus_name: str, subdir_string: str = "model"):
    """
    Finds or creates a model subdirectory for the given corpus.
    Example: model_0_shakespeare, model_1_sherlock
    """
    # Check if a subdir already exists
    for dir in os.listdir():
        if os.path.isdir(dir) and dir.endswith("_" + corpus_name):
            return dir

    # Otherwise, pick the next available index
    model_numbers = []
    for dir in os.listdir():
        if os.path.isdir(dir) and dir.startswith(f"{subdir_string}_"):
            n = dir.replace(f"{subdir_string}_", "").split("_")[0]
            try:
                model_numbers.append(int(n))
            except ValueError:
                pass

    first_unused = 0
    while first_unused in model_numbers:
        first_unused += 1

    new_dir = f"{subdir_string}_{first_unused}_{corpus_name}"
    os.makedirs(new_dir, exist_ok=True)
    print(f"📂 Created new directory: {new_dir}")
    return new_dir


def load_trained_model_and_data(base_argument):
    """
    Loads a trained model (.keras) and its associated data.
    Returns None if any required file is missing.
    """
    try:
        # Model path
        model_path = f"{base_argument}_model.keras"
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return None

        # Load model
        print(f"🔍 Loading model from {model_path} ...")
        model = keras.models.load_model(model_path, compile=False)

        # Vocabulary
        vocab_path = f"{base_argument}_word_to_id.json"
        if not os.path.exists(vocab_path):
            print(f"❌ Vocabulary file not found: {vocab_path}")
            return None
        with open(vocab_path, "r") as f:
            word_to_id = json.load(f)
        id_to_word = {v: k for k, v in word_to_id.items()}

        # Preprocessing
        preprocess_path = f"{base_argument}_preprocessed_data.pkl"
        if not os.path.exists(preprocess_path):
            print(f"❌ Preprocessed data not found: {preprocess_path}")
            return None
        with open(preprocess_path, "rb") as f:
            preprocessed_data = pickle.load(f)

        max_seq_length = preprocessed_data.get("max_seq_length", 20)

        print(f"✅ Successfully loaded {base_argument}")
        return {
            "model": model,
            "word_to_id": word_to_id,
            "id_to_word": id_to_word,
            "max_seq_length": max_seq_length,
        }

    except Exception as e:
        print(f"⚠️ Could not load model {base_argument}: {e}")
        return None


def generate_text(model, seed_text, num_words_to_generate, word_to_id, id_to_word, max_seq_length):
    """
    Generates text using the trained model given a seed text.
    """
    if model is None:
        return "[Model not available]"

    processed_seed = [
        word_to_id.get(word.lower(), word_to_id.get("<UNK>", 0))
        for word in seed_text.split()
    ]
    generated_text = ""

    for _ in range(num_words_to_generate):
        # Pad or truncate
        padded_sequence = processed_seed[-max_seq_length:]
        padded_sequence += [word_to_id.get("<PAD>", 0)] * (max_seq_length - len(padded_sequence))
        padded_sequence = np.array(padded_sequence).reshape(1, max_seq_length)

        # Predict distribution
        predictions = model.predict(padded_sequence, verbose=0)[0]

        # Sample a word
        predicted_id = np.random.choice(len(predictions), p=predictions)
        predicted_word = id_to_word.get(predicted_id, "<UNK>")

        if predicted_word == "<EOS>":
            break

        generated_text += " " + predicted_word
        processed_seed.append(predicted_id)

    return generated_text.strip()
