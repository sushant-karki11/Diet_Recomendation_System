import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from recommender.models import Food

# ---------------- CORE ML ENGINE ----------------
class DietRecommender:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.kmeans = None
        self.food_data = None
        self.food_ids = None
        self.labels = None
        
        # Initialize model immediately
        self._train_model()
        
    def _train_model(self):
        """
        Fetches data from DB and trains KMeans model.
        Clusters foods based on: Calories, Fat, Protein, Sugar
        """
        try:
            foods = Food.objects.all()
            if not foods.exists():
                print("WARNING: No food data found in database.")
                return

            # Prepare data frame for training
            data = list(foods.values('id', 'cal', 'fat', 'pro', 'sug'))
            df = pd.DataFrame(data)
            
            self.food_ids = df['id'].values
            
            # Features for clustering
            X = df[['cal', 'fat', 'pro', 'sug']].values
            
            # Train KMeans
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
            self.labels = self.kmeans.fit_predict(X)
            
            # Analyze clusters to determine which is which
            # We want to identify:
            # - Cluster with Low Cal/Fat (Weight Loss)
            # - Cluster with High Protein/Cal (Weight Gain)
            # - Cluster with Balanced stats (Healthy)
            
            cluster_stats = []
            for i in range(self.n_clusters):
                center = self.kmeans.cluster_centers_[i]
                # center index: 0=cal, 1=fat, 2=pro, 3=sug
                cluster_stats.append({
                    'cluster_id': i,
                    'cal': center[0],
                    'pro': center[2],
                    'fat': center[1]
                })
            
            # Sort by Calories to find Weight Loss (Lowest Cal)
            sorted_by_cal = sorted(cluster_stats, key=lambda x: x['cal'])
            self.loss_cluster = sorted_by_cal[0]['cluster_id']
            
            # Sort by Protein * Cal to find Weight Gain (Highest nutrient density)
            sorted_by_gain = sorted(cluster_stats, key=lambda x: x['pro'] * x['cal'], reverse=True)
            self.gain_cluster = sorted_by_gain[0]['cluster_id']
            
            # Healthy is whatever is left, or the middle one
            self.healthy_cluster = sorted_by_cal[1]['cluster_id'] if self.n_clusters >= 3 else self.loss_cluster
            
            print(f"Model Trained. Loss Cluster: {self.loss_cluster}, Gain Cluster: {self.gain_cluster}, Healthy Cluster: {self.healthy_cluster}")
            
        except Exception as e:
            print(f"Error training model: {e}")

    def get_recommendations(self, meal_type, goal_cluster):
        """
        Get food items belonging to a specific cluster and meal type.
        """
        if self.kmeans is None:
            self._train_model()
            
        if self.labels is None:
            return Food.objects.none()
            
        # identifying indices of foods in the target cluster
        target_indices = np.where(self.labels == goal_cluster)[0]
        target_food_ids = self.food_ids[target_indices].tolist()
        
        # Filter by meal type in DB
        qs = Food.objects.filter(id__in=target_food_ids)
        
        if meal_type == 'breakfast':
            return qs.filter(bf=1)
        elif meal_type == 'lunch':
            return qs.filter(lu=1)
        elif meal_type == 'dinner':
            return qs.filter(di=1)
            
        return qs


# Global instance to avoid retraining on every request
# In production, this might be handled differently (e.g. cache or startup script)
recommender = DietRecommender()


# ---------------- UTILS ----------------
def get_bmi_class(bmi):
    if bmi < 18.5: return "Underweight"
    elif 18.5 <= bmi < 24.9: return "Healthy"
    elif 25 <= bmi < 29.9: return "Overweight"
    else: return "Obese"

def calculate_bmi(weight, height_m):
    return weight / (height_m ** 2)


# ---------------- INTERFACE FUNCTIONS ----------------
# These replace the old functions but return QuerySets instead of mixed lists

def Weight_Loss(age, weight, height):
    """
    Returns (breakfast, lunch, dinner, bmi, bmi_info)
    """
    bmi = calculate_bmi(weight, height)
    bmi_info = get_bmi_class(bmi)
    
    # Use the Loss Cluster for all meals
    bf = recommender.get_recommendations(meal_type='breakfast', goal_cluster=recommender.loss_cluster)
    lu = recommender.get_recommendations(meal_type='lunch', goal_cluster=recommender.loss_cluster)
    di = recommender.get_recommendations(meal_type='dinner', goal_cluster=recommender.loss_cluster)
    
    return bf.order_by('?')[:5], lu.order_by('?')[:5], di.order_by('?')[:5], bmi, bmi_info

def Weight_Gain(age, weight, height):
    """
    Returns (breakfast, lunch, dinner, bmi, bmi_info)
    """
    bmi = calculate_bmi(weight, height)
    bmi_info = get_bmi_class(bmi)
    
    # Use the Gain Cluster for all meals
    bf = recommender.get_recommendations(meal_type='breakfast', goal_cluster=recommender.gain_cluster)
    lu = recommender.get_recommendations(meal_type='lunch', goal_cluster=recommender.gain_cluster)
    di = recommender.get_recommendations(meal_type='dinner', goal_cluster=recommender.gain_cluster)
    
    return bf.order_by('?')[:5], lu.order_by('?')[:5], di.order_by('?')[:5], bmi, bmi_info

def Healthy(age, weight, height):
    """
    Returns (breakfast, lunch, dinner, bmi, bmi_info)
    """
    bmi = calculate_bmi(weight, height)
    bmi_info = get_bmi_class(bmi)
    
    # Use the Healthy Cluster for all meals
    bf = recommender.get_recommendations(meal_type='breakfast', goal_cluster=recommender.healthy_cluster)
    lu = recommender.get_recommendations(meal_type='lunch', goal_cluster=recommender.healthy_cluster)
    di = recommender.get_recommendations(meal_type='dinner', goal_cluster=recommender.healthy_cluster)
    
    return bf.order_by('?')[:5], lu.order_by('?')[:5], di.order_by('?')[:5], bmi, bmi_info
