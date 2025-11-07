# ML

def ml_help():
    print(
        '''
    Welcome to the ML Practicals CLI! 🚀

    This tool allows you to print the code for various machine learning practicals.
    You can run any command either directly from your terminal or by calling its
    function within a Python environment.

    =========================
    == General Commands    ==
    =========================
    
    Command: ml-help
    Function: ml_help()
    Description: Shows this help message.

    Command: ml-index
    Function: ml_index()
    Description: Displays the full list of practicals.

    =========================
    == Practical Commands  ==
    =========================

    --- Practical 1: Data Pre-processing ---
    ml-prac-1a      (ml_prac_1a)
    ml-prac-1b      (ml_prac_1b)
    ml-prac-1c      (ml_prac_1c)
    ml-prac-1d      (ml_prac_1d)

    --- Practical 2: Testing Hypothesis ---
    ml-prac-2a      (ml_prac_2a)

    --- Practical 3: Linear Models ---
    ml-prac-3a      (ml_prac_3a)
    ml-prac-3b      (ml_prac_3b)
    ml-prac-3c      (ml_prac_3c)
    
    --- Practical 4: Discriminative Models ---
    ml-prac-4a      (ml_prac_4a)
    ml-prac-4b      (ml_prac_4b)
    ml-prac-4c      (ml_prac_4c)
    ml-prac-4d      (ml_prac_4d)
    ml-prac-4e      (ml_prac_4e)
    ml-prac-4f      (ml_prac_4f)

    --- Practical 5: Generative Models ---
    ml-prac-5a      (ml_prac_5a)
    ml-prac-5b      (ml_prac_5b)

    --- Practical 6: Probabilistic Models ---
    ml-prac-6a      (ml_prac_6a)
    ml-prac-6b      (ml_prac_6b)

    --- Practical 7: Model Evaluation ---
    ml-prac-7a      (ml_prac_7a)
    ml-prac-7b      (ml_prac_7b)

    --- Practical 8: Bayesian Learning ---
    ml-prac-8a      (ml_prac_8a)

    --- Practical 9: Deep Generative Models ---
    ml-prac-9a      (ml_prac_9a)
        '''
    )

def ml_index():
    print(
        '''
1. Data Pre-processing and Exploration
    1a. Load a CSV dataset. Handle missing values, inconsistent formatting, and outliers.
    1b. Load a dataset, calculate descriptive summary statistics, create visualizations using different graphs, and identify potential features and target variables Note: Explore Univariate and Bivariate graphs (Matplotlib) and Seaborn for visualization.
    1c. Create or Explore datasets to use all pre-processing routines like label encoding, scaling and binerization.
    1d. Design a simple machine learning model to train the training instances and test the same.

2. Testing Hypothesis
    2a. Implement and demonstrate the find-s algorithm for finding the most specific hypothesis based on given set of training data samples. Read the training data from a. CSV file and generate the final specific hypothesis (Create your dataset).

3. Linear Models
    3a. Simple Linear Regression: Fit a linear regression model on a dataset. Interpret coefficients, make predictions, and evaluate performance using metrics like R-squared and MSE.
    3b. Multiple Linear Regression: Extend linear regression to multiple features. Handle feature selection and potential multi collinearity.
    3c. Regularized Linear Models (Ridge, Lasso, ElasticNet): Implement regression variants like LASSO aid Ridge on any generated dataset.

4. Discriminative Models
    4a. Logistic Regression: Perform binary classification using logistic regression. Calculate accuracy, precision, recall, and understand the ROC curve.
    4b. k-nearest Neighbor: Implement and demonstrate k-nearest Neighbor algorithm. Read the training data from .CSV file and build a model to classify the test sample. Print both correct and wrong predictions.
    4c. Decision Tree: Build decision tree classifier or regressor. Control hyperparameters like tree depth to avoid overfitting. Visualize the tree.
    4d. Support Vector Machine: Implement a Support Vector Machine for any relevant dataset.
    4e. Random Forest ensemble: Train the random forest ensemble. Experiment with the number of trees and feature sampling. Compare performance to a single decision tree.
    4f. Gradient Boosting machine: Implement a gradient boosting machine. Tune hyper parameters and explore feature importance.

5. Generative Models
    5a. Implement and demonstrate the working of a Naïve Bayesian classifier using a sample data set. Build the model to classify a test sample.
    5b. Implement Hidden Markov Models using hmmlearn.

6. Probabilistic Models
    6a. Implement Bayesian Linear Regression to explore prior and posterior distribution.
    6b. Implement Gaussian Mixture Models for density estimation and unsupervised clustering.

7. Model Evaluation and Hyperparameter Tuning
    7a. Implement cross-validation techniques (k-fold, stratified, etc.) for robust model evaluation.
    7b. Systematically explore combinations of hyperparameters to optimize model performance. (use grid and randomized search).

8. Bayesian learning
    8a. Implement Bayesian Learning using inferences.

9. Deep Generative Models
    9a. Set up a generator network to produce samples and a discriminator network to distinguish between real and generated data. (Use a simple dataset).

10. Model Deployment
    10a. Develop an API to deploy your model and perform predictions.
        '''
    )

def ml_prac_1a():
    print(
        '''
import pandas as pd
from scipy import stats

df = pd.read_csv('D:\\M.Sc.IT\\Sem3\\ML\\Practicals\\Social_Network_Ads.csv')

print("Missing values before cleaning:")
print(df.isnull().sum())

numeric_cols = df.select_dtypes(include=['number']).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

categorical_cols = df.select_dtypes(include=['object']).columns
for column in categorical_cols:
    df[column] = df[column].fillna(df[column].mode()[0])

print("\\nData types before formatting:")
print(df.dtypes)

for column in categorical_cols:
    df[column] = df[column].str.lower().str.strip()

for column in numeric_cols:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

print("\\nMissing values after cleaning:")
print(df.isnull().sum())
print("\\nData types after formatting:")
print(df.dtypes)
print("\\nCleaned DataFrame:")
print(df.head())
        '''
    )

def ml_prac_1b():
    print(
        '''
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

titanic = sns.load_dataset('titanic')

print("First few rows of the dataset:")
print(titanic.head())

summary_statistics = titanic.describe(include='all')
print("\\nDescriptive Summary Statistics:")
print(summary_statistics)

plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
sns.histplot(titanic['age'].dropna(), bins=15, kde=True)
plt.title('Distribution of Age')

plt.subplot(2, 2, 2)
sns.countplot(x='survived', data=titanic)
plt.title('Count of Survival (0 = No, 1 = Yes)')

plt.subplot(2, 2, 3)
sns.countplot(x='pclass', data=titanic)
plt.title('Count of Passengers by Class')

plt.subplot(2, 2, 4)
sns.boxplot(x='survived', y='fare', data=titanic)
plt.title('Fare by Survival Status')

plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=titanic, x='age', y='fare', hue='survived', alpha=0.6)
plt.title('Age vs Fare by Survival Status')
plt.show()

sns.pairplot(titanic, hue='survived', diag_kind='kde')
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='survived', y='age', data=titanic)
plt.title('Age by Survival Status')
plt.show()

features = ['pclass', 'sex', 'age', 'fare', 'sibsp', 'parch', 'embarked']
target = 'survived'

print("\\nPotential Features:", features)
print("Target Variable:", target)
        '''
    )

def ml_prac_1c():
    print(
        '''
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler, Binarizer

np.random.seed(42)

data = {
    'age': np.random.randint(18, 70, size=100),
    'income': np.random.randint(20000, 120000, size=100),
    'gender': np.random.choice(['male', 'female'], size=100),
    'purchased': np.random.choice(['yes', 'no'], size=100)
}
df = pd.DataFrame(data)

print("First few rows of the dataset:")
print(df.head())

print("\\nDescriptive Statistics:")
print(df.describe(include='all'))

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
sns.histplot(df['age'], bins=15, kde=True)
plt.title('Age Distribution')

plt.subplot(1, 2, 2)
sns.histplot(df['income'], bins=15, kde=True)
plt.title('Income Distribution')

plt.tight_layout()
plt.show()

label_encoder = LabelEncoder()
df['gender_encoded'] = label_encoder.fit_transform(df['gender'])
df['purchased_encoded'] = label_encoder.fit_transform(df['purchased'])
print("\\nData after Label Encoding:")
print(df[['gender', 'gender_encoded', 'purchased', 'purchased_encoded']].head())

scaler = StandardScaler()
df[['age_scaled', 'income_scaled']] = scaler.fit_transform(df[['age', 'income']])
print("\\nData after Scaling:")
print(df[['age', 'income', 'age_scaled', 'income_scaled']].head())

binarizer = Binarizer(threshold=50000)
df['income_binarized'] = binarizer.fit_transform(df[['income']])
print("\\nData after Binarization:")
print(df[['income', 'income_binarized']].head())

print("\\nFinal DataFrame:")
print(df.head())
        '''
    )

def ml_prac_1d():
    print(
        '''
import numpy
import matplotlib.pyplot as plt
numpy.random.seed(2)
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

x = numpy.random.normal(3,1,100)
y = numpy.random.normal(156,40,100)/x

plt.scatter(x,y)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Scatter Plot of X vs Y")
plt.show()

train_x = x[:80]
train_y = y[:80]
test_x = x[:20]
test_y = y[:20]

plt.scatter(train_x, train_y)
plt.xlabel("train_x")
plt.ylabel("train_y")
plt.title("Training Data Scatter Plot")
plt.show()

train_x,test_x,train_y,test_y = train_test_split(x,y,test_size=0.3)

plt.scatter(test_x,test_y)
plt.xlabel("test_x")
plt.ylabel("test_y")
plt.title("Test Data Scatter Plot")
plt.show()

mymodel = numpy.poly1d(numpy.polyfit(train_x, train_y,4))
myline = numpy.linspace(0,6,100)

plt.scatter(train_x, train_y)
plt.plot(myline, mymodel(myline))
plt.xlabel("train_x")
plt.ylabel("train_y")
plt.title("Polynomial Regression Fit on Training Data")
plt.show()
        '''
    )

def ml_prac_2a():
    print(
        '''
import csv

a = []
with open("book2.csv", "r") as csvfile:
    next(csvfile)
    for row in csv.reader(csvfile):
        a.append(row)

print("\\nThe Training Data:")
for x in a:
    print(x)

print("\\nThe total number of training instances: ", len(a))

num_attribute = len(a[0]) - 1

hypothesis = ["0"] * num_attribute
print("\\nThe initial hypothesis is:", hypothesis)

for i in range(len(a)):
    if a[i][num_attribute] == "yes":
        print(f"\\nInstance {i+1} is {a[i]} (Positive Instance)")
        for j in range(num_attribute):
            if hypothesis[j] == "0":
                hypothesis[j] = a[i][j]
            elif hypothesis[j] != a[i][j]:
                hypothesis[j] = "?"
        print(f"Hypothesis after instance {i+1}: {hypothesis}")
    else:
        print(f"\\nInstance {i+1} is {a[i]} (Negative Instance) → Ignored")

print("\\nFinal Maximally Specific Hypothesis:", hypothesis)
        '''
    )

def ml_prac_3a():
    print(
        '''
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

data = pd.read_csv('D:\\M.Sc.IT\\Sem3\\ML\\Practicals\\grades_km_input.csv')
df = pd.DataFrame(data)

X = df[['Math']]
y = df['Science']

model = LinearRegression()
model.fit(X, y)

y_pred = model.predict(X)

print("Coefficient:", model.coef_[0])
print("Intercept:", model.intercept_)
print("MSE:", mean_squared_error(y, y_pred))
print("R²:", r2_score(y, y_pred))

plt.scatter(X, y, color='blue', label='Actual')
plt.plot(X, y_pred, color='red', label='Prediction')
plt.xlabel('Math')
plt.ylabel('Science')
plt.title('Simple Linear Regression')
plt.legend()
plt.show()
        '''
    )

def ml_prac_3b():
    print(
        '''
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv('D:\\M.Sc.IT\\Sem3\\ML\\Practicals\\grades_km_input.csv')
df = pd.DataFrame(data)

X = df[['English', 'Math']]
y = df['Science']

X_const = sm.add_constant(X)

vif_data = pd.DataFrame()
vif_data['Feature'] = X_const.columns
vif_data['VIF'] = [variance_inflation_factor(X_const.values, i) for i in range(X_const.shape[1])]
print("\\nVariance Inflation Factor (VIF):\\n", vif_data)

high_vif_features = vif_data[vif_data['VIF'] > 5]['Feature']
high_vif_features = [f for f in high_vif_features if f != 'const']
if high_vif_features:
    X = X.drop(columns=high_vif_features)
    print(f"\\nRemoved features due to high multicollinearity: {high_vif_features}")

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

print("\\nMultiple Linear Regression Results:")
print("Features used:", list(X.columns))
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)
print("MSE:", mean_squared_error(y, y_pred))
print("R²:", r2_score(y, y_pred))

plt.figure(figsize=(5, 4))
sns.scatterplot(x=y, y=y_pred)
plt.xlabel("Actual Science Scores")
plt.ylabel("Predicted Science Scores")
plt.title("Actual vs Predicted")
plt.show()

residuals = y - y_pred
plt.figure(figsize=(5, 4))
sns.scatterplot(x=y_pred, y=residuals)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted Science Scores")
plt.ylabel("Residuals")
plt.title("Residual Plot")
plt.show()
        '''
    )

def ml_prac_3c():
    print(
        '''
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score

data = pd.read_csv('D:\\M.Sc.IT\\Sem3\\ML\\Practicals\\grades_km_input.csv')
df = pd.DataFrame(data)

X = df[['English', 'Math']]
y = df['Science']

models = {
    'Ridge': Ridge(alpha=1.0),
    'Lasso': Lasso(alpha=1.0),
    'ElasticNet': ElasticNet(alpha=1.0, l1_ratio=0.5)
}

predictions = {}
coefficients = {}

for name, model in models.items():
    model.fit(X, y)
    y_pred = model.predict(X)
    predictions[name] = y_pred
    coefficients[name] = model.coef_
    
    print(f"{name} Regression")
    print("  Coefficients:", model.coef_)
    print("  Intercept:", model.intercept_)
    print("  MSE:", mean_squared_error(y, y_pred))
    print("  R²:", r2_score(y, y_pred))
    print()
    
    plt.figure(figsize=(7, 4))
    plt.plot(y.values, label="Actual", marker='o', linestyle='--')
    plt.plot(y_pred, label=f"{name} Predicted", marker='x')
    plt.title(f"Actual vs Predicted Science Scores ({name} Regression)")
    plt.xlabel("Student Index")
    plt.ylabel("Science Score")
    plt.legend()
    plt.grid(True)
    plt.show()
        '''
    )

def ml_prac_4a():
    print(
        '''
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_curve,
    auc
)

data = load_breast_cancer()
X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression(max_iter=10000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)

print("Accuracy:", acc)
print("Precision:", prec)
print("Recall:", rec)

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=data.target_names, yticklabels=data.target_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

fpr, tpr, thresholds = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(6, 4))
plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.2f})")
plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Receiver Operating Characteristic (ROC) Curve")
plt.legend()
plt.grid(True)
plt.show()
        '''
    )

def ml_prac_4b():
    print(
        '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.decomposition import PCA

wine = load_wine()
df = pd.DataFrame(wine.data, columns=wine.feature_names)
df['target'] = wine.target

df.to_csv("wine_dataset.csv", index=False)
data = pd.read_csv("wine_dataset.csv")

X = data.drop("target", axis=1)
y = data["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))

results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
results["Match"] = results["Actual"] == results["Predicted"]
print("\\n✅ Correct Predictions:\\n", results[results["Match"]])
print("\\n❌ Wrong Predictions:\\n", results[~results["Match"]])

plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='OrRd',
            xticklabels=wine.target_names, yticklabels=wine.target_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

pca = PCA(n_components=2)
X_test_pca = pca.fit_transform(X_test)

plt.figure(figsize=(8, 5))
scatter = plt.scatter(X_test_pca[:, 0], X_test_pca[:, 1], c=y_pred, cmap='plasma', edgecolor='k', s=100)
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.title("KNN Predictions (PCA 2D)")
plt.legend(handles=scatter.legend_elements()[0], labels=list(wine.target_names))
plt.grid(True)
plt.show()
        '''
    )

def ml_prac_4c():
    print(
        '''
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score

iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

for depth in [1, 2, 3, 4, 5, None]:
    clf = DecisionTreeClassifier(max_depth=depth, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"max_depth={depth} --> Accuracy: {acc:.3f}")

clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(f"Accuracy on test set: {accuracy_score(y_test, y_pred):.2f}")

plt.figure(figsize=(12,8))
plot_tree(clf,
          feature_names=iris.feature_names,
          class_names=iris.target_names,
          filled=True, rounded=True, fontsize=12)
plt.title("Decision Tree Classifier (max_depth=3) on Iris Dataset")
plt.show()
        '''
    )

def ml_prac_4d():
    print(
        '''
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
import numpy as np

iris = datasets.load_iris()
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

svm_clf = SVC(kernel='linear', random_state=42)
svm_clf.fit(X_train, y_train)

y_pred = svm_clf.predict(X_test)
print(f"Accuracy on test set: {accuracy_score(y_test, y_pred):.2f}")

pca = PCA(n_components=2)
X_test_pca = pca.fit_transform(X_test)

def plot_decision_boundary_pca(clf, X_pca, y, title):
    x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
    y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))
    
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    grid_points_original = pca.inverse_transform(grid_points)
    Z = clf.predict(grid_points_original)
    Z = Z.reshape(xx.shape)
    
    plt.figure(figsize=(10, 6))
    plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.coolwarm)
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap=plt.cm.coolwarm, edgecolor='k', s=50)
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title(title)
    handles, _ = scatter.legend_elements()
    plt.legend(handles, iris.target_names)
    plt.show()

plot_decision_boundary_pca(svm_clf, X_test_pca, y_test, "SVM Decision Boundary with PCA (All features)")
        '''
    )

def ml_prac_4e():
    print(
        '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X, y = make_moons(n_samples=500, noise=0.3, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

dt_clf = DecisionTreeClassifier(random_state=42)
dt_clf.fit(X_train, y_train)
y_pred_dt = dt_clf.predict(X_test)
acc_dt = accuracy_score(y_test, y_pred_dt)

rf_params = [(10, 'sqrt'), (50, 'sqrt'), (100, 'sqrt')]
rf_results = []
for n, mf in rf_params:
    rf = RandomForestClassifier(n_estimators=n, max_features=mf, random_state=42)
    rf.fit(X_train, y_train)
    acc = accuracy_score(y_test, rf.predict(X_test))
    rf_results.append((n, mf, acc))

print(f"Decision Tree Accuracy: {acc_dt:.3f}")
for n, mf, acc in rf_results:
    print(f"Random Forest (n_estimators={n}, max_features={mf}) Accuracy: {acc:.3f}")

def plot_boundaries(clf, title):
    x_min, x_max = X[:,0].min() - .5, X[:,0].max() + .5
    y_min, y_max = X[:,1].min() - .5, X[:,1].max() + .5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                         np.linspace(y_min, y_max, 300))
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    plt.contourf(xx, yy, Z, alpha=0.3)
    plt.scatter(X_test[:,0], X_test[:,1], c=y_test, edgecolor='k')
    plt.title(title)
    plt.show()

plot_boundaries(dt_clf, f"Decision Tree (Accuracy: {acc_dt:.2f})")
best_rf = RandomForestClassifier(n_estimators=100, max_features='sqrt', random_state=42)
best_rf.fit(X_train, y_train)
plot_boundaries(best_rf, f"Random Forest (Accuracy: {accuracy_score(y_test, best_rf.predict(X_test)):.2f})")
        '''
    )

def ml_prac_4f():
    print(
        '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
from sklearn.model_selection import GridSearchCV

wine = load_wine()
X = wine.data
y = wine.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

gb_clf = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)
gb_clf.fit(X_train, y_train)

y_pred = gb_clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Gradient Boosting Accuracy: {acc:.3f}")

importances = gb_clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = np.array(wine.feature_names)[indices]

plt.figure(figsize=(10, 6))
plt.title("Feature Importances (Gradient Boosting - Wine Dataset)")
plt.bar(range(X.shape[1]), importances[indices], align='center')
plt.xticks(range(X.shape[1]), features, rotation=90)
plt.tight_layout()
plt.show()

params = {
    'n_estimators': [50, 100, 200],
    'learning_rate': [0.05, 0.1, 0.2],
    'max_depth': [2, 3, 5]
}
grid = GridSearchCV(GradientBoostingClassifier(random_state=42), params, cv=5, scoring='accuracy')
grid.fit(X_train, y_train)
print(f"Best Parameters: {grid.best_params_}")
print(f"Best CV Accuracy: {grid.best_score_:.3f}")
        '''
    )

def ml_prac_5a():
    print(
        '''
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

data = pd.read_csv("D:/M.Sc.IT/Sem3/ML/Practicals/Social_Network_Ads.csv")

print("Dataset Preview:")
print(data.head(), "\\n")

le = LabelEncoder()
data['Gender'] = le.fit_transform(data['Gender'])

X = data[['Gender', 'Age', 'EstimatedSalary']]
y = data['Purchased']

print("Feature Names:", list(X.columns))
print("Target Name: Purchased\\n")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = GaussianNB()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Predictions:", y_pred)
print("Actual:", y_test.values)
print("Accuracy:", accuracy_score(y_test, y_pred), "\\n")

new_sample = [[1, 30, 50000]]
prediction = model.predict(new_sample)
print("New sample classified as:", prediction[0])
        '''
    )

def ml_prac_5b():
    print(
        '''
import numpy as np
from hmmlearn import hmm

model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=100)

X = np.array([[1.0], [2.0], [3.0], [2.0], [1.0],
              [6.0], [7.0], [8.0], [7.0], [6.0]])

lengths = [len(X)]

model.fit(X, lengths)

hidden_states = model.predict(X)

print("Hidden States:", hidden_states)

X_new, Z_new = model.sample(5)
print("\\nGenerated sequence of observations:\\n", X_new)
print("Generated hidden states:\\n", Z_new)
        '''
    )

def ml_prac_6a():
    print(
        '''
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
X = np.linspace(-1, 1, 20)
Y = 2.5 * X + np.random.normal(0, 0.2, size=X.shape)

alpha = 2.0
beta = 25.0

Phi = np.vstack([np.ones(X.shape[0]), X]).T

m0 = np.zeros(2)
S0 = (1.0/alpha) * np.eye(2)

SN = np.linalg.inv(np.linalg.inv(S0) + beta * Phi.T @ Phi)

mN = SN @ (np.linalg.inv(S0) @ m0 + beta * Phi.T @ Y)

print("Posterior mean:", mN)
print("Posterior covariance:\\n", SN)

w0, w1 = np.random.multivariate_normal(m0, S0, 5).T
x_grid = np.linspace(-1, 1, 100)

plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
for i in range(5):
    plt.plot(x_grid, w0[i] + w1[i]*x_grid, lw=2)
plt.title("Prior Samples")
plt.scatter(X, Y, c='red')

w0_post, w1_post = np.random.multivariate_normal(mN, SN, 5).T
plt.subplot(1,2,2)
for i in range(5):
    plt.plot(x_grid, w0_post[i] + w1_post[i]*x_grid, lw=2)
plt.title("Posterior Samples")
plt.scatter(X, Y, c='red')

plt.show()
        '''
    )

def ml_prac_6b():
    print(
        '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.datasets import make_blobs

X, y_true = make_blobs(n_samples=300, centers=3, cluster_std=0.6, random_state=42)

gmm = GaussianMixture(n_components=3, covariance_type='full', random_state=42)
gmm.fit(X)
labels = gmm.predict(X)

log_probs = gmm.score_samples(X)

print("Cluster means:\\n", gmm.means_)
print("Cluster covariances:\\n", gmm.covariances_)

plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis')
plt.title("GMM Clustering")

x = np.linspace(X[:,0].min()-1, X[:,0].max()+1)
y = np.linspace(X[:,1].min()-1, X[:,1].max()+1)
X_grid, Y_grid = np.meshgrid(x, y)
XY = np.array([X_grid.ravel(), Y_grid.ravel()]).T
Z = -gmm.score_samples(XY)
Z = Z.reshape(X_grid.shape)

plt.subplot(1,2,2)
plt.contourf(X_grid, Y_grid, Z, levels=20, cmap='viridis')
plt.scatter(X[:, 0], X[:, 1], s=10, c='red')
plt.title("Density Estimation")

plt.show()
        '''
    )

def ml_prac_7a():
    print(
        '''
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt

iris = load_iris()
X, y = iris.data, iris.target

model = LogisticRegression(max_iter=200)

print("K-Fold Cross Validation:")
kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores_kf = cross_val_score(model, X, y, cv=kf)
print("Scores for each fold:", scores_kf)
print("Average Accuracy:", np.mean(scores_kf))


print("\\nStratified K-Fold Cross Validation:")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_skf = cross_val_score(model, X, y, cv=skf)
print("Scores for each fold:", scores_skf)
print("Average Accuracy:", np.mean(scores_skf))

plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.bar(range(1, len(scores_kf)+1), scores_kf, color="skyblue")
plt.axhline(np.mean(scores_kf), color="red", linestyle="--", label=f"Avg = {np.mean(scores_kf):.2f}")
plt.title("K-Fold Cross Validation Scores")
plt.xlabel("Fold")
plt.ylabel("Accuracy")
plt.legend()

plt.subplot(1,2,2)
plt.bar(range(1, len(scores_skf)+1), scores_skf, color="lightgreen")
plt.axhline(np.mean(scores_skf), color="red", linestyle="--", label=f"Avg = {np.mean(scores_skf):.2f}")
plt.title("Stratified K-Fold Cross Validation Scores")
plt.xlabel("Fold")
plt.ylabel("Accuracy")
plt.legend()

plt.tight_layout()
plt.show()
        '''
    )

def ml_prac_7b():
    print(
        '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(random_state=42)

param_grid = {
    'n_estimators': [10, 50, 100],
    'max_depth': [None, 5, 10],
    'min_samples_split': [2, 5, 10]
}
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

print("Best Parameters (Grid Search):", grid_search.best_params_)
print("Best Accuracy (Grid Search):", grid_search.best_score_)

param_dist = {
    'n_estimators': np.arange(10, 200, 10),
    'max_depth': [None] + list(np.arange(2, 20, 2)),
    'min_samples_split': np.arange(2, 20, 2)
}
random_search = RandomizedSearchCV(model, param_distributions=param_dist,
                                     n_iter=20, cv=5, scoring='accuracy',
                                     random_state=42)
random_search.fit(X_train, y_train)

print("\\nBest Parameters (Randomized Search):", random_search.best_params_)
print("Best Accuracy (Randomized Search):", random_search.best_score_)

best_model = random_search.best_estimator_
y_pred = best_model.predict(X_test)
print("\\nTest Accuracy with Best Model:", accuracy_score(y_test, y_pred))

scores = grid_search.cv_results_['mean_test_score']
params = range(len(scores))

plt.figure(figsize=(8,4))
plt.plot(params, scores, marker='o', label='Grid Search Scores')
plt.axhline(y=max(scores), color='r', linestyle='--', label='Best Grid Search Score')
plt.xlabel("Parameter Combination Index")
plt.ylabel("Accuracy")
plt.title("Grid Search Performance Across Parameter Combinations")
plt.legend()

best_grid_acc = grid_search.best_score_
best_random_acc = random_search.best_score_

plt.figure(figsize=(6,4))
plt.bar(["Grid Search", "Randomized Search"],
        [best_grid_acc, best_random_acc],
        color=["skyblue", "lightgreen"])
plt.ylabel("Accuracy")
plt.title("Comparison of Best Accuracies")
plt.ylim(0, 1)
plt.show()
        '''
    )

def ml_prac_8a():
    print(
        '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# This code assumes a CSV file named 'student_exam_synthetic.csv' exists
# in the same directory with columns: 'Hours_Studied', 'Attendance', 'Passed_Exam'

df = pd.read_csv("student_exam_synthetic.csv")
print(df.head())

X = df[['Hours_Studied', 'Attendance']].values
y = df['Passed_Exam'].map({'No': 0, 'Yes': 1}).values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = GaussianNB()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\\nAccuracy: {accuracy:.4f}")
print("\\nConfusion Matrix:\\n", confusion_matrix(y_test, y_pred))
print("\\nClassification Report:\\n", classification_report(y_test, y_pred))

new_student = [[6, 85]]
probabilities = model.predict_proba(new_student)
print(f"\\nProbability of Passing for student {new_student[0]}:")
print(f"Not Passed (No): {probabilities[0][0]:.2f}")
print(f"Passed (Yes): {probabilities[0][1]:.2f}")

x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                     np.arange(y_min, y_max, 0.1))

Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.figure(figsize=(8,6))
plt.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
plt.scatter(X[:,0], X[:,1], c=y, cmap='coolwarm', edgecolor='k', s=80)
plt.scatter(new_student[0][0], new_student[0][1], color='green', s=150, marker='*', label='New Student')
plt.xlabel('Hours Studied')
plt.ylabel('Attendance (%)')
plt.title('Naive Bayes Classification & Decision Boundary')
plt.legend()
plt.show()
        '''
    )

def ml_prac_9a():
    print(
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

def real_data(n=1000):
    return torch.randn(n, 1) * 1.5 + 2

class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(1, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )
    def forward(self, z):
        return self.model(z)

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(1, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.model(x)

G, D = Generator(), Discriminator()
criterion = nn.BCELoss()
opt_G = optim.Adam(G.parameters(), lr=0.01)
opt_D = optim.Adam(D.parameters(), lr=0.01)

epochs = 2000
for epoch in range(epochs):
    real = real_data(32)
    fake = G(torch.randn(32, 1))
    D_loss = criterion(D(real), torch.ones(32, 1)) + criterion(D(fake.detach()), torch.zeros(32, 1))
    opt_D.zero_grad()
    D_loss.backward()
    opt_D.step()

    fake = G(torch.randn(32, 1))
    G_loss = criterion(D(fake), torch.ones(32, 1))
    opt_G.zero_grad()
    G_loss.backward()
    opt_G.step()

    if epoch % 500 == 0:
        print(f"Epoch {epoch}, D_loss: {D_loss.item():.4f}, G_loss: {G_loss.item():.4f}")

real_samples = real_data(500).detach().numpy()
fake_samples = G(torch.randn(500, 1)).detach().numpy()

plt.hist(real_samples, bins=30, alpha=0.5, label="Real Data")
plt.hist(fake_samples, bins=30, alpha=0.5, label="Generated Data")
plt.legend()
plt.show()
        '''
    )