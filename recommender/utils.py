import numpy as np

class KMeans:
    def __init__(self, k=3, max_iter=100):
        self.k = k
        self.max_iter = max_iter
        self.centroids = None
        
    def fit(self, X):
        # Initialize centroids randomly
        n_samples, n_features = X.shape
        self.centroids = np.random.rand(self.k, n_features)
        
        # Run k-means algorithm
        for i in range(self.max_iter):
            # Assign each data point to the nearest centroid
            distances = np.sqrt(((X - self.centroids[:, np.newaxis])**2).sum(axis=2))
            distances[~np.isfinite(distances)] = np.inf
            labels = np.argmin(distances, axis=0)
            
            # Update each centroid as the mean of all data points assigned to it
            for j in range(self.k):
                if np.sum(labels == j) == 0:
                    continue
                self.centroids[j] = np.mean(X[labels == j], axis=0)
    
    def predict(self, X):
        distances = np.sqrt(((X - self.centroids[:, np.newaxis])**2).sum(axis=2))
        labels = np.argmin(distances, axis=0)
        return labels
        
