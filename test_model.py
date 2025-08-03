import joblib
import json
import random

# Load model
model = joblib.load("recipe_recommender.pkl")

# Load recipe dataset (same used in training)
with open('spoonacular_recipes.json') as f:
    recipes = json.load(f)

# Build lookup
id_to_ingredients = {r['id']: r['ingredients'] for r in recipes}
id_to_cuisine = {r['id']: r['cuisine'] for r in recipes}
id_to_title = {r['id']: r['title'] for r in recipes}
id_to_text = {r['id']: r['ingredients'] + ' ' + r['cuisine'] for r in recipes}
all_ids = list(id_to_text.keys())

# 1. Simulate a user: randomly choose 3 bookmarked recipes
bookmarks = random.sample(all_ids, 3)
print("User bookmarks:")
for rid in bookmarks:
    print(f"- {rid} {id_to_title[rid]} ({id_to_cuisine[rid]})")

# 2. Simulate candidate recipes (e.g., from findByIngredients)
# Choose 20 random ones that are not bookmarked
candidates = [rid for rid in all_ids if rid not in bookmarks]
candidates = random.sample(candidates, 20)

# Combine the user's bookmarks into a single string
bookmark_text = ' '.join([id_to_text[rid] for rid in bookmarks])

# 3. For each candidate, concatenate with the bookmark context
candidate_texts = [
    bookmark_text + ' ' + id_to_text[rid]
    for rid in candidates
]

predictions = model.predict(candidate_texts)
probabilities = model.predict_proba(candidate_texts)[:, 1]  # Prob for class 1

# 4. Zip together and sort by probability (descending)
results = list(zip(candidates, predictions, probabilities))
results.sort(key=lambda x: x[2], reverse=True)

# 5. Output sorted predictions
print("\nModel predictions (sorted by confidence):")
for rid, pred, prob in results:
    liked = "Likely liked" if pred == 1 else "Unlikely"
    print(f"{rid} {id_to_title[rid]} ({id_to_cuisine[rid]}): {liked} (confidence: {prob:.2f})")
