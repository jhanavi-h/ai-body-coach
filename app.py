import streamlit as st
import csv
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

LOG_FILE = "meals.csv"
load_dotenv()
API_KEY = os.getenv("USDA_API_KEY") # replace with your actual key

def get_nutrition(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if not data["foods"]:
        return None
    food = data["foods"][0]
    nutrients = {}
    for nutrient in food["foodNutrients"]:
        name = nutrient["nutrientName"]
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
        return []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_meal(meal_name, calories, protein, carbs, fats):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        fieldnames = ["date", "meal", "calories", "protein", "carbs", "fats"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "meal": meal_name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats
        })

st.title("AI Body Recomposition Coach")
st.subheader("Meal Logger")

food_search = st.text_input("Search a food to auto-fill nutrition info")
nutrition = None

if food_search:
    nutrition = get_nutrition(food_search)
    if nutrition:
        st.success(f"Found: {food_search} — {nutrition['calories']} kcal | {nutrition['protein']}g protein | {nutrition['carbs']}g carbs | {nutrition['fats']}g fats")
    else:
        st.warning("Food not found. You can still enter values manually.")

with st.form("meal_form"):
    meal_name = st.text_input("Meal name", value=food_search if food_search else "")
    calories = st.number_input("Calories", min_value=0, value=nutrition["calories"] if nutrition else 0)
    protein = st.number_input("Protein (g)", min_value=0, value=nutrition["protein"] if nutrition else 0)
    carbs = st.number_input("Carbs (g)", min_value=0, value=nutrition["carbs"] if nutrition else 0)
    fats = st.number_input("Fats (g)", min_value=0, value=nutrition["fats"] if nutrition else 0)
    submitted = st.form_submit_button("Log Meal")

if submitted:
    save_meal(meal_name, calories, protein, carbs, fats)
    st.success(f"Logged: {meal_name} — {calories} kcal | {protein}g protein | {carbs}g carbs | {fats}g fats")

st.subheader("Today's Meals")
meals = load_meals()
if meals:
    for meal in meals:
        st.write(f"**{meal['date']}** — {meal['meal']} | {meal['calories']} kcal | {meal['protein']}g protein | {meal['carbs']}g carbs | {meal['fats']}g fats")
else:
    st.write("No meals logged yet.")