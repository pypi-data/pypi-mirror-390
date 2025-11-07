import pandas as pd
import numpy as np
import math

# --- Helper Functions ---

def entropy(target_col):
    """Calculate the entropy of a target column"""
    elements, counts = np.unique(target_col, return_counts=True)
    entropy = 0
    for i in range(len(elements)):
        prob = counts[i] / np.sum(counts)
        entropy += -prob * math.log2(prob)
    return entropy


def info_gain(data, split_attribute, target_attribute):
    """Calculate information gain for a given attribute"""
    total_entropy = entropy(data[target_attribute])
    vals, counts = np.unique(data[split_attribute], return_counts=True)
    
    weighted_entropy = 0
    for i in range(len(vals)):
        subset = data[data[split_attribute] == vals[i]]
        prob = counts[i] / np.sum(counts)
        weighted_entropy += prob * entropy(subset[target_attribute])
    
    info_gain_value = total_entropy - weighted_entropy
    return info_gain_value


def majority_class(target_col):
    """Return the majority class"""
    return target_col.value_counts().idxmax()

# --- Core Decision Tree Function ---

def generate_decision_tree(data, attributes, target_attribute):
    """Recursively generate a decision tree following the given algorithm"""
    
    # Create a new node N
    node = {}

    # If all tuples have the same class → leaf node
    if len(np.unique(data[target_attribute])) == 1:
        return np.unique(data[target_attribute])[0]

    # If attribute list empty → leaf node with majority class
    elif len(attributes) == 0:
        return majority_class(data[target_attribute])

    else:
        # Apply attribute selection method (information gain)
        gains = [info_gain(data, attr, target_attribute) for attr in attributes]
        best_attr = attributes[np.argmax(gains)]
        node['attribute'] = best_attr
        node['branches'] = {}

        # Remove the best attribute from further splitting
        remaining_attrs = [a for a in attributes if a != best_attr]

        # For each outcome of the splitting attribute
        for val in np.unique(data[best_attr]):
            subset = data[data[best_attr] == val]
            
            # If subset empty → leaf with majority class
            if subset.shape[0] == 0:
                node['branches'][val] = majority_class(data[target_attribute])
            else:
                # Recursive call
                node['branches'][val] = generate_decision_tree(subset, remaining_attrs, target_attribute)
        
        return node


def print_tree(tree, depth=0):
    """Pretty-print the tree"""
    if isinstance(tree, dict):
        attr = tree['attribute']
        for val, branch in tree['branches'].items():
            print("\t" * depth + f"├── {attr} = {val}")
            print_tree(branch, depth + 1)
    else:
        print("\t" * depth + f"└── [Class: {tree}]")
        
        
# --- Sample Dataset ---
# data = pd.DataFrame({
#     'Outlook': ['Sunny', 'Sunny', 'Overcast', 'Rain', 'Rain', 'Rain', 'Overcast', 'Sunny', 'Sunny', 'Rain', 'Sunny', 'Overcast', 'Overcast', 'Rain'],
#     'Temperature': ['Hot', 'Hot', 'Hot', 'Mild', 'Cool', 'Cool', 'Cool', 'Mild', 'Cool', 'Mild', 'Mild', 'Mild', 'Hot', 'Mild'],
#     'Humidity': ['High', 'High', 'High', 'High', 'Normal', 'Normal', 'Normal', 'High', 'Normal', 'Normal', 'Normal', 'High', 'Normal', 'High'],
#     'Wind': ['Weak', 'Strong', 'Weak', 'Weak', 'Weak', 'Strong', 'Strong', 'Weak', 'Weak', 'Weak', 'Strong', 'Strong', 'Weak', 'Strong'],
#     'PlayTennis': ['No', 'No', 'Yes', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No']
# })

# attributes = ['Outlook', 'Temperature', 'Humidity', 'Wind']
# target = 'PlayTennis'

data = pd.read_csv("comp.csv")

attributes = ['age', 'income', 'student', 'credit_rating']
target = 'buys'

# --- Generate Decision Tree ---
tree = generate_decision_tree(data, attributes, target)

print("Decision Tree Structure:")
print_tree(tree)
    
