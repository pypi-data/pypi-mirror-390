import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def k_means(D, k, max_iters=100):
    # Convert to numpy array
    X = np.array(D)
    n_samples, n_features = X.shape

    # Step 1: Randomly choose k initial cluster centers
    np.random.seed(42)
    random_indices = np.random.choice(n_samples, k, replace=False)
    centroids = X[random_indices]

    for iteration in range(max_iters):
        # Step 2: Assign each point to the nearest centroid
        clusters = [[] for _ in range(k)]
        for point in X:
            distances = [np.linalg.norm(point - c) for c in centroids]
            cluster_index = np.argmin(distances)
            clusters[cluster_index].append(point)

        # Step 3: Store old centroids for convergence check
        old_centroids = centroids.copy()

        # Step 4: Update centroids (mean of each cluster)
        for i in range(k):
            if len(clusters[i]) > 0:
                centroids[i] = np.mean(clusters[i], axis=0)

        # Step 5: Check if centroids changed (stop condition)
        if np.allclose(old_centroids, centroids):
            print(f"Converged after {iteration+1} iterations.")
            break

    # Create label assignments
    labels = []
    for point in X:
        distances = [np.linalg.norm(point - c) for c in centroids]
        labels.append(np.argmin(distances))

    return np.array(centroids), np.array(labels)

# Sample dataset (2D points)
data = pd.DataFrame({
    'X': [1, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 18, 20, 22, 25, 27],
    'Y': [60, 65, 63, 70, 75, 80, 82, 85, 88, 90, 92, 95, 96, 97, 98, 99, 99, 100, 100, 100],
    'Z': [45, 50, 52, 58, 62, 70, 75, 80, 82, 85, 87, 90, 91, 93, 95, 96, 97, 98, 99, 100]
})

k = 10  # number of clusters

# Run K-Means
centroids, labels = k_means(data, k)

# Display results
print("Final Centroids:\n", centroids)
print("\nCluster Assignments:")
for i, label in enumerate(labels):
    print(f"Point {list(data.iloc[i])} → Cluster {label+1}")

# Visualization
plt.figure(figsize=(7, 5))
colors = ['red', 'blue', 'green', 'purple', 'orange', 'teal', 'yellow', 'pink', 'gray', 'brown', 'cyan']
for i in range(k):
    cluster_points = data[np.array(labels) == i]
    plt.scatter(cluster_points['X'], cluster_points['Y'], cluster_points['Z'], color=colors[i], label=f'Cluster {i+1}')
plt.scatter(centroids[:, 0], centroids[:, 1], color='black', marker='X', s=200, label='Centroids')
plt.title('K-Means Clustering')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()
