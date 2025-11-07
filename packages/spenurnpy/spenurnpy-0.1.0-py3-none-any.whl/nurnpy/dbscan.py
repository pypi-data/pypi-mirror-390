import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def euclidean_distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2))

def region_query(X, point_idx, eps):
    """Return all points within eps distance of point_idx"""
    neighbors = []
    for i in range(len(X)):
        if euclidean_distance(X[point_idx], X[i]) <= eps:
            neighbors.append(i)
    return neighbors

def expand_cluster(X, labels, point_idx, neighbors, cluster_id, eps, min_pts):
    """Expand cluster recursively"""
    labels[point_idx] = cluster_id
    i = 0
    while i < len(neighbors):
        neighbor_idx = neighbors[i]
        if labels[neighbor_idx] == -1:  # previously marked as noise
            labels[neighbor_idx] = cluster_id
        elif labels[neighbor_idx] == 0:  # unvisited
            labels[neighbor_idx] = cluster_id
            new_neighbors = region_query(X, neighbor_idx, eps)
            if len(new_neighbors) >= min_pts:
                neighbors += new_neighbors  # merge neighbors
        i += 1

def dbscan(D, eps, min_pts):
    """
    DBSCAN algorithm
    D: dataset (Pandas DataFrame or NumPy array)
    eps: radius parameter (ϵ)
    min_pts: minimum number of points in neighborhood
    """
    X = np.array(D)
    n = len(X)
    labels = np.zeros(n)  # 0 = unvisited
    cluster_id = 0

    for i in range(n):
        if labels[i] != 0:  # already visited
            continue

        neighbors = region_query(X, i, eps)
        if len(neighbors) < min_pts:
            labels[i] = -1  # mark as noise
        else:
            cluster_id += 1
            expand_cluster(X, labels, i, neighbors, cluster_id, eps, min_pts)

    return labels

# Generate sample dataset
data = pd.DataFrame({
    'X': [1, 2, 2, 8, 8, 25, 24, 25, 50, 51, 52, 80, 81, 82, 83],
    'Y': [2, 2, 3, 8, 9, 25, 26, 24, 50, 51, 52, 80, 81, 83, 82]
})

# Parameters
eps = 3        # radius
min_pts = 2    # minimum neighbors

# Run DBSCAN
labels = dbscan(data, eps, min_pts)

# Display results
data['Cluster'] = labels
print("Cluster assignments:")
print(data)

# Plot clusters
plt.figure(figsize=(7, 5))
colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown']
unique_clusters = set(labels)

for cluster_id in unique_clusters:
    cluster_points = data[data['Cluster'] == cluster_id]
    if cluster_id == -1:
        plt.scatter(cluster_points['X'], cluster_points['Y'], color='gray', label='Noise', marker='x')
    else:
        plt.scatter(cluster_points['X'], cluster_points['Y'],
                    color=colors[int(cluster_id) % len(colors)], label=f'Cluster {int(cluster_id)}')

plt.title('DBSCAN Clustering')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()
