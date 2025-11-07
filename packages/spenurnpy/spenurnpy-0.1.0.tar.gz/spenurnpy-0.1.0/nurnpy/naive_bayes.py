import numpy as np
import pandas as pd

# ---------------- Sample Dataset ----------------
data = pd.DataFrame({
    'Height': [180, 160, 170, 175, 165, 155, 172, 168],
    'Weight': [80, 55, 65, 75, 60, 50, 68, 62],
    'HairColor': ['Black', 'Blonde', 'Brown', 'Black', 'Blonde', 'Blonde', 'Brown', 'Brown'],
    'Gender': ['Male', 'Female', 'Male', 'Male', 'Female', 'Female', 'Male', 'Female']
})

# ---------------- Naive Bayes Implementation ----------------
class MixedNaiveBayes:
    def __init__(self):
        self.classes = None
        self.cont_means = {}
        self.cont_stds = {}
        self.cat_probs = {}
        self.priors = {}

    def fit(self, X, y, categorical_features=[]):
        self.classes = np.unique(y)
        self.categorical_features = categorical_features
        self.continuous_features = [f for f in X.columns if f not in categorical_features]

        for c in self.classes:
            X_c = X[y == c]
            self.priors[c] = X_c.shape[0] / X.shape[0]

            # Continuous features
            self.cont_means[c] = X_c[self.continuous_features].mean()
            self.cont_stds[c] = X_c[self.continuous_features].std()

            # Categorical features
            self.cat_probs[c] = {}
            for f in categorical_features:
                counts = X_c[f].value_counts()
                total = X_c.shape[0]
                self.cat_probs[c][f] = (counts + 1) / (total + len(X[f].unique()))

    def _gaussian_pdf(self, x, mean, std):
        eps = 1e-6
        coeff = 1.0 / (np.sqrt(2 * np.pi) * (std + eps))
        exponent = np.exp(- ((x - mean) ** 2) / (2 * (std + eps) ** 2))
        return coeff * exponent

    def predict(self, X):
        y_pred = []
        for _, x in X.iterrows():
            posteriors = {}
            for c in self.classes:
                posterior = np.log(self.priors[c])
                for f in self.continuous_features:
                    posterior += np.log(self._gaussian_pdf(x[f], self.cont_means[c][f], self.cont_stds[c][f]))
                for f in self.categorical_features:
                    value = x[f]
                    prob = self.cat_probs[c][f].get(value, 1e-6)  # small prob if unseen
                    posterior += np.log(prob)
                posteriors[c] = posterior
            y_pred.append(max(posteriors, key=posteriors.get))
        return np.array(y_pred)

# ---------------- Train ----------------
X = data[['Height', 'Weight', 'HairColor']]
y = data['Gender']
categorical_features = ['HairColor']

nb = MixedNaiveBayes()
nb.fit(X, y, categorical_features=categorical_features)

# ---------------- Test on New Data ----------------
test_data = pd.DataFrame({
    'Height': [178, 162, 169, 158],
    'Weight': [78, 57, 66, 52],
    'HairColor': ['Black', 'Blonde', 'Brown', 'Blonde']
})
test_labels = ['Male', 'Female', 'Male', 'Female']

predictions = nb.predict(test_data)
print("Predictions:", predictions)
print("Actual:", test_labels)

# ---------------- Evaluation Metrics ----------------
def evaluate(y_true, y_pred, classes):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    metrics = {}
    
    # Accuracy
    metrics['accuracy'] = np.sum(y_true == y_pred) / len(y_true)
    
    for cls in classes:
        TP = np.sum((y_true == cls) & (y_pred == cls))
        FP = np.sum((y_true != cls) & (y_pred == cls))
        FN = np.sum((y_true == cls) & (y_pred != cls))
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        metrics[cls] = {'precision': precision, 'recall': recall, 'f1-score': f1}
    
    return metrics

metrics = evaluate(test_labels, predictions, nb.classes)
print("\nEvaluation Metrics:")
print(metrics)
