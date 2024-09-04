import tkinter as tk
from tkinter import messagebox
from aima3.logic import expr, FolKB, fol_fc_ask
import sqlite3
from PIL import Image, ImageTk
import ast

conn = sqlite3.connect('meal_plans.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS meal_plans (plan_text TEXT)''')

def save_meal_plan_to_db(mel):
    c.execute("INSERT INTO meal_plans (plan_text) VALUES (?)", (mel,))
    conn.commit()

def fetch_meal_plans_from_db():
    c.execute("SELECT * FROM meal_plans")
    meal_plans = c.fetchall()
    return meal_plans


def calculate_calories(user_profile):
    age = user_profile["age"]
    weight = user_profile["weight"]
    height = user_profile["height"]
    gender = user_profile["gender"]
    activity_level = user_profile["activity_level"]

    if gender == "Male":
        base_calorie_intake = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        base_calorie_intake = 10 * weight + 6.25 * height - 5 * age - 161

    if activity_level == "Sedentary":
        calorie_intake = base_calorie_intake * 1.2
    elif activity_level == "Light":
        calorie_intake = base_calorie_intake * 1.375
    elif activity_level == "Moderate":
        calorie_intake = base_calorie_intake * 1.55
    elif activity_level == "Active":
        calorie_intake = base_calorie_intake * 1.725
    else:
        calorie_intake = base_calorie_intake * 1.9
    
    return calorie_intake


kb = FolKB()

# RULES

kb.tell(expr("Calorie_intake_below1500(x) & Sedentary(x) ==> Low_calorie_meal(x)"))
kb.tell(expr("Calorie_intake_above1500(x) & Calorie_intake_below2000(x) & Sedentary(x) ==> Balanced_meal(x)"))
kb.tell(expr("Calorie_intake_above2000(x) & Sedentary(x) ==> High_protein_meal(x)"))

kb.tell(expr("Calorie_intake_below1500(x) & Light(x) ==> Light_meal(x)"))
kb.tell(expr("Calorie_intake_above1500(x) & Calorie_intake_below2000(x) & Light(x) ==> Balanced_meal(x)"))
kb.tell(expr("Calorie_intake_above2000(x) & Light(x) ==> Protein_rich_meal(x)"))

kb.tell(expr("Calorie_intake_below1500(x) & Moderate(x) ==> Balanced_meal(x)"))
kb.tell(expr("Calorie_intake_above1500(x) & Calorie_intake_below2000(x) & Moderate(x) ==> Energy_rich_meal(x)"))
kb.tell(expr("Calorie_intake_above2000(x) & Moderate(x) ==> Protein_carb_balanced_meal(x)"))

kb.tell(expr("Calorie_intake_below1500(x) & Active(x) ==> Protein_rich_meal(x)"))
kb.tell(expr("Calorie_intake_above1500(x) & Calorie_intake_below2000(x) & Active(x) ==> High_energy_meal(x)"))
kb.tell(expr("Calorie_intake_above2000(x) & Active(x) ==> Carb_protein_balanced_meal(x)"))

kb.tell(expr("Calorie_intake_below1500(x) & VeryActive(x) ==> High_protein_meal(x)"))
kb.tell(expr("Calorie_intake_above1500(x) & Calorie_intake_below2000(x) & VeryActive(x) ==> High_energy_meal(x)"))
kb.tell(expr("Calorie_intake_above2000(x) & VeryActive(x) ==> Carb_rich_meal(x)"))

kb.tell(expr("Low_calorie_meal(x) ==> Recommended_meals('Salad with grilled chicken', 'Vegetable stir-fry', 'Poached fish with steamed vegetables', 'Greek yogurt with berries')"))
kb.tell(expr("Balanced_meal(x) ==> Recommended_meals('Quinoa salad with grilled shrimp', 'Brown rice bowl with tofu and mixed vegetables', 'Grilled chicken with sweet potato and broccoli', 'Turkey and avocado wrap')"))
kb.tell(expr("High_protein_meal(x) ==> Recommended_meals('Grilled salmon with quinoa and asparagus', 'Egg white omelette with spinach and tomatoes', 'Lean beef with roasted vegetables', 'Chickpea and vegetable curry with brown rice')"))
kb.tell(expr("Light_meal(x) ==> Recommended_meals('Mixed green salad with vinaigrette dressing', 'Vegetable soup with whole grain roll', 'Grilled vegetable and hummus wrap', 'Quinoa salad with lemon-tahini dressing')"))
kb.tell(expr("Protein_rich_meal(x) ==> Recommended_meals('Grilled chicken breast with roasted vegetables', 'Turkey chili with mixed beans', 'Salmon salad with avocado and mixed greens', 'Tofu and vegetable stir-fry with brown rice')"))
kb.tell(expr("Energy_rich_meal(x) ==> Recommended_meals('Whole wheat pasta with marinara sauce and lean turkey meatballs', 'Bean and vegetable chili with quinoa', 'Grilled chicken and vegetable kebabs with couscous', 'Vegetable and lentil stew with crusty bread')"))
kb.tell(expr("Protein_carb_balanced_meal(x) ==> Recommended_meals('Turkey and quinoa stuffed bell peppers', 'Grilled chicken Caesar salad with whole grain croutons', 'Salmon and vegetable quinoa bowl', 'Tofu and broccoli stir-fry with brown rice')"))
kb.tell(expr("High_energy_meal(x) ==> Recommended_meals('Chicken and vegetable curry with brown rice', 'Beef stir-fry with noodles', 'Grilled shrimp and vegetable skewers with quinoa', 'Chickpea and sweet potato hash with fried eggs')"))
kb.tell(expr("Carb_protein_balanced_meal(x) ==> Recommended_meals('Teriyaki chicken and vegetable stir-fry with brown rice', 'Quinoa and black bean salad with grilled chicken', 'Spaghetti with turkey meatballs and marinara sauce', 'Grilled tofu and vegetable kebabs with couscous')"))
kb.tell(expr("Carb_rich_meal(x) ==> Recommended_meals('Vegetable and chickpea curry with naan bread', 'Pasta primavera with grilled chicken', 'Sweet potato and black bean enchiladas', 'Mushroom and spinach risotto')"))


agenda = []

# Function to submit user profile
def submit_profile():
   
    age = int(age_entry.get())
    weight = float(weight_entry.get())
    height = float(height_entry.get())
    gender = gender_var.get()
    activity_level = activity_var.get()

    user_profile = {"age": age, "weight": weight, "height": height, "gender": gender, "activity_level": activity_level}
    
    calorie_intake = calculate_calories(user_profile)

    if calorie_intake < 1500:
        agenda.append(expr("Calorie_intake_below1500(Heeshaam)"))
    if calorie_intake > 1500:
        agenda.append(expr("Calorie_intake_above1500(Heeshaam)"))
    if calorie_intake < 2000 :
        agenda.append(expr("Calorie_intake_below2000(Heeshaam)"))
    if calorie_intake > 2000:
        agenda.append(expr("Calorie_intake_above2000(Heeshaam)"))

    l = user_profile["activity_level"]
    agenda.append(expr(f"{l}(Heeshaam)"))

    process_agenda(calorie_intake)

memory = {}

def process_agenda(calorie_intake):
    seen = set()
    while agenda:
        p = agenda.pop(0)
        if p in seen:
            continue
        seen.add(p)
        if fol_fc_ask(kb, p):
            memory[p] = True
        else:
            memory[p] = False

        # Rules activation
        if memory.get(expr('Calorie_intake_below1500(Heeshaam)'), False) and memory.get(expr('Sedentary(Heeshaam)'), False):
            agenda.append(expr("Low_calorie_meal(Heeshaam)"))

        if memory.get(expr('Low_calorie_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Salad with grilled chicken', 'Vegetable stir-fry', 'Poached fish with steamed vegetables', 'Greek yogurt with berries')"))

        if memory.get(expr('Calorie_intake_above1500(Heeshaam)'), False) and memory.get(expr('Calorie_intake_below2000(Heeshaam)'), False) and memory.get(expr('Sedentary(Heeshaam)'), False):
            agenda.append(expr("Balanced_meal(Heeshaam)"))

        if memory.get(expr('Balanced_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Quinoa salad with grilled shrimp', 'Brown rice bowl with tofu and mixed vegetables', 'Grilled chicken with sweet potato and broccoli', 'Turkey and avocado wrap')"))

        if memory.get(expr('Calorie_intake_above2000(Heeshaam)'), False) and memory.get(expr('Sedentary(Heeshaam)'), False):
            agenda.append(expr("High_protein_meal(Heeshaam)"))

        if memory.get(expr('High_protein_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Grilled salmon with quinoa and asparagus', 'Egg white omelette with spinach and tomatoes', 'Lean beef with roasted vegetables', 'Chickpea and vegetable curry with brown rice')"))
        
        if memory.get(expr('Calorie_intake_below1500(Heeshaam)'), False) and memory.get(expr('Light(Heeshaam)'), False):
            agenda.append(expr("Light_meal(Heeshaam)"))

        if memory.get(expr('Light_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Mixed green salad with vinaigrette dressing', 'Vegetable soup with whole grain roll', 'Grilled vegetable and hummus wrap', 'Quinoa salad with lemon-tahini dressing')"))

        if memory.get(expr('Calorie_intake_above1500(Heeshaam)'), False) and memory.get(expr('Calorie_intake_below2000(Heeshaam)'), False) and memory.get(expr('Light(Heeshaam)'), False):
            agenda.append(expr("Protein_rich_meal(Heeshaam)"))

        if memory.get(expr('Protein_rich_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Grilled chicken breast with roasted vegetables', 'Turkey chili with mixed beans', 'Salmon salad with avocado and mixed greens', 'Tofu and vegetable stir-fry with brown rice')"))

        if memory.get(expr('Calorie_intake_above2000(Heeshaam)'), False) and memory.get(expr('Light(Heeshaam)'), False):
            agenda.append(expr("Protein_rich_meal(Heeshaam)"))
            
        if memory.get(expr('Calorie_intake_above1500(Heeshaam)'), False) and memory.get(expr('Calorie_intake_below2000(Heeshaam)'), False) and memory.get(expr('Moderate(Heeshaam)'), False):
            agenda.append(expr("Energy_rich_meal(Heeshaam)"))
        
        if memory.get(expr('Energy_rich_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Whole wheat pasta with marinara sauce and lean turkey meatballs', 'Bean and vegetable chili with quinoa', 'Grilled chicken and vegetable kebabs with couscous', 'Vegetable and lentil stew with crusty bread')"))

        if memory.get(expr('Calorie_intake_above2000(Heeshaam)'), False) and memory.get(expr('Moderate(Heeshaam)'), False):
            agenda.append(expr("Protein_carb_balanced_meal(Heeshaam)"))

        if memory.get(expr('Protein_carb_balanced_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Turkey and quinoa stuffed bell peppers', 'Grilled chicken Caesar salad with whole grain croutons', 'Salmon and vegetable quinoa bowl', 'Tofu and broccoli stir-fry with brown rice')"))

        if memory.get(expr('Calorie_intake_above1500(Heeshaam)'), False) and memory.get(expr('Calorie_intake_below2000(Heeshaam)'), False) and memory.get(expr('Active(Heeshaam)'), False):
            agenda.append(expr("High_energy_meal(Heeshaam)"))

        if memory.get(expr('High_energy_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Chicken and vegetable curry with brown rice', 'Beef stir-fry with noodles', 'Grilled shrimp and vegetable skewers with quinoa', 'Chickpea and sweet potato hash with fried eggs')"))

        if memory.get(expr('Calorie_intake_above2000(Heeshaam)'), False) and memory.get(expr('Active(Heeshaam)'), False):
            agenda.append(expr("Carb_protein_balanced_meal(Heeshaam)"))

        if memory.get(expr('Carb_protein_balanced_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Teriyaki chicken and vegetable stir-fry with brown rice', 'Quinoa and black bean salad with grilled chicken', 'Spaghetti with turkey meatballs and marinara sauce', 'Grilled tofu and vegetable kebabs with couscous')"))

        if memory.get(expr('Calorie_intake_above2000(Heeshaam)'), False) and memory.get(expr('VeryActive(Heeshaam)'), False):
            agenda.append(expr("Carb_rich_meal(Heeshaam)"))

        if memory.get(expr('Carb_rich_meal(Heeshaam)'), False):
            agenda.append(expr("Recommended_meals('Vegetable and chickpea curry with naan bread', 'Pasta primavera with grilled chicken', 'Sweet potato and black bean enchiladas', 'Mushroom and spinach risotto')"))
    
    # Prepare meal plan message
    me = []
    meal_plan = "Selected meal plan:\n"
    me.append(meal_plan)
    i=0
    for p, value in memory.items():
        if value:
            meal_plan += f'{p}\n'
            me.append(p)
            i += 1

    mel = "Selected meal plan:\n\n"
    mel += f'-> {me[i-1]}\n\n'.replace("(Heeshaam)", "")
    mel += "Recommended meal plans :\n\n"
    mele = f'{me[i]}\n'.replace("Recommended_meals(","")
    mele2 = mele.replace(")","")
    mele3= mele2.split(", ")
    
    for k in mele3:
        
        mel += "->  " + k
        mel += '\n'
    mel += '_____________________________________________________'
    mel += '_______________________________________________'

    save_meal_plan_to_db(mel)

    meal_plan_text.insert(tk.END, mel)

# Function to create user profile input form
def create_profile_form():
    global age_entry, weight_entry, height_entry, gender_var, activity_var
    profile_form = tk.Frame(root, bg="lightblue")
    profile_form.pack()

    
    age_label = tk.Label(profile_form, text="Age:", bg="lightblue", fg="black", font=("Arial", 12))
    age_label.grid(row=0, column=0, padx=10, pady=5)
    age_entry = tk.Entry(profile_form, bg="white", fg="black", font=("Arial", 12))
    age_entry.grid(row=0, column=1, padx=10, pady=5)

    
    weight_label = tk.Label(profile_form, text="Weight (kg):", bg="lightblue", fg="black", font=("Arial", 12))
    weight_label.grid(row=1, column=0, padx=10, pady=5)
    weight_entry = tk.Entry(profile_form, bg="white", fg="black", font=("Arial", 12))
    weight_entry.grid(row=1, column=1, padx=10, pady=5)

    
    height_label = tk.Label(profile_form, text="Height (cm):", bg="lightblue", fg="black", font=("Arial", 12))
    height_label.grid(row=2, column=0, padx=10, pady=5)
    height_entry = tk.Entry(profile_form, bg="white", fg="black", font=("Arial", 12))
    height_entry.grid(row=2, column=1, padx=10, pady=5)

    
    gender_label = tk.Label(profile_form, text="Gender:", bg="lightblue", fg="black", font=("Arial", 12))
    gender_label.grid(row=3, column=0, padx=10, pady=5)
    gender_var = tk.StringVar(profile_form)
    gender_var.set("Male")
    gender_option = tk.OptionMenu(profile_form, gender_var, "Male", "Female")
    gender_option.config(bg="white", fg="black", font=("Arial", 12))
    gender_option.grid(row=3, column=1, padx=10, pady=5)

    
    activity_label = tk.Label(profile_form, text="Activity Level:", bg="lightblue", fg="black", font=("Arial", 12))
    activity_label.grid(row=4, column=0, padx=10, pady=5)
    activity_var = tk.StringVar(profile_form)
    activity_var.set("Sedentary")
    activity_option = tk.OptionMenu(profile_form, activity_var, "Sedentary", "Light", "Moderate", "Active", "VeryActive")
    activity_option.config(bg="white", fg="black", font=("Arial", 12))
    activity_option.grid(row=4, column=1, padx=10, pady=5)

    
    submit_button = tk.Button(profile_form, text="Submit", command=submit_profile, width=20, bg="#003319", fg="white", font=("Arial", 12), relief=tk.RAISED)
    submit_button.grid(row=5, columnspan=2, pady=10)

    
    submit_button.config(cursor="hand2")  



icon_image = Image.open("logoo.png")  
icon_image.save("icon.ico")

root = tk.Tk()
root.title("Meal Planner")
root.iconbitmap("icon.ico")
root.configure(bg="lightblue")

def display_meal_plans():
    meal_plans = fetch_meal_plans_from_db()
    for plan in meal_plans:
        print(plan)

create_profile_form()

custom_font = ("Comic sans", 12,"bold")
meal_plan_text = tk.Text(root, height=10, width=50, bg="white", fg="black", font=custom_font)
meal_plan_text.pack(pady=20)

root.mainloop()
display_meal_plans()
