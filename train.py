import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load recipe data
with open('../spoonacular_recipes.json') as f:
    recipes = json.load(f)

print(f"Loaded {len(recipes)} recipes")

# Preprocess
for r in recipes:
    r['text'] = r['ingredients'] + ' ' + r['cuisine']

# Map for easy lookup
id_to_ingredients = {r['id']: r['ingredients'] for r in recipes}
id_to_cuisine = {r['id']: r['cuisine'].lower() for r in recipes}
id_to_text = {r['id']: r['text'] for r in recipes}
all_recipe_ids = list(id_to_text.keys())

# Parameters
NUM_USERS = 5000
BOOKMARKS_PER_USER = 5
SIMILARITY_THRESHOLD = 0.45  # Combined score
CUISINE_BONUS = 0.25        # Bonus if cuisine matches

def ingredient_overlap(ing1, ing2):
    set1 = set(ing1.lower().split())
    set2 = set(ing2.lower().split())
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

X = []
y = []

for _ in range(NUM_USERS):
    bookmarks = random.sample(all_recipe_ids, BOOKMARKS_PER_USER)
    bookmark_ingredients = [id_to_ingredients[rid] for rid in bookmarks]
    bookmark_cuisines = [id_to_cuisine[rid] for rid in bookmarks]

    for rid in all_recipe_ids:
        if rid in bookmarks:
            continue

        candidate_ing = id_to_ingredients[rid]
        candidate_cuisine = id_to_cuisine[rid]

        max_similarity = 0
        for i, b_ing in enumerate(bookmark_ingredients):
            sim = ingredient_overlap(candidate_ing, b_ing)
            if candidate_cuisine == bookmark_cuisines[i]:
                sim += CUISINE_BONUS
            max_similarity = max(max_similarity, sim)

        label = 1 if max_similarity >= SIMILARITY_THRESHOLD else 0
        X.append(id_to_text[rid])
        y.append(label)

print(f"Generated dataset with {len(X)} samples. Positive examples: {sum(y)}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model: TF-IDF + Logistic Regression
model = Pipeline([
    ('vectorizer', TfidfVectorizer(max_features=5000)),
    ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced'))
])

print("Training model...")
model.fit(X_train, y_train)

print("Evaluating model...")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
joblib.dump(model, "recipe_recommender.pkl")
