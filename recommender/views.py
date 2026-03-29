from django.shortcuts import render
from recommender.functions import Weight_Gain, Weight_Loss, Healthy
from recommender.models import Food


def diet(request):
    error = None

    if request.method == "POST":
        try:
            # 🔹 Get inputs
            age = int(request.POST.get("age"))
            weight = float(request.POST.get("weight"))
            height_ft = float(request.POST.get("height_ft"))
            height_in = float(request.POST.get("height_in"))
            bodyfat = float(request.POST.get("bodyfat"))
            goal = request.POST.get("goal")
            activity = float(request.POST.get("activity"))
            gender = request.POST.get("gender")

            # 🔹 VALIDATION
            if not (5 <= age <= 100):
                error = "Age must be between 5 and 100."
            elif not (30 <= weight <= 300):
                error = "Weight must be between 30 kg and 300 kg."
            elif not (1 <= height_ft <= 8):
                error = "Height (feet) must be between 1 and 8."
            elif not (0 <= height_in < 12):
                error = "Inches must be between 0 and 12."
            elif not (5 <= bodyfat <= 60):
                error = "Body fat % must be between 5 and 60."
            elif activity not in [1.2, 1.375, 1.55, 1.725, 1.9]:
                error = "Invalid activity level."
            elif gender not in ["m", "f"]:
                error = "Invalid gender selection."

            if error:
                return render(request, "index.html", {"error": error})

            # 🔹 Convert height (ft + inches → meters)
            height = (height_ft * 12 + height_in) * 0.0254

            # 🔹 Lean factor
            leanfactor = 0.85
            if gender == "m":
                if 10 <= bodyfat <= 14:
                    leanfactor = 1
                elif 15 <= bodyfat <= 20:
                    leanfactor = 0.95
                elif 21 <= bodyfat <= 28:
                    leanfactor = 0.90
            else:
                if 14 <= bodyfat <= 18:
                    leanfactor = 1
                elif 19 <= bodyfat <= 28:
                    leanfactor = 0.95
                elif 29 <= bodyfat <= 38:
                    leanfactor = 0.90

            # 🔹 Maintenance calories
            maintaincalories = int(weight * 24 * leanfactor * activity)

            # 🔹 Goal logic
            if goal == "weight gain":
                breakfast_qs, lunch_qs, dinner_qs, bmi, bmiinfo = Weight_Gain(age, weight, height)
                caloriesreq = maintaincalories + 300
            elif goal == "weight loss":
                breakfast_qs, lunch_qs, dinner_qs, bmi, bmiinfo = Weight_Loss(age, weight, height)
                caloriesreq = maintaincalories - 300
            else:
                breakfast_qs, lunch_qs, dinner_qs, bmi, bmiinfo = Healthy(age, weight, height)
                caloriesreq = maintaincalories

            context = {
                "breakfast": breakfast_qs,
                "lunch": lunch_qs,
                "dinner": dinner_qs,
                "bmi": round(bmi, 2),
                "bmiinfo": bmiinfo,
                "caloriesreq": caloriesreq
            }

            return render(request, "diet.html", context)

        except (TypeError, ValueError):
            error = "Please enter valid numeric values."

    return render(request, "index.html", {"error": error})


def index(request): return render(request, "index.html") 
def bodymass(request): return render(request,"bodymass.html") 
def home(request): return render(request,"home.html") 
def login(request): return render(request,"login.html")
