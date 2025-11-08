def show():
    print(r"""

prac 1a

# Import necessary libraries
import pandas as pd
from scipy import stats

# Load the dataset
df = pd.read_csv('Social_Network_Ads.csv')

# Check for missing values
print("Missing values before cleaning:")
print(df.isnull().sum())

# -------------------------------
# Handle Missing Values
# -------------------------------

# Numeric columns: fill missing values with mean
numeric_cols = df.select_dtypes(include=['number']).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# Categorical columns: fill missing values with mode
categorical_cols = df.select_dtypes(include=['object']).columns
for column in categorical_cols:
    df[column].fillna(df[column].mode()[0], inplace=True)

# -------------------------------
# Format & Standardize Data
# -------------------------------

print("\nData types before formatting:")
print(df.dtypes)

# Convert string columns to lowercase and remove extra spaces
for column in categorical_cols:
    df[column] = df[column].str.lower().str.strip()

# -------------------------------
# Handle Outliers (IQR Method)
# -------------------------------

for column in numeric_cols:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# -------------------------------
# Final Review
# -------------------------------

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nData types after formatting:")
print(df.dtypes)

print("\nFinal dataset shape:", df.shape)

print("\nCleaned DataFrame:")
print(df.head())

# Optional: Summary statistics for numeric columns
print("\nSummary Statistics:")
print(df.describe())


prac1b

# Import necessary libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Load the Dataset
titanic = sns.load_dataset('titanic')

# Display the first few rows of the dataset
print("First few rows of the dataset:")
print(titanic.head())

# Step 2: Calculate Descriptive Summary Statistics
summary_statistics = titanic.describe(include='all')  # Include all columns for summary
print("\nDescriptive Summary Statistics:")
print(summary_statistics)

# Step 3: Univariate Graphs
plt.figure(figsize=(12, 8))

# Histogram for Age
plt.subplot(2, 2, 1)
sns.histplot(titanic['age'].dropna(), bins=15, kde=True)
plt.title('Distribution of Age')

# Countplot for Survival
plt.subplot(2, 2, 2)
sns.countplot(x='survived', data=titanic)
plt.title('Count of Survival (0 = No, 1 = Yes)')

# Countplot for Pclass
plt.subplot(2, 2, 3)
sns.countplot(x='pclass', data=titanic)
plt.title('Count of Passengers by Class')

# Box plot for Fare by Survival
plt.subplot(2, 2, 4)
sns.boxplot(x='survived', y='fare', data=titanic)
plt.title('Fare by Survival Status')

plt.tight_layout()
plt.show()

# Step 4: Bivariate Graphs

# 4.1 Scatter Plot of Age vs Fare
plt.figure(figsize=(10, 6))
sns.scatterplot(data=titanic, x='age', y='fare', hue='survived', alpha=0.6)
plt.title('Age vs Fare by Survival Status')
plt.show()

# 4.2 Pair Plot
sns.pairplot(titanic, hue='survived', diag_kind='kde')
plt.show()

# 4.3 Box Plot for Age by Survival
plt.figure(figsize=(10, 6))
sns.boxplot(x='survived', y='age', data=titanic)
plt.title('Age by Survival Status')
plt.show()

# Step 5: Identify Potential Features and Target Variables
features = ['pclass', 'sex', 'age', 'fare', 'sibsp', 'parch', 'embarked']  # Potential features
target = 'survived'  # Target variable

print("\nPotential Features:", features)
print("Target Variable:", target)

prac1c

# Import necessary libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler, Binarizer

# Step 1: Create a Synthetic Dataset
np.random.seed(42)

# Generating a DataFrame
data = {
    'age': np.random.randint(18, 70, size=100),
    'income': np.random.randint(20000, 120000, size=100),
    'gender': np.random.choice(['male', 'female'], size=100),
    'purchased': np.random.choice(['yes', 'no'], size=100)
}

df = pd.DataFrame(data)

# Display the first few rows of the dataset
print("First few rows of the dataset:")
print(df.head())

# Step 2: Explore the Dataset
print("\nDescriptive Statistics:")
print(df.describe(include='all'))

# Visualize the distribution of age and income
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(df['age'], bins=15, kde=True)
plt.title('Age Distribution')

plt.subplot(1, 2, 2)
sns.histplot(df['income'], bins=15, kde=True)
plt.title('Income Distribution')

plt.tight_layout()
plt.show()

# Step 3: Preprocess the Data
# 3.1 Label Encoding
label_encoder = LabelEncoder()
df['gender_encoded'] = label_encoder.fit_transform(df['gender'])
df['purchased_encoded'] = label_encoder.fit_transform(df['purchased'])

print("\nData after Label Encoding:")
print(df[['gender', 'gender_encoded', 'purchased', 'purchased_encoded']].head())

# 3.2 Scaling
scaler = StandardScaler()
df[['age_scaled', 'income_scaled']] = scaler.fit_transform(df[['age', 'income']])

print("\nData after Scaling:")
print(df[['age', 'income', 'age_scaled', 'income_scaled']].head())

# 3.3 Binarization
binarizer = Binarizer(threshold=50000)  # 1 if income > 50000, else 0
df['income_binarized'] = binarizer.fit_transform(df[['income']])

print("\nData after Binarization:")
print(df[['income', 'income_binarized']].head())

# Step 4: Final Output
print("\nFinal DataFrame:")
print(df.head())

prac1d


# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# Set random seed for reproducibility
np.random.seed(2)

# Generate synthetic data
x = np.random.normal(3, 1, 100)
y = np.random.normal(156, 40, 100) / x

# Step 1: Scatter Plot of the Data
plt.scatter(x, y)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Scatter Plot of X vs Y")
plt.show()

# Step 2: Split the Data (Manual Split)
train_x = x[:80]
train_y = y[:80]
test_x = x[80:]
test_y = y[80:]

# Plot training data
plt.scatter(train_x, train_y)
plt.xlabel("train_x")
plt.ylabel("train_y")
plt.title("Training Data Scatter Plot (Manual Split)")
plt.show()

# Step 3: Split the Data (Using sklearn)
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3)

# Plot test data
plt.scatter(test_x, test_y)
plt.xlabel("test_x")
plt.ylabel("test_y")
plt.title("Test Data Scatter Plot (sklearn Split)")
plt.show()

# Step 4: Fit Polynomial Regression Model (Degree 4)
mymodel = np.poly1d(np.polyfit(train_x, train_y, 4))
myline = np.linspace(0, 6, 100)

# Plot regression line on training data
plt.scatter(train_x, train_y)
plt.plot(myline, mymodel(myline), color='red')
plt.xlabel("train_x")
plt.ylabel("train_y")
plt.title("Polynomial Regression Fit on Training Data")
plt.show()

# Step 5: Evaluate Model using R² Score
r2 = r2_score(test_y, mymodel(test_x))
print("R² Score on Test Data:", r2)

prac2a


import csv

# Step 1: Create a sample dataset with 6 attributes + class label
header = ['Sky', 'Temperature', 'Humidity', 'Wind', 'Water', 'Forecast', 'Play']

data = [
    ['Sunny', 'Warm', 'Normal', 'Strong', 'Warm', 'Same', 'Yes'],
    ['Sunny', 'Warm', 'High', 'Strong', 'Warm', 'Same', 'Yes'],
    ['Rainy', 'Cold', 'High', 'Strong', 'Warm', 'Change', 'No'],
    ['Sunny', 'Warm', 'High', 'Strong', 'Cool', 'Change', 'Yes']
]

# Step 2: Write dataset to CSV file
with open('training_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

print("✅ Dataset 'training_data.csv' created successfully.")

# Step 3: Read the dataset
num_attributes = 6
a = []

print("\n📘 The Given Training Data Set:\n")

with open('training_data.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    count = 0
    for row in reader:
        if count == 0:
            print(row)   # Print header
            count += 1
        else:
            a.append(row)
            print(row)

# Step 4: Initialize hypothesis
print("\nThe initial value of hypothesis:")
hypothesis = ['0'] * num_attributes
print(hypothesis)

# Step 5: Initialize with first positive example
for j in range(num_attributes):
    hypothesis[j] = a[0][j]

print("\nInitial Hypothesis after first positive example:")
print(hypothesis)

# Step 6: Find-S Algorithm
print("\nFind-S: Finding the Maximally Specific Hypothesis\n")

for i in range(1, len(a)):
    if a[i][num_attributes].lower() == 'yes':  # if the example is positive
        for j in range(num_attributes):
            if a[i][j] != hypothesis[j]:
                hypothesis[j] = '?'  # generalize
    print(f"After training example {i+1}, hypothesis is: {hypothesis}")

print("\n✅ The Maximally Specific Hypothesis:")
print(hypothesis)
prac3a

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Step 1: Create the dataset
X = np.array([5, 15, 25, 35, 45, 55]).reshape(-1, 1)  # independent variable (feature)
y = np.array([5, 20, 14, 32, 22, 38])                # dependent variable (target)

# Step 2: Create and train the Linear Regression model
model = LinearRegression()
model.fit(X, y)

# Step 3: Extract model parameters
intercept = model.intercept_
coefficient = model.coef_[0]

print(f"Intercept (b0): {intercept:.3f}")
print(f"Coefficient (b1): {coefficient:.3f}")

# Step 4: Make predictions
y_pred = model.predict(X)
print("Predictions:", y_pred)

# Step 5: Evaluate the model
r2 = r2_score(y, y_pred)
mse = mean_squared_error(y, y_pred)

print(f"R-squared: {r2:.3f}")
print(f"MSE: {mse:.3f}")

# Step 6: Plot the results
plt.scatter(X, y, color='blue', label='Actual data')
plt.plot(X, y_pred, color='red', label='Regression line')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Simple Linear Regression Fit')
plt.legend()
plt.show()

prac3b

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import RFE
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm

# Step 1: Load the California Housing dataset
data = fetch_california_housing()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target)

# Step 2: Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0
)

# Step 3: Train the Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Step 4: Display coefficients and intercept
print("\nIntercept:", model.intercept_)
print("\nCoefficients:")
for name, coef in zip(X.columns, model.coef_):
    print(f"{name}: {coef:.4f}")

# Step 5: Evaluate model performance
y_pred = model.predict(X_test)
print("\nModel Performance:")
print(f"R-squared: {r2_score(y_test, y_pred):.4f}")
print(f"MSE: {mean_squared_error(y_test, y_pred):.4f}")

# Step 6: Recursive Feature Elimination (RFE)
rfe = RFE(estimator=LinearRegression(), n_features_to_select=3)
rfe.fit(X_train, y_train)
selected_features = X.columns[rfe.support_]
print("\nSelected features by RFE:", list(selected_features))

# Step 7: Check Multicollinearity using VIF
X_const = sm.add_constant(X_train)
vif_data = pd.DataFrame({
    "feature": X_const.columns,
    "VIF": [variance_inflation_factor(X_const.values, i)
            for i in range(X_const.shape[1])]
})
print("\nVariance Inflation Factors (VIF):")
print(vif_data)
prac 3c

# Import necessary libraries
import numpy as np
import pandas as pd
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Step 1: Create synthetic regression data
X, y = make_regression(
    n_samples=200,
    n_features=10,
    noise=10,
    random_state=42
)

# Step 2: Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Step 3: Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 4: Initialize models
ridge = Ridge(alpha=1.0)
lasso = Lasso(alpha=0.1)
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)

# Step 5: Train models
ridge.fit(X_train_scaled, y_train)
lasso.fit(X_train_scaled, y_train)
elastic.fit(X_train_scaled, y_train)

# Step 6: Make predictions
ridge_pred = ridge.predict(X_test_scaled)
lasso_pred = lasso.predict(X_test_scaled)
elastic_pred = elastic.predict(X_test_scaled)

# Step 7: Evaluate models
print("Model Performance:\n")
print(f"Ridge:   R² = {r2_score(y_test, ridge_pred):.4f}, MSE = {mean_squared_error(y_test, ridge_pred):.4f}")
print(f"Lasso:   R² = {r2_score(y_test, lasso_pred):.4f}, MSE = {mean_squared_error(y_test, lasso_pred):.4f}")
print(f"Elastic: R² = {r2_score(y_test, elastic_pred):.4f}, MSE = {mean_squared_error(y_test, elastic_pred):.4f}")

# Step 8: Plot coefficient comparison
plt.figure(figsize=(10, 6))
plt.plot(ridge.coef_, 'o-', label="Ridge")
plt.plot(lasso.coef_, 's-', label="Lasso")
plt.plot(elastic.coef_, '^-', label="ElasticNet")
plt.xlabel("Feature Index")
plt.ylabel("Coefficient Value")
plt.title("Model Coefficients Comparison")
plt.legend()
plt.show()
prac4a logistic regression

# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_curve, auc, precision_recall_curve
)

# 1. Generate a synthetic binary classification dataset
X, y = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=2,
    n_redundant=10,
    n_classes=2,
    random_state=42
)

# 2. Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 3. Fit Logistic Regression Model
model = LogisticRegression(solver='lbfgs', max_iter=1000)
model.fit(X_train, y_train)

# 4. Predict class and probabilities
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]  # Probability for positive class

# 5. Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")

# 6. ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(7, 5))
plt.plot(fpr, tpr, label=f'Logistic Regression (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate (Recall)')
plt.title('ROC Curve')
plt.legend()
plt.grid(True)
plt.show()

# 7. Precision-Recall Curve
precision_vals, recall_vals, thresholds_pr = precision_recall_curve(y_test, y_proba)

plt.figure(figsize=(7, 5))
plt.plot(recall_vals, precision_vals, label='Precision-Recall Curve', color='orange')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()
plt.grid(True)
plt.show()
 prac 4b k nearest

# K-Nearest Neighbors Classification Example

# Import required libraries
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

# 1. Load a sample dataset (Iris dataset for demonstration)
iris = load_iris()
X = iris.data      # Features
y = iris.target    # Labels
target_names = iris.target_names

# 2. Split into train (70%) and test (30%) sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 3. Create and train k-NN model
k = 5
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train, y_train)

# 4. Predict the test data
y_pred = knn.predict(X_test)

# 5. Print correct and wrong predictions
print("Test Predictions:\n")
for i in range(len(y_test)):
    true_class = target_names[y_test[i]]
    predicted_class = target_names[y_pred[i]]
    status = "CORRECT" if y_test[i] == y_pred[i] else "WRONG"
    print(f"Sample {i+1}: True = {true_class}, Predicted = {predicted_class} --> {status}")

# 6. Print accuracy
accuracy = knn.score(X_test, y_test)
print(f"\n✅ Overall Model Accuracy: {accuracy:.2f}")
prac4c decision tree

# Decision Tree Classifier and Regressor Example

# Import required libraries
from sklearn.datasets import load_iris, make_regression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree
from sklearn.metrics import accuracy_score, mean_squared_error
import matplotlib.pyplot as plt

# -----------------------------
# 🔹 Decision Tree Classifier
# -----------------------------

# 1. Load dataset
iris = load_iris()
X, y = iris.data, iris.target

# 2. Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 3. Build classifier (limit tree depth to control overfitting)
clf = DecisionTreeClassifier(max_depth=3, random_state=0)
clf.fit(X_train, y_train)

# 4. Predict and evaluate
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Classifier Accuracy: {acc:.2f}")

# 5. Visualize the classifier tree
plt.figure(figsize=(12, 6))
plot_tree(
    clf,
    feature_names=iris.feature_names,
    class_names=iris.target_names,
    filled=True
)
plt.title("Decision Tree Classifier (max_depth=3)")
plt.show()


# -----------------------------
# 🔹 Decision Tree Regressor
# -----------------------------

# 6. Generate regression data
Xr, yr = make_regression(
    n_samples=200,
    n_features=1,
    noise=15,
    random_state=0
)

# 7. Split into train and test sets
Xr_train, Xr_test, yr_train, yr_test = train_test_split(
    Xr, yr, test_size=0.3, random_state=42
)

# 8. Build regressor (limit tree depth)
reg = DecisionTreeRegressor(max_depth=3, random_state=0)
reg.fit(Xr_train, yr_train)

# 9. Predict and evaluate
yr_pred = reg.predict(Xr_test)
mse = mean_squared_error(yr_test, yr_pred)
print(f"✅ Regressor Mean Squared Error: {mse:.2f}")

# 10. Visualize the regressor tree
plt.figure(figsize=(12, 6))
plot_tree(reg, filled=True)
plt.title("Decision Tree Regressor (max_depth=3)")
plt.show()
prac 4d svm


# Import libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -------------------------------
# 1. Load the Iris dataset
# -------------------------------
iris = datasets.load_iris()
X = iris.data[:, :2]   # Take only first two features for easy visualization
y = iris.target

# -------------------------------
# 2. Split data into train (70%) and test (30%)
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# -------------------------------
# 3. Build an SVM classifier (Linear Kernel)
# -------------------------------
svm_model = SVC(kernel='linear', C=1.0, random_state=42)
svm_model.fit(X_train, y_train)

# -------------------------------
# 4. Predict on test data
# -------------------------------
y_pred = svm_model.predict(X_test)

# -------------------------------
# 5. Evaluate accuracy
# -------------------------------
accuracy = accuracy_score(y_test, y_pred)
print(f'✅ Accuracy of SVM classifier: {accuracy:.2f}')

# -------------------------------
# 6. Visualize decision boundaries
# -------------------------------
def plot_decision_boundaries(X, y, model):
    # Define the grid range
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))

    # Predict on grid points
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Plot contour and points
    plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.coolwarm)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm, edgecolors='k')
    plt.xlabel(iris.feature_names[0])
    plt.ylabel(iris.feature_names[1])
    plt.title('SVM Decision Boundaries (Linear Kernel)')
    plt.show()

# Call the visualization function
plot_decision_boundaries(X_test, y_test, svm_model)
prac 4f gradient boosting

# Import required libraries
import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

# -----------------------------------
# 1. Load dataset
# -----------------------------------
data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target)

# -----------------------------------
# 2. Split into train and test sets
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=7
)

# -----------------------------------
# 3. Define a baseline Gradient Boosting Classifier
# -----------------------------------
gbm = GradientBoostingClassifier(random_state=7)

# -----------------------------------
# 4. Hyperparameter tuning using GridSearchCV
# -----------------------------------
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [3, 4, 5],
    'learning_rate': [0.01, 0.1, 0.2]
}

grid_search = GridSearchCV(
    estimator=gbm,
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

print(f"Best parameters found: {grid_search.best_params_}")
best_gbm = grid_search.best_estimator_

# -----------------------------------
# 5. Predict on test set and evaluate
# -----------------------------------
y_pred = best_gbm.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Test set accuracy: {accuracy:.3f}\n")
print("📊 Classification Report:\n", classification_report(y_test, y_pred))

# -----------------------------------
# 6. Feature importance visualization
# -----------------------------------
feat_importances = pd.Series(best_gbm.feature_importances_, index=X.columns)
feat_importances = feat_importances.sort_values(ascending=False)

plt.figure(figsize=(10, 6))
plt.bar(feat_importances.index, feat_importances.values, color='teal')
plt.xticks(rotation=90)
plt.title('Feature Importance from Gradient Boosting')
plt.ylabel('Importance')
plt.tight_layout()
plt.show()

prac5a  naive bayes

# Import libraries
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------------
# 1. Load dataset (Iris dataset)
# -----------------------------------
iris = load_iris()
X = iris.data
y = iris.target

print("Feature names:", iris.feature_names)
print("Target names:", iris.target_names)

# -----------------------------------
# 2. Split dataset into train and test sets
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# -----------------------------------
# 3. Train Naïve Bayes classifier
# -----------------------------------
model = GaussianNB()
model.fit(X_train, y_train)

# -----------------------------------
# 4. Predict on test set
# -----------------------------------
y_pred = model.predict(X_test)

# -----------------------------------
# 5. Evaluate model performance
# -----------------------------------
print("\n✅ Model Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:\n", classification_report(y_test, y_pred, target_names=iris.target_names))

# -----------------------------------
# 6. Classify a new sample
# -----------------------------------
test_sample = [[5.1, 3.5, 1.4, 0.2]]  # Example: Iris-setosa-like input
predicted_class = model.predict(test_sample)

print("\nTest Sample:", test_sample)
print("Predicted Class:", iris.target_names[predicted_class][0])
prac 5b hidden markov model

# Install hmmlearn if not already installed
# (Uncomment the below line if running for the first time)
# !pip install hmmlearn

import numpy as np
import matplotlib.pyplot as plt
from hmmlearn import hmm

# -----------------------------------
# 1. Generate synthetic sequential data
# -----------------------------------
np.random.seed(42)
X = np.concatenate([
    np.random.normal(0, 1, 100),  # Observations near 0 (state 1)
    np.random.normal(5, 1, 100)   # Observations near 5 (state 2)
]).reshape(-1, 1)

# -----------------------------------
# 2. Define an HMM with 2 hidden states
# -----------------------------------
model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=100)

# -----------------------------------
# 3. Fit the model to the data
# -----------------------------------
model.fit(X)

# -------------
6a implment bayesian linear regression to explore prior and posterior distribution

import numpy as np
import matplotlib.pyplot as plt

# Simulating data
np.random.seed(0)
X = np.linspace(0, 10, 100)
y = 3 * X + np.random.normal(0, 2, size=X.shape)

# Design matrix (with intercept term)
X_design = np.vstack([np.ones_like(X), X]).T

# Parameters
alpha = 1.0   # prior precision
sigma2 = 4.0  # noise variance

# Compute the posterior distribution
Sigma_w = np.linalg.inv(alpha * np.dot(X_design.T, X_design) + (1 / sigma2) * np.eye(2))
mu_w = np.dot(Sigma_w, np.dot(X_design.T, y))

# Posterior samples
num_samples = 1000
w_samples = np.random.multivariate_normal(mu_w, Sigma_w, num_samples)

# Plot the prior and posterior distributions of the weights
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

# Prior: Gaussian with mean 0 and precision alpha
prior_w = np.random.normal(0, 1/np.sqrt(alpha), (num_samples, 2))

# Plot prior for w_0 and w_1
axs[0].hist(prior_w[:, 0], bins=30, alpha=0.6, label='w_0 (Prior)')
axs[0].hist(prior_w[:, 1], bins=30, alpha=0.6, label='w_1 (Prior)')
axs[0].set_title("Prior Distributions of w_0 and w_1")
axs[0].legend()

# Plot posterior for w_0 and w_1
axs[1].hist(w_samples[:, 0], bins=30, alpha=0.6, label='w_0 (Posterior)')
axs[1].hist(w_samples[:, 1], bins=30, alpha=0.6, label='w_1 (Posterior)')
axs[1].set_title("Posterior Distributions of w_0 and w_1")
axs[1].legend()

plt.show()

# Visualize data with posterior predictive lines
x_pred = np.linspace(0, 10, 100)
X_pred = np.vstack([np.ones_like(x_pred), x_pred]).T
y_pred_samples = np.dot(X_pred, w_samples.T)

plt.plot(X, y, 'bo', label='Data')
plt.plot(x_pred, np.mean(y_pred_samples, axis=1), 'r-', label='Posterior Mean Prediction')

plt.fill_between(
    x_pred,
    np.percentile(y_pred_samples, 2.5, axis=1),
    np.percentile(y_pred_samples, 97.5, axis=1),
    color='gray',
    alpha=0.5,
    label='95% CI'
)

plt.legend()
plt.title('Bayesian Linear Regression with Posterior Predictive Interval')
plt.show()
6b implement gaussin mixture models for density estimation nd unsupervised clustering 

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal

# Generate synthetic 2D data from 3 clusters
np.random.seed(42)
mean1 = [0, 0]
cov1 = [[0.5, 0], [0, 0.5]]
data1 = np.random.multivariate_normal(mean1, cov1, 100)

mean2 = [3, 5]
cov2 = [[0.7, 0], [0, 0.3]]
data2 = np.random.multivariate_normal(mean2, cov2, 100)

mean3 = [7, 2]
cov3 = [[0.6, 0.1], [0.1, 0.4]]
data3 = np.random.multivariate_normal(mean3, cov3, 100)

X = np.vstack([data1, data2, data3])
N, D = X.shape
K = 3  # Number of mixture components

# Initialize parameters
np.random.seed(0)
mu = X[np.random.choice(N, K, replace=False)]  # Random initial means
cov = [np.eye(D) for _ in range(K)]            # Identity covariance matrices
pi = np.ones(K) / K                            # Equal weights

# EM Algorithm
def gaussian_pdf(x, mean, cov):
    return multivariate_normal.pdf(x, mean=mean, cov=cov)

def e_step(X, mu, cov, pi):
    N, K = X.shape[0], len(pi)
    gamma = np.zeros((N, K))
    for k in range(K):
        gamma[:, k] = pi[k] * gaussian_pdf(X, mu[k], cov[k])
    gamma /= gamma.sum(axis=1, keepdims=True)
    return gamma

def m_step(X, gamma):
    N, D = X.shape
    K = gamma.shape[1]

    Nk = gamma.sum(axis=0)
    pi = Nk / N

    mu = (gamma.T @ X) / Nk[:, np.newaxis]

    cov = []
    for k in range(K):
        X_centered = X - mu[k]
        cov_k = (gamma[:, k][:, np.newaxis] * X_centered).T @ X_centered / Nk[k]
        cov.append(cov_k + 1e-6 * np.eye(D))  # Stability term

    return mu, cov, pi

# Run EM
n_iter = 100
for i in range(n_iter):
    gamma = e_step(X, mu, cov, pi)
    mu, cov, pi = m_step(X, gamma)

# Predict cluster assignment
cluster_assignments = np.argmax(gamma, axis=1)

# Plot clustered data
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=cluster_assignments, cmap='viridis', s=20)
plt.scatter(mu[:, 0], mu[:, 1], c='red', marker='x', label='Means', s=100)
plt.title("GMM Clustering using EM Algorithm")
plt.xlabel("X1")
plt.ylabel("X2")
plt.legend()
plt.grid(True)
plt.show()
7a implement cross validation techniques robust model evaluation 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# Step 1: Load the dataset
dataset = pd.read_csv("Social_Network_Ads.csv")

# Step 2: Preprocess the dataset
# Encode 'Gender' column (Male=0, Female=1)
label_encoder = LabelEncoder()
dataset['Gender'] = label_encoder.fit_transform(dataset['Gender'])

# Features and target variable
X = dataset[['Gender', 'Age', 'EstimatedSalary']]  # Features
y = dataset['Purchased']                           # Target

# Step 3: Initialize the model
model = RandomForestClassifier(random_state=42)

# --- 1. K-Fold Cross-Validation ---
print("Performing K-Fold Cross-Validation...")

# Define K-Fold Cross-Validation (5 folds)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Perform k-fold cross-validation and get accuracy scores for each fold
kf_cv_results = cross_val_score(model, X, y, cv=kf, scoring='accuracy')

# Output results
print(f"K-Fold Cross-Validation Accuracy Scores: {kf_cv_results}")
print(f"Mean Accuracy (K-Fold): {kf_cv_results.mean():.4f}")

# --- 2. Stratified K-Fold Cross-Validation ---
print("\nPerforming Stratified K-Fold Cross-Validation...")

# Define Stratified K-Fold Cross-Validation (5 folds)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Perform stratified k-fold cross-validation and get accuracy scores for each fold
skf_cv_results = cross_val_score(model, X, y, cv=skf, scoring='accuracy')

# Output results
print(f"Stratified K-Fold Cross-Validation Accuracy Scores: {skf_cv_results}")
print(f"Mean Accuracy (Stratified K-Fold): {skf_cv_results.mean():.4f}")

# --- 3. Plot the results ---
plt.figure(figsize=(12, 6))

# Plot for K-Fold Cross-Validation
plt.subplot(1, 2, 1)
sns.boxplot(x=kf_cv_results)
plt.title('K-Fold Cross-Validation Accuracy Scores')
plt.xlabel('Accuracy')

# Plot for Stratified K-Fold Cross-Validation
plt.subplot(1, 2, 2)
sns.boxplot(x=skf_cv_results)
plt.title('Stratified K-Fold Cross-Validation Accuracy Scores')
plt.xlabel('Accuracy')

plt.tight_layout()
plt.show()
 7b systematically explore combination of hyperparameters to optimize model performance 

import pandas as pd
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
from scipy.stats import randint
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the dataset
dataset = pd.read_csv("Social_Network_Ads.csv")

# Step 2: Preprocess the dataset
label_encoder = LabelEncoder()
dataset['Gender'] = label_encoder.fit_transform(dataset['Gender'])

# Features and target variable
X = dataset[['Gender', 'Age', 'EstimatedSalary']]
y = dataset['Purchased']

# Step 3: Initialize the model
model = RandomForestClassifier(random_state=42)

# --- 1. Grid Search Hyperparameter Optimization ---
print("Performing Grid Search for Hyperparameter Tuning...")

# Define the hyperparameter grid
param_grid = {
    'n_estimators': [10, 50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['auto', 'sqrt', 'log2'],
}

# Setup the GridSearchCV with 5-fold cross-validation
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5,
                           scoring='accuracy', n_jobs=-1)

# Fit the grid search to the data
grid_search.fit(X, y)

# Output the best parameters and the best score
print(f"Best Hyperparameters from Grid Search: {grid_search.best_params_}")
print(f"Best Cross-Validation Accuracy from Grid Search: {grid_search.best_score_:.4f}")

# --- 2. Randomized Search Hyperparameter Optimization ---
print("\nPerforming Randomized Search for Hyperparameter Tuning...")

# Define the hyperparameter distribution
param_dist = {
    'n_estimators': randint(10, 200),
    'max_depth': [5, 10, 15, None],
    'min_samples_split': randint(2, 10),
    'min_samples_leaf': randint(1, 5),
    'max_features': ['auto', 'sqrt', 'log2'],
}

# Setup the RandomizedSearchCV with 5-fold cross-validation
random_search = RandomizedSearchCV(estimator=model, param_distributions=param_dist,
                                   n_iter=100, cv=5, scoring='accuracy',
                                   n_jobs=-1, random_state=42)

# Fit the randomized search to the data
random_search.fit(X, y)

# Output the best parameters and the best score
print(f"Best Hyperparameters from Randomized Search: {random_search.best_params_}")
print(f"Best Cross-Validation Accuracy from Randomized Search: {random_search.best_score_:.4f}")

# Step 4: Confusion Matrix and Visualization
best_model_grid = grid_search.best_estimator_
best_model_random = random_search.best_estimator_

# Predictions using the best models
y_pred_grid = best_model_grid.predict(X)
y_pred_random = best_model_random.predict(X)

# Confusion Matrices
cm_grid = confusion_matrix(y, y_pred_grid)
cm_random = confusion_matrix(y, y_pred_random)

# Plot confusion matrices
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
sns.heatmap(cm_grid, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Not Purchased', 'Purchased'],
            yticklabels=['Not Purchased', 'Purchased'])
plt.title('Confusion Matrix - GridSearchCV')
plt.xlabel('Predicted')
plt.ylabel('True')

plt.subplot(1, 2, 2)
sns.heatmap(cm_random, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Not Purchased', 'Purchased'],
            yticklabels=['Not Purchased', 'Purchased'])
plt.title('Confusion Matrix - RandomizedSearchCV')
plt.xlabel('Predicted')
plt.ylabel('True')

plt.tight_layout()
plt.show()
8a Bayesian Learning using inferences.

import matplotlib.pyplot as plt

# Given probabilities
P_Disease = 0.01
P_NoDisease = 0.99
P_Positive_given_Disease = 0.99
P_Positive_given_NoDisease = 0.05  # False positive rate

# Total probability of a positive test
P_Positive = (P_Positive_given_Disease * P_Disease) + \
             (P_Positive_given_NoDisease * P_NoDisease)

# Posterior probability: P(Disease | Positive)
P_Disease_given_Positive = (P_Positive_given_Disease * P_Disease) / P_Positive
P_NoDisease_given_Positive = 1 - P_Disease_given_Positive

# Bar chart data
labels = ['Disease | Positive', 'No Disease | Positive']
values = [P_Disease_given_Positive, P_NoDisease_given_Positive]
colors = ['red', 'green']

# Plotting
plt.figure(figsize=(8, 5))
plt.bar(labels, values, color=colors)
plt.ylim(0, 1)
plt.title('Posterior Probabilities Given a Positive Test Result')
plt.ylabel('Probability')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
9a set up a generator network to produce samples nd a disrcrimanator network to distinguish between real nd generated data 

import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

# Simple 1D dataset: real data ~ N(4, 1)
def get_real_data(batch_size):
    return torch.randn(batch_size, 1) + 4

# Generator network
class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, z):
        return self.net(z)

# Discriminator network
class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

# Hyperparameters
lr = 0.001
batch_size = 32
epochs = 2000

# Initialize networks and optimizers
G = Generator()
D = Discriminator()
criterion = nn.BCELoss()
optimizerD = optim.Adam(D.parameters(), lr=lr)
optimizerG = optim.Adam(G.parameters(), lr=lr)

# For plotting losses
losses_D = []
losses_G = []

for epoch in range(epochs):
    # -------- Train Discriminator --------
    D.zero_grad()

    # Real data
    real_data = get_real_data(batch_size)
    real_labels = torch.ones(batch_size, 1)
    fake_labels = torch.zeros(batch_size, 1)

    output_real = D(real_data)
    loss_real = criterion(output_real, real_labels)

    # Fake data
    noise = torch.randn(batch_size, 1)
    fake_data = G(noise)
    output_fake = D(fake_data.detach())
    loss_fake = criterion(output_fake, fake_labels)

    lossD = loss_real + loss_fake
    lossD.backward()
    optimizerD.step()

    # -------- Train Generator --------
    G.zero_grad()
    noise = torch.randn(batch_size, 1)
    fake_data = G(noise)
    output = D(fake_data)
    lossG = criterion(output, real_labels)  # want D(fake) -> 1
    lossG.backward()
    optimizerG.step()

    # Track losses
    losses_D.append(lossD.item())
    losses_G.append(lossG.item())

    if epoch % 200 == 0:
        print(f"Epoch {epoch} | LossD: {lossD.item():.4f} | LossG: {lossG.item():.4f}")

# Plot losses
plt.figure(figsize=(10, 5))
plt.plot(losses_D, label="Discriminator Loss")
plt.plot(losses_G, label="Generator Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.title("Training Losses")
plt.show()

# Plot real vs generated data distribution
with torch.no_grad():
    real_samples = get_real_data(1000).numpy()
    noise = torch.randn(1000, 1)
    generated_samples = G(noise).numpy()

plt.figure(figsize=(10, 5))
plt.hist(real_samples, bins=30, alpha=0.6, label='Real Data')
plt.hist(generated_samples, bins=30, alpha=0.6, label='Generated Data')
plt.legend()
plt.title("Real vs Generated Data Distribution")
plt.show()
10a devlop an API to deploy your model nd perform predictions 

import nest_asyncio
import uvicorn
from fastapi import FastAPI
from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB
from pydantic import BaseModel
import threading

# Allow nested event loops for Jupyter notebook
nest_asyncio.apply()

# Creating FastAPI instance
app = FastAPI()

# Creating class to define the request body and the type hints of each attribute
class request_body(BaseModel):
sepal_length: float
sepal_width: float
petal_length: float
petal_width: float

# Loading Iris Dataset
iris = load_iris()

# Getting our Features and Targets
X = iris.data
Y = iris.target

# Creating and Fitting our Model
clf = GaussianNB()
clf.fit(X, Y)

# Creating an Endpoint to receive the data for prediction
@app.post('/predict')
def predict(data: request_body):
# Making the data in a form suitable for prediction
test_data = [[
data.sepal_length,
data.sepal_width,
data.petal_length,
data.petal_width
]]
# Predicting the Class
class_idx = clf.predict(test_data)[0]
# Return the Result
return {'class': iris.target_names[class_idx]}

# Run Uvicorn in a separate thread to avoid blocking the Jupyter notebook
def run_uvicorn():
uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", use_colors=True)

# Start Uvicorn server in the background
thread = threading.Thread(target=run_uvicorn)
thread.start()
prac4e random forest


# Import libraries
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# -------------------------------
# 1. Load the Iris dataset
# -------------------------------
iris = load_iris()
X, y = iris.data, iris.target

# -------------------------------
# 2. Split into train and test sets
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# -------------------------------
# 3. Train a single Decision Tree (limit depth to prevent overfitting)
# -------------------------------
dt_clf = DecisionTreeClassifier(max_depth=5, random_state=42)
dt_clf.fit(X_train, y_train)
y_pred_dt = dt_clf.predict(X_test)
acc_dt = accuracy_score(y_test, y_pred_dt)

# -------------------------------
# 4. Train Random Forests with varying n_estimators and max_features
# -------------------------------
results = []
n_estimators_list = [5, 10, 50, 100]
max_features_list = ['sqrt', 'log2', None]  # None = all features

for n_trees in n_estimators_list:
    for max_feat in max_features_list:
        rf_clf = RandomForestClassifier(
            n_estimators=n_trees,
            max_features=max_feat,
            max_depth=5,
            random_state=42
        )
        rf_clf.fit(X_train, y_train)
        y_pred_rf = rf_clf.predict(X_test)
        acc_rf = accuracy_score(y_test, y_pred_rf)
        results.append((n_trees, max_feat, acc_rf))

# -------------------------------
# 5. Print Results
# -------------------------------
print(f"🌳 Decision Tree Accuracy (max_depth=5): {acc_dt:.3f}\n")

print("🤖 Random Forest Accuracy with varying n_estimators and max_features:")
for n_trees, max_feat, acc in results:
    print(f"Trees: {n_trees:3d}, max_features: {max_feat:6}, Accuracy: {acc:.3f}")

# -------------------------------
# 6. Visualize the Decision Tree
# -------------------------------
plt.figure(figsize=(12, 6))
plot_tree(dt_clf,
          feature_names=iris.feature_names,
          class_names=iris.target_names,
          filled=True)
plt.title("Decision Tree (max_depth=5)")
plt.show()


""")

