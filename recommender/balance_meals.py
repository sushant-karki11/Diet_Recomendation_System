# balance_meals.py
import pandas as pd
import os

def balance_meal_distribution():
    # Get the correct path to the CSV file
    # The script is in recommender/, CSV is in static/data/
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))  # recommender/
    project_root = os.path.dirname(os.path.dirname(script_dir))  # project root
    
    # Construct the full path
    csv_path = os.path.join(project_root,"Diet_recommendation_system", "static", "data", "food_nepali_full.csv")
    output_path = os.path.join(project_root,"Diet_recommendation_system", "static", "data", "food_nepali_full_balanced.csv")
    
    print(f"Looking for CSV at: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        print("Please check the file location.")
        return None
    
    # Read your current CSV
    df = pd.read_csv(csv_path)
    
    print(f"Original data: {len(df)} items")
    
    # Ensure each food appears in at least 2 meals for variety
    for index, row in df.iterrows():
        meal_count = row['Breakfast'] + row['Lunch'] + row['Dinner']
        
        # If a food is only in 1 meal, add it to at least one more
        if meal_count == 1:
            food_type = row['Food_items'].lower()
            
            # Based on food type, add to appropriate meals
            if 'soup' in food_type or 'porridge' in food_type or 'oats' in food_type:
                # Soups and porridge can be breakfast or dinner
                if row['Breakfast'] == 1:
                    df.at[index, 'Dinner'] = 1
                elif row['Dinner'] == 1:
                    df.at[index, 'Breakfast'] = 1
                else:
                    df.at[index, 'Breakfast'] = 1
                    
            elif 'curry' in food_type or 'rice' in food_type or 'bhat' in food_type:
                # Main dishes can be lunch or dinner
                if row['Lunch'] == 1:
                    df.at[index, 'Dinner'] = 1
                elif row['Dinner'] == 1:
                    df.at[index, 'Lunch'] = 1
                else:
                    df.at[index, 'Lunch'] = 1
                    
            elif 'salad' in food_type or 'yogurt' in food_type:
                # Salads can be any meal
                if row['Breakfast'] == 1:
                    df.at[index, 'Lunch'] = 1
                else:
                    df.at[index, 'Breakfast'] = 1
    
    # Save balanced version
    df.to_csv(output_path, index=False)
    print(f"\n✓ Balanced CSV saved to: {output_path}")
    print(f"Output file exists: {os.path.exists(output_path)}")
    
    # Count meal distributions
    breakfast_count = df['Breakfast'].sum()
    lunch_count = df['Lunch'].sum()
    dinner_count = df['Dinner'].sum()
    
    print(f"\n📊 Balanced meal distribution:")
    print(f"  Breakfast items: {breakfast_count}")
    print(f"  Lunch items: {lunch_count}")
    print(f"  Dinner items: {dinner_count}")
    
    # Show foods by meal
    print(f"\n🍽️ Sample Breakfast foods (10):")
    breakfast_foods = df[df['Breakfast'] == 1]['Food_items'].head(10).tolist()
    for i, food in enumerate(breakfast_foods, 1):
        print(f"  {i}. {food}")
    
    print(f"\n🍽️ Sample Lunch foods (10):")
    lunch_foods = df[df['Lunch'] == 1]['Food_items'].head(10).tolist()
    for i, food in enumerate(lunch_foods, 1):
        print(f"  {i}. {food}")
    
    print(f"\n🍽️ Sample Dinner foods (10):")
    dinner_foods = df[df['Dinner'] == 1]['Food_items'].head(10).tolist()
    for i, food in enumerate(dinner_foods, 1):
        print(f"  {i}. {food}")
    
    return df

if __name__ == "__main__":
    balance_meal_distribution()