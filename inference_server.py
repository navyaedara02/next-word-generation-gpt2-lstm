# inference_server.py

import os
from flask import Flask, request, jsonify
import shared_project_functions as spf

# ==========================================================
# Define Shakespeare model only
# ==========================================================
model_list = {
    "shakespeare": "model_0_shakespeare/shakespeare"
}

# Load trained model + data
model_data = {
    "shakespeare": spf.load_trained_model_and_data(model_list["shakespeare"])
}

# ==========================================================
# Flask App Setup
# ==========================================================
app = Flask(__name__)

last_input_text = None
suggestions = []
model_name = None

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    global last_input_text, suggestions, model_name

    data = request.get_json()
    input_text = data.get('text', '')
    model_name = data.get('model', 'shakespeare')

    if input_text != last_input_text:
        last_input_text = input_text
        print("✅ New request received")

        if not input_text.strip():
            suggestions = ["no suggestions"]
        else:
            model_info = model_data["shakespeare"]
            model = model_info["model"]
            word_to_id = model_info["word_to_id"]
            id_to_word = model_info["id_to_word"]
            max_seq_length = model_info["max_seq_length"]

            generated_text = spf.generate_text(
                model, input_text, 5, word_to_id, id_to_word, max_seq_length
            )
            suggestions = [generated_text]

        print(f"🔹 Input: {input_text} | Suggestions: {suggestions}")
    else:
        print("♻️ Duplicate request, using cached suggestions")

    return jsonify({
        "suggestions": suggestions,
        "model": "shakespeare",
        "model_list": list(model_list.keys())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
