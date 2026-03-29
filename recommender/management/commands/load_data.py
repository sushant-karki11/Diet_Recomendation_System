import csv
import os
from django.core.management.base import BaseCommand
from recommender.models import Food
from django.conf import settings

class Command(BaseCommand):
    help = 'Load food data from CSV file into the database'

    def handle(self, *args, **kwargs):
        # Define path to CSV
        csv_file_path = os.path.join(settings.BASE_DIR, 'static/data/food_nepali_full.csv')
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found at: {csv_file_path}'))
            return

        # Clear existing data
        self.stdout.write('Clearing existing Food data...')
        Food.objects.all().delete()

        self.stdout.write('Loading fresh data...')
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                foods_to_create = []
                
                for row in reader:
                    # Map CSV columns to Model fields
                    # CSV columns: Food_items,Breakfast,Lunch,Dinner,VegNovVeg,Calories,Fats,Proteins,Iron,Calcium,Sodium,Potassium,Carbohydrates,Fibre,VitaminD,Sugars
                    
                    
                    # Logix to find image
                    # Try to find image with same name
                    sanitized_under = row['Food_items'].replace(" ", "_")
                    sanitized_concat = row['Food_items'].replace(" ", "")
                    # Also try removing special chars just in case? No, stick to observed patterns first.
                    
                    potential_images = [
                        f"food/{sanitized_under}.jpg",
                        f"food/{sanitized_under}.png",
                        f"food/{sanitized_concat}.jpg",
                        f"food/{sanitized_concat}.png",
                        f"food2/{sanitized_under}.jpg",
                        f"food2/{sanitized_under}.png",
                        f"food2/{sanitized_concat}.jpg",
                        f"food2/{sanitized_concat}.png",
                        # Try original name if weird casing
                        f"food/{row['Food_items']}.jpg",
                        f"food/{row['Food_items']}.png",
                    ]
                    
                    image_path = "planner.jpg" # Default
                    
                    for img in potential_images:
                        # Check complete path
                        full_path = os.path.join(settings.BASE_DIR, 'static/images', img)
                        if os.path.exists(full_path):
                            image_path = img
                            break
                    
                    food = Food(
                        name=row['Food_items'],
                        bf=int(row['Breakfast']),
                        lu=int(row['Lunch']),
                        di=int(row['Dinner']),
                        cal=float(row['Calories']),
                        fat=float(row['Fats']),
                        pro=float(row['Proteins']),
                        sug=float(row['Sugars']),
                        imagepath=image_path
                    )
                    foods_to_create.append(food)
                
                # Bulk create for performance
                Food.objects.bulk_create(foods_to_create)
                
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(foods_to_create)} food items.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
