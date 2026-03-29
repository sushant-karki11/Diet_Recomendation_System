# clean_csv.py
import pandas as pd
import os

# Set the base directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
input_path = os.path.join(BASE_DIR, "static/data/food_nepali_full.csv")
output_path = os.path.join(BASE_DIR, "static/data/food_nepali_full_clean.csv")

# Read the CSV
print(f"Reading CSV from: {input_path}")
df = pd.read_csv(input_path)

print(f"Original dataset:")
print(f"  Total rows: {len(df)}")
print(f"  Unique foods: {df['Food_items'].nunique()}")

df_clean = df.drop_duplicates(subset=['Food_items'], keep='first')

if len(duplicates) > 0:
    print(f"\nFound {len(duplicates['Food_items'].unique())} foods with duplicates:")
    
    # Group duplicates
    duplicate_counts = df['Food_items'].value_counts()
    foods_with_duplicates = duplicate_counts[duplicate_counts > 1]
    
    for food_name, count in foods_with_duplicates.items():
        print(f"  '{food_name}': {count} entries")
        
        # Show different values for the same food
        food_rows = df[df['Food_items'] == food_name]
        print(f"    Calories values: {food_rows['Calories'].tolist()}")
        print(f"    Protein values: {food_rows['Proteins'].tolist()}")
        print()
    
    # Remove duplicates, keeping the first occurrence
    df_clean = df.drop_duplicates(subset=['Food_items'], keep='first')
    
    print(f"\nCleaned dataset:")
    print(f"  Total rows after cleaning: {len(df_clean)}")
    print(f"  Rows removed: {len(df) - len(df_clean)}")
    
    # Save cleaned version
    df_clean.to_csv(output_path, index=False)
    print(f"\nCleaned CSV saved to: {output_path}")
    
    # Optional: Also create a version with average values instead of just keeping first
    print("\n\nAlternative: Creating averaged version...")
    
    # Group by food name and average numeric columns
    numeric_cols = ['Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 'Sodium', 
                   'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD', 'Sugars']
    
    # For boolean columns (Breakfast, Lunch, Dinner, VegNovVeg), take max (if any is 1, keep as 1)
    bool_cols = ['Breakfast', 'Lunch', 'Dinner', 'VegNovVeg']
    
    averaged_df = df.groupby('Food_items').agg({
        **{col: 'mean' for col in numeric_cols},
        **{col: 'max' for col in bool_cols}
    }).reset_index()
    
    # Round numeric columns
    for col in numeric_cols:
        averaged_df[col] = averaged_df[col].round(2)
    
    # Convert boolean columns back to 0/1
    for col in bool_cols:
        averaged_df[col] = averaged_df[col].astype(int)
    
    # Save averaged version
    averaged_path = os.path.join(BASE_DIR, "static/data/food_nepali_full_averaged.csv")
    averaged_df.to_csv(averaged_path, index=False)
    print(f"Averaged CSV saved to: {averaged_path}")
    
else:
    print("No duplicates found!")
    # Still save a copy just in case
    df.to_csv(output_path, index=False)
    print(f"CSV copied to: {output_path}")