import os
import django
import sys

# Setup Django environment
sys.path.append("c:\\Users\\Dell\\Documents\\clone2 - Copy\\Diet_recommendation_system\\Diet recommendation system\\Diet_recommendation_system")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodrec.settings')
django.setup()

from recommender.functions import recommender, Weight_Loss, Weight_Gain

print("Testing Recommendation Logic...")

# Force train
recommender._train_model()

print(f"\nClusters identified:")
print(f"Loss Cluster: {recommender.loss_cluster}")
print(f"Gain Cluster: {recommender.gain_cluster}")
print(f"Healthy Cluster: {recommender.healthy_cluster}")

# Test Weight Loss
print("\n--- Testing Weight Loss (Simulated View Logic) ---")
loss_bf = recommender.get_recommendations('breakfast', recommender.loss_cluster)[:3]
print(f"Weight Loss Breakfast Recommendations:")
for food in loss_bf:
    print(f" - {food.name} (Cal: {food.cal}, Fat: {food.fat})")

# Test Weight Gain
print("\n--- Testing Weight Gain (Simulated View Logic) ---")
gain_lu = recommender.get_recommendations('lunch', recommender.gain_cluster)[:3]
print(f"Weight Gain Lunch Recommendations:")
for food in gain_lu:
    print(f" - {food.name} (Cal: {food.cal}, Pro: {food.pro})")

print("\nVerify complete.")
