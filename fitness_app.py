import streamlit as st
import numpy as np
import pandas as pd
import time
import hashlib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import datetime
from datetime import timedelta
import json

# Set page configuration and styling
st.set_page_config(
    page_title="Fitness Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for basic styling
st.markdown("""
    <style>
        .main .block-container {padding-top: 2rem;}
        h1, h2, h3 {color: #4285F4;}
        .stButton>button {background-color: #4285F4; color: white;}
        .stTextInput>div>div>input {border-radius: 5px;}
        .stNumberInput>div>div>input {border-radius: 5px;}
        .stSelectbox>div>div>select {border-radius: 5px;}
        .sidebar .sidebar-content {background-color: #f5f5f5;}
        div.stMetric {background-color: #f0f8ff; padding: 10px; border-radius: 5px;}
        div.css-1r6slb0 {background-color: #f5f5f5; padding: 1.5rem; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load user credentials from file or use default if file doesn't exist
def load_user_credentials():
    if os.path.exists("user_credentials.json"):
        with open("user_credentials.json", "r") as f:
            return json.load(f)
    else:
        # Default credentials
        default_credentials = {
            "Thanvith": hash_password("Thanvith13"),
            "Reddy": hash_password("Reddy13")
        }
        # Save default credentials to file
        with open("user_credentials.json", "w") as f:
            json.dump(default_credentials, f)
        return default_credentials

# Save user credentials to file
def save_user_credentials(credentials):
    with open("user_credentials.json", "w") as f:
        json.dump(credentials, f)

# Load user credentials
USER_CREDENTIALS = load_user_credentials()

# Simulated food database with caloric values (per 100g or standard serving)
FOOD_DATABASE = {
    "Apple": 52,
    "Banana": 89,
    "Chicken Breast": 165,
    "White Rice": 130,
    "Eggs": 155,
    "Oatmeal": 68,
    "Salmon": 208,
    "Broccoli": 34,
    "Sweet Potato": 86,
    "Greek Yogurt": 59,
    "Peanut Butter": 588,
    "Whole Wheat Bread": 265,
    "Avocado": 160,
    "Milk": 42,
    "Protein Shake": 120
}

# App state management
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# User Registration Function
def register_user(username, password, confirm_password, age, height, weight, fitness_level):
    if username in USER_CREDENTIALS:
        return False, "Username already exists. Please choose another."
    
    if password != confirm_password:
        return False, "Passwords do not match."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    # Add new user to credentials
    USER_CREDENTIALS[username] = hash_password(password)
    save_user_credentials(USER_CREDENTIALS)
    
    # Create user profile
    user_profile = {
        "username": username,
        "age": age,
        "height": height,
        "weight": weight,
        "fitness_level": fitness_level,
        "registration_date": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    # Save user profile to dataset
    user_profile_df = pd.DataFrame([user_profile])
    if not os.path.exists("user_profiles.csv"):
        user_profile_df.to_csv("user_profiles.csv", index=False)
    else:
        user_profile_df.to_csv("user_profiles.csv", mode='a', header=False, index=False)
    
    return True, "Registration successful! You can now log in."

# Navigation
if st.session_state['page'] == 'login':
    # Show login/register options
    st.sidebar.header("Fitness Tracker")
    auth_option = st.sidebar.radio("Choose an option", ["Login", "Register"])
    
    if auth_option == "Login":
        # Login Form
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            if username in USER_CREDENTIALS and hash_password(password) == USER_CREDENTIALS[username]:
                st.session_state['username'] = username
                st.session_state['page'] = 'dashboard'
                st.experimental_rerun()
            else:
                st.sidebar.error("Invalid login credentials")
    
    else:
        # Registration Form
        st.header("Create New Account")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reg_username = st.text_input("Choose a Username")
            reg_password = st.text_input("Create a Password", type="password")
            reg_confirm = st.text_input("Confirm Password", type="password")
        
        with col2:
            reg_age = st.number_input("Age", 13, 100, 30)
            reg_height = st.number_input("Height (cm)", 100, 250, 170)
            reg_weight = st.number_input("Weight (kg)", 30, 200, 70)
            reg_fitness = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
        
        if st.button("Register"):
            success, message = register_user(
                reg_username, reg_password, reg_confirm, 
                reg_age, reg_height, reg_weight, reg_fitness
            )
            
            if success:
                st.success(message)
                st.info("Please use the login form to access your account.")
            else:
                st.error(message)

# Main Application (when logged in)
elif st.session_state['page'] == 'dashboard':
    username = st.session_state['username']
    st.sidebar.success(f"Welcome, {username}!")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state['page'] = 'login'
        st.experimental_rerun()
    
    # Load user profile if exists
    user_profile = None
    if os.path.exists("user_profiles.csv"):
        profiles_df = pd.read_csv("user_profiles.csv")
        user_profile = profiles_df[profiles_df["username"] == username].to_dict('records')
        if user_profile:
            user_profile = user_profile[0]
    
    # Load synthetic datasets
    if not os.path.exists("fitness_data.csv"):
        np.random.seed(42)
        data = pd.DataFrame({
            "User_ID": np.arange(1, 101),
            "Age": np.random.randint(18, 60, 100),
            "BMI": np.round(np.random.uniform(18, 35, 100), 2),
            "Duration": np.random.randint(5, 60, 100),
            "Heart_Rate": np.random.randint(60, 150, 100),
            "Body_Temp": np.round(np.random.uniform(36, 40, 100), 2),
            "Calories": np.random.randint(100, 800, 100)
        })
        data.to_csv("fitness_data.csv", index=False)
    
    fitness_data = pd.read_csv("fitness_data.csv")
    
    # Activity tracking and workout logging
    st.sidebar.header("Activity Tracking & Workout Logging")
    activity_type = st.sidebar.selectbox("Select Activity Type", ["Running", "Cycling", "Swimming", "Gym Workout"])
    duration = st.sidebar.slider("Duration (minutes)", 5, 120, 30)
    calories_burned = np.round(np.random.uniform(100, 700), 2)
    
    # Add date selection for workout
    workout_date = st.sidebar.date_input("Workout Date", datetime.datetime.now())
    
    if st.sidebar.button("Log Workout"):
        new_entry = pd.DataFrame([[username, activity_type, duration, calories_burned, workout_date]],
                              columns=["Username", "Activity", "Duration", "Calories", "Date"])
        if not os.path.exists("workout_log.csv"):
            new_entry.to_csv("workout_log.csv", index=False)
        else:
            new_entry.to_csv("workout_log.csv", mode='a', header=False, index=False)
        st.sidebar.success("Workout logged successfully!")
    
    # User Profile Display
    st.header("My Profile")
    if user_profile:
        col1, col2, col3 = st.columns(3)
        col1.metric("Age", user_profile["age"])
        col2.metric("Height", f"{user_profile['height']} cm")
        col3.metric("Weight", f"{user_profile['weight']} kg")
        
        # Calculate and display BMI
        bmi = user_profile["weight"] / ((user_profile["height"]/100) ** 2)
        st.metric("BMI", round(bmi, 1))
        
        # BMI categories
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal weight"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
        
        st.info(f"BMI Category: {bmi_category}")
        st.write(f"Fitness Level: {user_profile['fitness_level']}")
        st.write(f"Member since: {user_profile['registration_date']}")
    else:
        st.info("Profile information not available.")
    
    # NEW FEATURE: Nutrition and Diet Intake Tracking
    st.header("Nutrition & Diet Tracking")
    
    # Date selection for food intake
    food_date = st.date_input("Select Date", datetime.datetime.now())
    
    # Food selection and quantity
    col1, col2 = st.columns(2)
    with col1:
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        food_item = st.selectbox("Select Food", list(FOOD_DATABASE.keys()))
    
    with col2:
        quantity = st.number_input("Quantity (g or serving)", min_value=1, max_value=1000, value=100)
        calories_intake = round(FOOD_DATABASE[food_item] * quantity / 100, 2)
        st.info(f"Calories in {quantity}g of {food_item}: {calories_intake} kcal")
    
    # Custom food entry
    st.subheader("Can't find your food?")
    custom_food = st.text_input("Food Name")
    custom_calories = st.number_input("Calories per 100g/serving", min_value=0, max_value=1000, value=0)
    
    # Log food button
    if st.button("Log Food Intake"):
        food_name = custom_food if custom_food else food_item
        calories = custom_calories if custom_food else calories_intake
        
        new_food_entry = pd.DataFrame([[username, food_date, meal_type, food_name, quantity, calories]],
                                  columns=["Username", "Date", "Meal", "Food", "Quantity", "Calories"])
        
        if not os.path.exists("food_log.csv"):
            new_food_entry.to_csv("food_log.csv", index=False)
        else:
            new_food_entry.to_csv("food_log.csv", mode='a', header=False, index=False)
        
        st.success(f"Added {food_name} to your {meal_type} log!")
    
    # Calorie Summary
    st.header("Calorie Summary")
    
    # Time period selection
    summary_period = st.radio("Select Period", ["Today", "This Week"])
    
    # Calculate date ranges
    today = datetime.datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Display calorie summary
    if os.path.exists("food_log.csv") and os.path.exists("workout_log.csv"):
        food_log = pd.read_csv("food_log.csv")
        workout_log = pd.read_csv("workout_log.csv")
        
        # Convert date columns to datetime
        food_log["Date"] = pd.to_datetime(food_log["Date"]).dt.date
        workout_log["Date"] = pd.to_datetime(workout_log["Date"]).dt.date
        
        # Filter by username
        user_food = food_log[food_log["Username"] == username]
        user_workouts = workout_log[workout_log["Username"] == username]
        
        # Filter by time period
        if summary_period == "Today":
            period_food = user_food[user_food["Date"] == today]
            period_workouts = user_workouts[user_workouts["Date"] == today]
            period_label = "Today"
        else:  # This Week
            period_food = user_food[(user_food["Date"] >= week_start) & (user_food["Date"] <= week_end)]
            period_workouts = user_workouts[(user_workouts["Date"] >= week_start) & (user_workouts["Date"] <= week_end)]
            period_label = f"This Week ({week_start} to {week_end})"
        
        # Calculate totals
        total_calories_in = period_food["Calories"].sum()
        total_calories_burned = period_workouts["Calories"].sum()
        net_calories = total_calories_in - total_calories_burned
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Calories Consumed", f"{round(total_calories_in, 2)} kcal")
        col2.metric("Calories Burned", f"{round(total_calories_burned, 2)} kcal")
        col3.metric("Net Calories", f"{round(net_calories, 2)} kcal")
        
        # Display food log
        st.subheader(f"Food Log - {period_label}")
        if not period_food.empty:
            meal_summary = period_food.groupby("Meal")["Calories"].sum().reset_index()
            st.bar_chart(meal_summary.set_index("Meal"))
            st.dataframe(period_food[["Date", "Meal", "Food", "Quantity", "Calories"]])
        else:
            st.info(f"No food entries for {period_label.lower()}")
        
        # Display workout log
        st.subheader(f"Workout Log - {period_label}")
        if not period_workouts.empty:
            st.dataframe(period_workouts[["Date", "Activity", "Duration", "Calories"]])
        else:
            st.info(f"No workout entries for {period_label.lower()}")
    else:
        st.info("Start logging your food and workouts to see your calorie summary!")
    
    # Progress dashboard
    st.header("Progress Dashboard")
    if os.path.exists("workout_log.csv"):
        workout_log = pd.read_csv("workout_log.csv")
        user_logs = workout_log[workout_log["Username"] == username]
        st.write(user_logs)
    else:
        st.write("No workouts logged yet!")
    
    # Goal setting
    st.sidebar.header("Set Your Goals")
    goal = st.sidebar.text_input("Enter your fitness goal (e.g., Run 5km in 30 min)")
    calorie_goal = st.sidebar.number_input("Daily Calorie Target", 1200, 4000, 2000)
    if goal:
        st.sidebar.success(f"Goal set: {goal}")
    if calorie_goal:
        st.sidebar.success(f"Daily calorie target: {calorie_goal} kcal")
    
    # Prediction model
    X = fitness_data.drop(columns=["User_ID", "Calories"])
    y = fitness_data["Calories"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    st.header("Calorie Prediction")
    age = st.number_input("Enter Age", 18, 60, 30)
    bmi = st.number_input("Enter BMI", 18.0, 35.0, 22.0)
    duration = st.number_input("Enter Exercise Duration (min)", 5, 60, 30)
    heart_rate = st.number_input("Enter Heart Rate", 60, 150, 90)
    body_temp = st.number_input("Enter Body Temperature (°C)", 36.0, 40.0, 37.0)
    
    user_data = pd.DataFrame([[age, bmi, duration, heart_rate, body_temp]], columns=X.columns)
    prediction = model.predict(user_data)
    st.write(f"Predicted Calories Burned: {round(prediction[0], 2)} kcal")