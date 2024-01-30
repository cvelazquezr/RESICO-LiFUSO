import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def count_missclassifications(missclassified_data, classes, unique_classes_minimum):
    minimum_label = list()

    for index in missclassified_data:
        if classes[index] in unique_classes_minimum:
            minimum_label.append(classes[index])

    return len(set(minimum_label))

DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
TRANSFORMED_DATA_FOLDER = DATA_FOLDER + "/transformed_input"
SPLIT = 10

data = pd.read_csv(TRANSFORMED_DATA_FOLDER + "/cutted_data.csv", header=None)
data_np = data.to_numpy()

X = data_np[:, :20]
y = data_np[:, 20]

train_indices = list()
test_indices = list()

folds = StratifiedKFold(n_splits=SPLIT, shuffle=True, random_state=42).split(X, y)

for train, test in folds:
    train_indices.append(train)
    test_indices.append(test)

train_dfs = list()
test_dfs = list()

for i in range(SPLIT):
    train_dfs.append(data.iloc[list(train_indices[i]), :])
    test_dfs.append(data.iloc[list(test_indices[i]), :])

for index, (train_df, test_df) in enumerate(zip(train_dfs, test_dfs)):
    print("Fold: " + str(index + 1))

    # This is the optimised model for the imbalanced training dataset: it doesn't work for balanced data.
    # It is also the same for the model trained on balanced data, it might not work for imbalanced data.
    classifier = KNeighborsClassifier(n_neighbors=2, weights="uniform", algorithm="kd_tree", leaf_size=621)
    train_df_numpy = train_df.to_numpy()

    X_train = train_df_numpy[:, :20]
    y_train = train_df_numpy[:, 20]

    test_df_numpy = test_df.to_numpy()
    X_test = test_df_numpy[:, :20]
    y_test = test_df_numpy[:, 20]

    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)

    # Compute the differences between the predictions and the actual values to see if the missclassified elements belong
    # to the minority classes.

    # First get the classes with a minimum number of elements.
    unique_classes = np.unique(y_test)
    unique_classes_minimum = list()

    for label in unique_classes:
        if len(np.where(y_pred == label)[0]) == 10:
            unique_classes_minimum.append(label)

    missclassified = np.where(y_pred != y_test)[0]
    print("Missclassified labels that have the minimum number of classes: {} / {}".format(count_missclassifications(missclassified, y_test, unique_classes_minimum), len(unique_classes_minimum)))

    # Statistics on the test set
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="micro")
    recall = recall_score(y_test, y_pred, average="micro")
    f1 = f1_score(y_test, y_pred, average="micro")

    print("Accuracy: {}".format(accuracy))
    print("Precision: {}".format(precision))
    print("Recall: {}".format(recall))
    print("F1: {}".format(f1))

# Train a model on the full dataset
classifier = KNeighborsClassifier(n_neighbors=2, weights="uniform", algorithm="kd_tree", leaf_size=621)
classifier.fit(X, y)
joblib.dump(classifier, "{}/models/cls/knn_github.joblib".format(DATA_FOLDER), compress=9)
