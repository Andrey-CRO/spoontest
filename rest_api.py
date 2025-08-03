from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Load your trained model (ensure recipe_recommender.pkl is in your repl files)
print("Files here:", os.listdir('.'))
try:
    model = joblib.load("recipe_recommender.pkl")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    print(data)
    bookmarks = data.get("bookmarks", [])
    candidates = data.get("candidates", [])

    results = []
    for candidate in candidates:
        combined_text = candidate + " " + " ".join(bookmarks)
        pred = model.predict([combined_text])[0]
        prob = model.predict_proba([combined_text])[0][1]
        results.append({"prediction": int(pred), "probability": float(prob), "candidate": candidate})

    return jsonify(results)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
