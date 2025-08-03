import requests
import json
import time

API_KEY = 'c4773c25ae68477289bc120460cf7f9d'
RANDOM_RECIPE_URL = 'https://api.spoonacular.com/recipes/random'
MAX_PER_REQUEST = 100
TOTAL_TO_FETCH = 1000  # Change this to however many recipes you want

def fetch_random_recipes(api_key, count=10):
    params = {
        'apiKey': api_key,
        'number': count
    }
    response = requests.get(RANDOM_RECIPE_URL, params=params)
    response.raise_for_status()
    return response.json().get('recipes', [])

def parse_recipe(recipe):
    return {
        'id': recipe['id'],
        'title': recipe['title'],
        'ingredients': ' '.join([ing['nameClean'] for ing in recipe.get('extendedIngredients', [])]),
        'cuisine': ' '.join(recipe.get('cuisines', [])) or 'unknown',
    }

def fetch_many_random_recipes(api_key, total_count):
    all_recipes = []
    for i in range(0, total_count, MAX_PER_REQUEST):
        batch_size = min(MAX_PER_REQUEST, total_count - i)
        print(f"Fetching {batch_size} recipes (batch {i // MAX_PER_REQUEST + 1})...")
        try:
            raw = fetch_random_recipes(api_key, batch_size)
            all_recipes.extend([parse_recipe(r) for r in raw])
        except requests.HTTPError as e:
            print(f"❌ Request failed: {e}")
        time.sleep(1.5)  # Respect API rate limits
    return all_recipes

if __name__ == '__main__':
    all = fetch_many_random_recipes(API_KEY, TOTAL_TO_FETCH)
    
    with open('spoonacular_recipes.json', 'w') as f:
        json.dump(all, f, indent=2)

    print(f"✅ Saved {len(all)} recipes to spoonacular_recipes.json")
