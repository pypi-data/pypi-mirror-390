#1)Apriori
# import pandas as pd
# from itertools import combinations
# 
# def apriori(D, min_sup):
#     # Step 1: Find frequent 1-itemsets
#     item_counts = {}
#     for transaction in D:
#         for item in transaction:
#             item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1
# 
#     # Convert support count threshold to actual count if given as fraction
#     if 0 < min_sup < 1:
#         min_sup = min_sup * len(D)
# 
#     L1 = {item for item, count in item_counts.items() if count >= min_sup}
#     L = [L1]
#     k = 2
# 
#     # Step 2: Iteratively find Lk
#     while True:
#         prev_L = L[-1]
#         Ck = apriori_gen(prev_L, k)
# 
#         # Count support for candidates
#         count_dict = {c: 0 for c in Ck}
#         for t in D:
#             t_set = set(t)
#             for c in Ck:
#                 if c.issubset(t_set):
#                     count_dict[c] += 1
# 
#         # Filter by min_sup
#         Lk = {c for c, count in count_dict.items() if count >= min_sup}
#         if not Lk:
#             break
#         L.append(Lk)
#         k += 1
# 
#     # Combine all frequent itemsets
#     all_freq = set().union(*L)
#     return all_freq
# 
# 
# def apriori_gen(L_prev, k):
#     """Generate candidate k-itemsets from frequent (k-1)-itemsets."""
#     candidates = set()
#     L_prev_list = list(L_prev)
#     for i in range(len(L_prev_list)):
#         for j in range(i + 1, len(L_prev_list)):
#             l1 = sorted(list(L_prev_list[i]))
#             l2 = sorted(list(L_prev_list[j]))
#             if l1[:k - 2] == l2[:k - 2]:
#                 c = frozenset(set(l1) | set(l2))
#                 if not has_infrequent_subset(c, L_prev):
#                     candidates.add(c)
#     return candidates
# 
# 
# def has_infrequent_subset(c, L_prev):
#     """Check if any (k-1)-subset of candidate c is not in L_prev."""
#     for subset in combinations(c, len(c) - 1):
#         if frozenset(subset) not in L_prev:
#             return True
#     return False
# 
# # Sample dataset (list of transactions)
# transactions = [
#     ['milk', 'bread', 'nuts', 'apple'],
#     ['milk', 'bread', 'nuts'],
#     ['milk', 'bread'],
#     ['bread', 'nuts'],
#     ['milk', 'apple'],
#     ['bread', 'apple']
# ]
# 
# # Minimum support = 0.5 (i.e., itemsets must appear in ≥ 50% of transactions)
# min_support = 0.3
# 
# # Run Apriori
# frequent_itemsets = apriori(transactions, min_support)
# 
# print("Frequent Itemsets:")
# for itemset in sorted(frequent_itemsets, key=lambda x: (len(x), sorted(x))):
#     print(list(itemset))


#2)DBSCAN
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# 
# def euclidean_distance(a, b):
#     return np.sqrt(np.sum((a - b) ** 2))
# 
# def region_query(X, point_idx, eps):
#     """Return all points within eps distance of point_idx"""
#     neighbors = []
#     for i in range(len(X)):
#         if euclidean_distance(X[point_idx], X[i]) <= eps:
#             neighbors.append(i)
#     return neighbors
# 
# def expand_cluster(X, labels, point_idx, neighbors, cluster_id, eps, min_pts):
#     """Expand cluster recursively"""
#     labels[point_idx] = cluster_id
#     i = 0
#     while i < len(neighbors):
#         neighbor_idx = neighbors[i]
#         if labels[neighbor_idx] == -1:  # previously marked as noise
#             labels[neighbor_idx] = cluster_id
#         elif labels[neighbor_idx] == 0:  # unvisited
#             labels[neighbor_idx] = cluster_id
#             new_neighbors = region_query(X, neighbor_idx, eps)
#             if len(new_neighbors) >= min_pts:
#                 neighbors += new_neighbors  # merge neighbors
#         i += 1
# 
# def dbscan(D, eps, min_pts):
#     """
#     DBSCAN algorithm
#     D: dataset (Pandas DataFrame or NumPy array)
#     eps: radius parameter (ϵ)
#     min_pts: minimum number of points in neighborhood
#     """
#     X = np.array(D)
#     n = len(X)
#     labels = np.zeros(n)  # 0 = unvisited
#     cluster_id = 0
# 
#     for i in range(n):
#         if labels[i] != 0:  # already visited
#             continue
# 
#         neighbors = region_query(X, i, eps)
#         if len(neighbors) < min_pts:
#             labels[i] = -1  # mark as noise
#         else:
#             cluster_id += 1
#             expand_cluster(X, labels, i, neighbors, cluster_id, eps, min_pts)
# 
#     return labels
# 
# # Generate sample dataset
# data = pd.DataFrame({
#     'X': [1, 2, 2, 8, 8, 25, 24, 25, 50, 51, 52, 80, 81, 82, 83],
#     'Y': [2, 2, 3, 8, 9, 25, 26, 24, 50, 51, 52, 80, 81, 83, 82]
# })
# 
# # Parameters
# eps = 3        # radius
# min_pts = 2    # minimum neighbors
# 
# # Run DBSCAN
# labels = dbscan(data, eps, min_pts)
# 
# # Display results
# data['Cluster'] = labels
# print("Cluster assignments:")
# print(data)
# 
# # Plot clusters
# plt.figure(figsize=(7, 5))
# colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown']
# unique_clusters = set(labels)
# 
# for cluster_id in unique_clusters:
#     cluster_points = data[data['Cluster'] == cluster_id]
#     if cluster_id == -1:
#         plt.scatter(cluster_points['X'], cluster_points['Y'], color='gray', label='Noise', marker='x')
#     else:
#         plt.scatter(cluster_points['X'], cluster_points['Y'],
#                     color=colors[int(cluster_id) % len(colors)], label=f'Cluster {int(cluster_id)}')
# 
# plt.title('DBSCAN Clustering')
# plt.xlabel('X')
# plt.ylabel('Y')
# plt.legend()
# plt.grid(True)
# plt.show()

#3)Decision_Tree
# import pandas as pd
# import numpy as np
# import math
# 
# # --- Helper Functions ---
# 
# def entropy(target_col):
#     """Calculate the entropy of a target column"""
#     elements, counts = np.unique(target_col, return_counts=True)
#     entropy = 0
#     for i in range(len(elements)):
#         prob = counts[i] / np.sum(counts)
#         entropy += -prob * math.log2(prob)
#     return entropy
# 
# 
# def info_gain(data, split_attribute, target_attribute):
#     """Calculate information gain for a given attribute"""
#     total_entropy = entropy(data[target_attribute])
#     vals, counts = np.unique(data[split_attribute], return_counts=True)
#     
#     weighted_entropy = 0
#     for i in range(len(vals)):
#         subset = data[data[split_attribute] == vals[i]]
#         prob = counts[i] / np.sum(counts)
#         weighted_entropy += prob * entropy(subset[target_attribute])
#     
#     info_gain_value = total_entropy - weighted_entropy
#     return info_gain_value
# 
# 
# def majority_class(target_col):
#     """Return the majority class"""
#     return target_col.value_counts().idxmax()
# 
# # --- Core Decision Tree Function ---
# 
# def generate_decision_tree(data, attributes, target_attribute):
#     """Recursively generate a decision tree following the given algorithm"""
#     
#     # Create a new node N
#     node = {}
# 
#     # If all tuples have the same class → leaf node
#     if len(np.unique(data[target_attribute])) == 1:
#         return np.unique(data[target_attribute])[0]
# 
#     # If attribute list empty → leaf node with majority class
#     elif len(attributes) == 0:
#         return majority_class(data[target_attribute])
# 
#     else:
#         # Apply attribute selection method (information gain)
#         gains = [info_gain(data, attr, target_attribute) for attr in attributes]
#         best_attr = attributes[np.argmax(gains)]
#         node['attribute'] = best_attr
#         node['branches'] = {}
# 
#         # Remove the best attribute from further splitting
#         remaining_attrs = [a for a in attributes if a != best_attr]
# 
#         # For each outcome of the splitting attribute
#         for val in np.unique(data[best_attr]):
#             subset = data[data[best_attr] == val]
#             
#             # If subset empty → leaf with majority class
#             if subset.shape[0] == 0:
#                 node['branches'][val] = majority_class(data[target_attribute])
#             else:
#                 # Recursive call
#                 node['branches'][val] = generate_decision_tree(subset, remaining_attrs, target_attribute)
#         
#         return node
# 
# 
# def print_tree(tree, depth=0):
#     """Pretty-print the tree"""
#     if isinstance(tree, dict):
#         attr = tree['attribute']
#         for val, branch in tree['branches'].items():
#             print("\t" * depth + f"├── {attr} = {val}")
#             print_tree(branch, depth + 1)
#     else:
#         print("\t" * depth + f"└── [Class: {tree}]")
#         
#         
# # --- Sample Dataset ---
# # data = pd.DataFrame({
# #     'Outlook': ['Sunny', 'Sunny', 'Overcast', 'Rain', 'Rain', 'Rain', 'Overcast', 'Sunny', 'Sunny', 'Rain', 'Sunny', 'Overcast', 'Overcast', 'Rain'],
# #     'Temperature': ['Hot', 'Hot', 'Hot', 'Mild', 'Cool', 'Cool', 'Cool', 'Mild', 'Cool', 'Mild', 'Mild', 'Mild', 'Hot', 'Mild'],
# #     'Humidity': ['High', 'High', 'High', 'High', 'Normal', 'Normal', 'Normal', 'High', 'Normal', 'Normal', 'Normal', 'High', 'Normal', 'High'],
# #     'Wind': ['Weak', 'Strong', 'Weak', 'Weak', 'Weak', 'Strong', 'Strong', 'Weak', 'Weak', 'Weak', 'Strong', 'Strong', 'Weak', 'Strong'],
# #     'PlayTennis': ['No', 'No', 'Yes', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No']
# # })
# 
# # attributes = ['Outlook', 'Temperature', 'Humidity', 'Wind']
# # target = 'PlayTennis'
# 
# data = pd.read_csv("comp.csv")
# 
# attributes = ['age', 'income', 'student', 'credit_rating']
# target = 'buys'
# 
# # --- Generate Decision Tree ---
# tree = generate_decision_tree(data, attributes, target)
# 
# print("Decision Tree Structure:")
# print_tree(tree)
#     

#4) FpGrowth
# import pandas as pd
# from collections import defaultdict, Counter
# 
# # -------------------- FP-Tree Node Class --------------------
# class FPNode:
#     def __init__(self, name, count, parent):
#         self.name = name
#         self.count = count
#         self.parent = parent
#         self.children = {}
#         self.link = None  # node-link for same item
# 
#     def increment(self, count):
#         self.count += count
# 
# # -------------------- Tree Construction --------------------
# def build_fp_tree(transactions, min_sup):
#     # Step 1: Count frequency of each item
#     item_counts = Counter()
#     for trans in transactions:
#         item_counts.update(trans)
# 
#     # Remove infrequent items
#     item_counts = {item: count for item, count in item_counts.items() if count >= min_sup}
#     if len(item_counts) == 0:
#         return None, None
# 
#     # Sort items by descending frequency
#     items = [item for item, count in sorted(item_counts.items(), key=lambda x: (-x[1], x[0]))]
# 
#     # Header table for node links
#     header_table = {item: [count, None] for item, count in item_counts.items()}
# 
#     # Create root node
#     root = FPNode('null', 1, None)
# 
#     # Insert transactions
#     for trans in transactions:
#         ordered_items = [item for item in items if item in trans]
#         insert_tree(ordered_items, root, header_table)
# 
#     return root, header_table
# 
# 
# def insert_tree(items, node, header_table):
#     if len(items) == 0:
#         return
# 
#     first_item = items[0]
#     if first_item in node.children:
#         node.children[first_item].increment(1)
#     else:
#         new_node = FPNode(first_item, 1, node)
#         node.children[first_item] = new_node
# 
#         # Update header table links
#         update_header(header_table, first_item, new_node)
# 
#     # Recurse for remaining items
#     remaining_items = items[1:]
#     insert_tree(remaining_items, node.children[first_item], header_table)
# 
# 
# def update_header(header_table, item, new_node):
#     # Maintain node-link connections
#     head = header_table[item][1]
#     if head is None:
#         header_table[item][1] = new_node
#     else:
#         while head.link is not None:
#             head = head.link
#         head.link = new_node
# 
# # -------------------- FP-Growth Mining --------------------
# def find_prefix_path(base_pat, node):
#     cond_pats = {}
#     while node is not None:
#         prefix_path = []
#         parent = node.parent
#         while parent is not None and parent.name != 'null':
#             prefix_path.append(parent.name)
#             parent = parent.parent
#         prefix_path.reverse()
#         if len(prefix_path) > 0:
#             cond_pats[frozenset(prefix_path)] = node.count
#         node = node.link
#     return cond_pats
# 
# 
# def mine_tree(header_table, min_sup, prefix, freq_item_list):
#     # Get items in ascending frequency order
#     sorted_items = [item for item, v in sorted(header_table.items(), key=lambda x: x[1][0])]
# 
#     for base_pat in sorted_items:
#         new_freq_set = prefix.copy()
#         new_freq_set.add(base_pat)
#         freq_item_list.append((new_freq_set, header_table[base_pat][0]))
# 
#         cond_patt_bases = find_prefix_path(base_pat, header_table[base_pat][1])
#         cond_tree, cond_header = build_cond_tree(cond_patt_bases, min_sup)
# 
#         if cond_header is not None:
#             mine_tree(cond_header, min_sup, new_freq_set, freq_item_list)
# 
# 
# def build_cond_tree(cond_patt_bases, min_sup):
#     # Build conditional FP-tree from pattern base
#     transactions = []
#     for pattern, count in cond_patt_bases.items():
#         for i in range(count):
#             transactions.append(list(pattern))
#     return build_fp_tree(transactions, min_sup)
# 
# # -------------------- Utility: Tree Printing --------------------
# def print_tree(node, indent=0):
#     print('  ' * indent + f"{node.name} ({node.count})")
#     for child in node.children.values():
#         print_tree(child, indent + 1)
# 
# # Sample transactional dataset
# transactions = [
#     ['milk', 'bread', 'nuts', 'apple'],
#     ['milk', 'bread', 'nuts'],
#     ['milk', 'bread'],
#     ['bread', 'nuts'],
#     ['milk', 'apple'],
#     ['bread', 'apple']
# ]
# 
# min_sup = 2
# 
# # Build FP-tree
# root, header_table = build_fp_tree(transactions, min_sup)
# 
# print("FP-Tree Structure:")
# print_tree(root)
# 
# # Mine frequent patterns
# freq_items = []
# mine_tree(header_table, min_sup, set(), freq_items)
# 
# print("\nFrequent Itemsets:")
# for itemset, support in freq_items:
#     print(f"{list(itemset)}: {support}")

#5)Kmeans
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# 
# def k_means(D, k, max_iters=100):
#     # Convert to numpy array
#     X = np.array(D)
#     n_samples, n_features = X.shape
# 
#     # Step 1: Randomly choose k initial cluster centers
#     np.random.seed(42)
#     random_indices = np.random.choice(n_samples, k, replace=False)
#     centroids = X[random_indices]
# 
#     for iteration in range(max_iters):
#         # Step 2: Assign each point to the nearest centroid
#         clusters = [[] for _ in range(k)]
#         for point in X:
#             distances = [np.linalg.norm(point - c) for c in centroids]
#             cluster_index = np.argmin(distances)
#             clusters[cluster_index].append(point)
# 
#         # Step 3: Store old centroids for convergence check
#         old_centroids = centroids.copy()
# 
#         # Step 4: Update centroids (mean of each cluster)
#         for i in range(k):
#             if len(clusters[i]) > 0:
#                 centroids[i] = np.mean(clusters[i], axis=0)
# 
#         # Step 5: Check if centroids changed (stop condition)
#         if np.allclose(old_centroids, centroids):
#             print(f"Converged after {iteration+1} iterations.")
#             break
# 
#     # Create label assignments
#     labels = []
#     for point in X:
#         distances = [np.linalg.norm(point - c) for c in centroids]
#         labels.append(np.argmin(distances))
# 
#     return np.array(centroids), np.array(labels)
# 
# # Sample dataset (2D points)
# data = pd.DataFrame({
#     'X': [1, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 18, 20, 22, 25, 27],
#     'Y': [60, 65, 63, 70, 75, 80, 82, 85, 88, 90, 92, 95, 96, 97, 98, 99, 99, 100, 100, 100],
#     'Z': [45, 50, 52, 58, 62, 70, 75, 80, 82, 85, 87, 90, 91, 93, 95, 96, 97, 98, 99, 100]
# })
# 
# k = 10  # number of clusters
# 
# # Run K-Means
# centroids, labels = k_means(data, k)
# 
# # Display results
# print("Final Centroids:\n", centroids)
# print("\nCluster Assignments:")
# for i, label in enumerate(labels):
#     print(f"Point {list(data.iloc[i])} → Cluster {label+1}")
# 
# # Visualization
# plt.figure(figsize=(7, 5))
# colors = ['red', 'blue', 'green', 'purple', 'orange', 'teal', 'yellow', 'pink', 'gray', 'brown', 'cyan']
# for i in range(k):
#     cluster_points = data[np.array(labels) == i]
#     plt.scatter(cluster_points['X'], cluster_points['Y'], cluster_points['Z'], color=colors[i], label=f'Cluster {i+1}')
# plt.scatter(centroids[:, 0], centroids[:, 1], color='black', marker='X', s=200, label='Centroids')
# plt.title('K-Means Clustering')
# plt.xlabel('X')
# plt.ylabel('Y')
# plt.legend()
# plt.grid(True)
# plt.show()

#6) Naive Bayes
# import math
# import random
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, precision_score, recall_score, f1_score
# 
# # ----------------------------- Preprocessing -----------------------------
# def encode_class(mydata):
#     classes = []
#     for i in range(len(mydata)):
#         if mydata[i][-1] not in classes:
#             classes.append(mydata[i][-1])
#     for i in range(len(classes)):
#         for j in range(len(mydata)):
#             if mydata[j][-1] == classes[i]:
#                 mydata[j][-1] = i
#     return mydata
# 
# def splitting(mydata, ratio):
#     train_num = int(len(mydata) * ratio)
#     train = []
#     test = list(mydata)
#     
#     while len(train) < train_num:
#         index = random.randrange(len(test))
#         train.append(test.pop(index))
#     return train, test
# 
# def groupUnderClass(mydata):
#     data_dict = {}
#     for i in range(len(mydata)):
#         if mydata[i][-1] not in data_dict:
#             data_dict[mydata[i][-1]] = []
#         data_dict[mydata[i][-1]].append(mydata[i])
#     return data_dict
# 
# def MeanAndStdDev(numbers):
#     avg = np.mean(numbers)
#     stddev = np.std(numbers)
#     return avg, stddev
# 
# def MeanAndStdDevForClass(mydata):
#     info = {}
#     data_dict = groupUnderClass(mydata)
#     for classValue, instances in data_dict.items():
#         # exclude last column (class label) when computing stats
#         info[classValue] = [MeanAndStdDev(attribute) for attribute in zip(*[row[:-1] for row in instances])]
#     return info
# 
# # ----------------------------- Naive Bayes Classifier -----------------------------
# def calculateGaussianProbability(x, mean, stdev):
#     epsilon = 1e-10  # to avoid division by zero
#     expo = math.exp(-(math.pow(x - mean, 2) / (2 * math.pow(stdev + epsilon, 2))))
#     return (1 / (math.sqrt(2 * math.pi) * (stdev + epsilon))) * expo
# 
# def calculateClassProbabilities(info, test):
#     probabilities = {}
#     for classValue, classSummaries in info.items():
#         probabilities[classValue] = 1
#         for i in range(len(classSummaries)):  # only features, label already excluded
#             mean, std_dev = classSummaries[i]
#             x = test[i]
#             probabilities[classValue] *= calculateGaussianProbability(x, mean, std_dev)
#     return probabilities
# 
# def predict(info, test):
#     probabilities = calculateClassProbabilities(info, test)
#     bestLabel = max(probabilities, key=probabilities.get)
#     return bestLabel
# 
# def getPredictions(info, test):
#     predictions = [predict(info, instance) for instance in test]
#     return predictions
# 
# def accuracy_rate(test, predictions):
#     correct = sum(1 for i in range(len(test)) if test[i][-1] == predictions[i])
#     return (correct / float(len(test))) * 100.0
# 
# # ----------------------------- Load and Prepare Data -----------------------------
# filename = 'diabetes_data.csv' 
# df = pd.read_csv(filename, header=0)   # assume first row has column names
# mydata = df.values.tolist()
# 
# # Encode class labels (last column)
# mydata = encode_class(mydata)
#         
# # Split data
# ratio = 0.7
# train_data, test_data = splitting(mydata, ratio)
# 
# print('Total number of examples:', len(mydata))
# print('Training examples:', len(train_data))
# print('Test examples:', len(test_data))
# 
# # ----------------------------- Train & Predict -----------------------------
# info = MeanAndStdDevForClass(train_data)
# predictions = getPredictions(info, test_data)
# 
# # Accuracy
# accuracy = accuracy_rate(test_data, predictions)
# print('Accuracy of the model:', accuracy)
# 
# # ----------------------------- Confusion Matrix -----------------------------
# y_true = [row[-1] for row in test_data]
# y_pred = predictions
# 
# cm = confusion_matrix(y_true, y_pred)
# disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['No Diabetes', 'Diabetes'])
# disp.plot(cmap='Blues')
# plt.title("Confusion Matrix")
# plt.show()
# 
# # ----------------------------- Precision, Recall, F1 -----------------------------
# precision = precision_score(y_true, y_pred)
# recall = recall_score(y_true, y_pred)
# f1 = f1_score(y_true, y_pred)
# 
# metrics = ['Precision', 'Recall', 'F1 Score']
# values = [precision, recall, f1]
# 
# plt.figure(figsize=(6, 4))
# plt.bar(metrics, values, color=['skyblue', 'lightgreen', 'salmon'])
# plt.ylim(0, 1)
# plt.title('Precision, Recall, and F1 Score')
# plt.ylabel('Score')
# 
# # Annotate bars with scores
# for i, v in enumerate(values):
#     plt.text(i, v + 0.02, f"{v:.2f}", ha='center', fontweight='bold')
#     
# plt.show()
# 
# 
#7) Hierarchiacal
# HIERARCHICAL CLUSTERING COMPARISON SCRIPT

# (Agglomerative vs Divisive)
# 
# # ===========================================
# 
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.cluster import AgglomerativeClustering, KMeans
# from scipy.cluster.hierarchy import dendrogram, linkage
# from sklearn.preprocessing import StandardScaler
# from tkinter import Tk, filedialog  # for file dialog
# 
# # -------------------------------------------
# 
# # 1️⃣ Load Dataset (any CSV file)
# 
# # -------------------------------------------
# 
# print("Select your dataset CSV file...")
# Tk().withdraw()  # hide root window
# file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
# if not file_path:
#     raise ValueError("No file selected!")
# 
# df = pd.read_csv(file_path)
# print("\nDataset Loaded Successfully ✅\n")
# print(df.head(), "\n")
# 
# # -------------------------------------------
# 
# # 2️⃣ Preprocessing — Select Numeric Columns
# 
# # -------------------------------------------
# 
# numeric_df = df.select_dtypes(include=[np.number])
# 
# if numeric_df.shape[1] < 2:
#     raise ValueError("Dataset must contain at least 2 numeric columns for clustering.")
# 
# scaler = StandardScaler()
# X = scaler.fit_transform(numeric_df)
# 
# print("Numeric columns used for clustering:", list(numeric_df.columns))
# 
# # -------------------------------------------
# 
# # 3️⃣ Agglomerative Clustering
# 
# # -------------------------------------------
# 
# agg_model = AgglomerativeClustering(n_clusters=3)
# agg_labels = agg_model.fit_predict(X)
# 
# # For dendrogram (distance_threshold=0 disables pre-cut)
# 
# agg_full = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
# agg_full.fit(X)
# 
# # Function to plot dendrogram from model
# 
# def plot_dendrogram(model, **kwargs):
# counts = np.zeros(model.children_.shape[0])
# n_samples = len(model.labels_)
# for i, merge in enumerate(model.children_):
# current_count = 0
# for child_idx in merge:
# if child_idx < n_samples:
# current_count += 1
# else:
# current_count += counts[child_idx - n_samples]
# counts[i] = current_count
# linkage_matrix = np.column_stack(
# [model.children_, model.distances_, counts]).astype(float)
# dendrogram(linkage_matrix, **kwargs)
# 
# # -------------------------------------------
# 
# # 4️⃣ Divisive Clustering (using recursive KMeans)
# 
# # -------------------------------------------
# 
# def divisive_clustering(data, max_clusters=3):
# clusters = [data]
# while len(clusters) < max_clusters:
# cluster_to_split = max(clusters, key=lambda x: len(x))
# clusters.remove(cluster_to_split)
# 
# ```
#     kmeans = KMeans(n_clusters=2, random_state=42).fit(cluster_to_split)
#     c1 = cluster_to_split[kmeans.labels_ == 0]
#     c2 = cluster_to_split[kmeans.labels_ == 1]
# 
#     clusters.extend([c1, c2])
# return clusters
# ```
# 
# div_clusters = divisive_clustering(X, max_clusters=3)
# 
# # -------------------------------------------
# 
# # 5️⃣ Visualization — Comparison
# 
# # -------------------------------------------
# 
# plt.figure(figsize=(14, 6))
# 
# # (a) Agglomerative Scatter
# 
# plt.subplot(1, 2, 1)
# plt.scatter(X[:, 0], X[:, 1], c=agg_labels, cmap='viridis', s=70)
# plt.title("Agglomerative Clustering Result")
# plt.xlabel("Feature 1")
# plt.ylabel("Feature 2")
# 
# # (b) Divisive Scatter
# 
# plt.figure(figsize=(14, 6))
# colors = ['r', 'g', 'b', 'c', 'm', 'y']
# plt.subplot(1, 2, 1)
# for i, cluster in enumerate(div_clusters):
# plt.scatter(cluster[:, 0], cluster[:, 1], s=50,
# c=colors[i], label=f'Cluster {i+1}')
# plt.title('Divisive Clustering Result')
# plt.legend()
# 
# # (c) Dendrogram (Agglomerative)
# 
# plt.subplot(1, 2, 2)
# plot_dendrogram(agg_full, truncate_mode='level', p=5)
# plt.title("Hierarchical Dendrogram (Agglomerative)")
# plt.xlabel("Sample index")
# plt.ylabel("Distance")
# 
# plt.tight_layout()
# plt.show()
# 


