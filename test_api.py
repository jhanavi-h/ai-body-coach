import requests

API_KEY = "WxfedIftsqGR0ygcJfDpy5FdWaIS4pihBqI8i1eP"  # replace with your actual key
food = "chicken breast"

url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food}&api_key={API_KEY}"
response = requests.get(url)
data = response.json()

first_food = data["foods"][0]
print("Food:", first_food["description"])
print("Nutrients:")
for nutrient in first_food["foodNutrients"]:
    if nutrient["nutrientName"] in ["Energy", "Protein", "Total lipid (fat)", "Carbohydrate, by difference"]:
        print(f"  {nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")