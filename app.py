import streamlit as st
import csv
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()
API_KEY = os.getenv("USDA_API_KEY")
LOG_FILE = "meals.csv"

def get_nutrition(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={API_KEY}" # builds the web address that you're going to send requests to, food_name and the api key are embedded so the USDA server knows a) what food to search for and b) that you are authorized to use the model
    response = requests.get(url) # requests the food searched
    data = response.json() # returns raw text in JSON format (curly braces, key-value pairs)
    # data is a a dictionary with one key, "foods"

    if not data["foods"]:
        return None
    food = data["foods"][0] # data["foods"] is the list of matching foods the API found
    nutrients = {}

    for nutrient in food["foodNutrients"]: # food["foodNutrients"]
        name = nutrient["nutrientName"] # name of specific nutrient
        if name == "Energy":
            nutrients["calories"] = round(nutrient["value"])
        elif name == "Protein":
            nutrients["protein"] = round(nutrient["value"])
        elif name == "Total lipid (fat)":
            nutrients["fats"] = round(nutrient["value"])
        elif name == "Carbohydrate, by difference":
            nutrients["carbs"] = round(nutrient["value"])

    return nutrients


def load_meals():
    if not os.path.exists(LOG_FILE):
        return[]
    
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)
    
def save_meal(meal_name, calories, protein, carbs, fats):
    file_exists = os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, "a") as f: # append mode adds new content at the end of the file
        fieldnames = ["date", "meal", "calories", "protein", "carbs", "fats"] #column names
        writer = csv.DictWriter(f, fieldnames = fieldnames) 

        if not file_exists:
            writer.writeheader() # writes the row headers
            
        writer.writerow({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                "meal": meal_name, 
                                "calories": calories,
                                "protein": protein, 
                                "carbs": carbs, 
                                "fats": fats})


st.title("AI Body Recomposition Coach")
st.subheader("Meal Logger")

# Text input for searching a food — sits outside the form so it can trigger an API call immediately when the user types
food_search = st.text_input("Search a food to auto-fill nutrition info")
nutrition = None

# If the user has typed something in the search box...
if food_search:
    # ...call the USDA API and store the result
    nutrition = get_nutrition(food_search)
    if nutrition:
        # If we got data back, show a green success message
        st.success(f"Found: {food_search} — {nutrition['calories']} kcal | {nutrition['protein']}g protein | {nutrition['carbs']}g carbs | {nutrition['fats']}g fats")
    else:
        st.warning("Food not found. You can still enter values manually.")

# A form groups all inputs together and only processes them when the user hits submit — without a form, every keystroke would trigger a full page rerun
with st.form("meal_form"):
    meal_name = st.text_input("Meal name", value=food_search if food_search else "")
    # Pre-fill with API data if we have it, otherwise default to 0
    calories = st.number_input("Calories", min_value=0, value=nutrition["calories"] if nutrition else 0)
    protein = st.number_input("Protein (g)", min_value=0, value=nutrition["protein"] if nutrition else 0)
    carbs = st.number_input("Carbs (g)", min_value=0, value=nutrition["carbs"] if nutrition else 0)
    fats = st.number_input("Fats (g)", min_value=0, value=nutrition["fats"] if nutrition else 0)
    # This creates the submit button — when clicked, submitted becomes True
    submitted = st.form_submit_button("Log Meal")

if submitted:
    # Save the meal to the CSV file
    save_meal(meal_name, calories, protein, carbs, fats)
    st.success(f"Logged: {meal_name} — {calories} kcal | {protein}g protein | {carbs}g carbs | {fats}g fats")

st.subheader("Today's Meals")
# Load all saved meals from the CSV every time the page reruns
meals = load_meals()
if meals:
    # Loop through each meal and display it as a line of text
    for meal in meals:
        st.write(f"**{meal['date']}** — {meal['meal']} | {meal['calories']} kcal | {meal['protein']}g protein | {meal['carbs']}g carbs | {meal['fats']}g fats")
else:
    st.write("No meals logged yet.")


def get_ai_coaching(meals):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"You are a fitness and nutrition coach specializing in body recomposition. Give specific feedback on whether the macros of {meals} supports body recomposition goals"}
        ]
    )

    return message.content[0].text

if st.button("Get AI Feedback"):
    with st.spinner("Thinking..."):
        st.write(get_ai_coaching(meals))