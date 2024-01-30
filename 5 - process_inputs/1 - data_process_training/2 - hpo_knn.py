import optuna
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
from random import randint


# def balance_data(data, number_occurrences):
#     """
#     This function is used to balance the data passed as input.
#     :param data: The data to be balanced.
#     :return: The balanced data.
#     """
#     data_np = data.to_numpy()
#     y = data_np[:, 20]

#     unique_labels = np.unique(y)
#     balanced_dfs = list()

#     for label in unique_labels:
#         selected_data = data[data[20] == label]
#         # Get the indexes of the selected data
#         indexes = np.random.choice(selected_data.shape[0], number_occurrences - 1, replace=False)
#         random_data = selected_data.iloc[indexes]
#         balanced_dfs.append(random_data)

#     return pd.concat(balanced_dfs)

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

# Select a random train and test index
random_index = randint(0, len(train_indices) - 1)

train_data = data.iloc[list(train_indices[random_index]), :]
test_data = data.iloc[list(test_indices[random_index]), :]

# # Balance the training data
# train_data = balance_data(train_data, SPLIT)

# Do the hyperparameter tuning with the selected random train and test data
train_df_numpy = train_data.to_numpy()
X_train = train_df_numpy[:, :20]
y_train = train_df_numpy[:, 20]

test_df_numpy = test_data.to_numpy()
X_test = test_df_numpy[:, :20]
y_test = test_df_numpy[:, 20]

def objective_knn(trial):
    knn_neighbours = trial.suggest_int("knn_neighbours", 2, 1e3, log=True)
    knn_weights = trial.suggest_categorical("knn_weights", ["uniform", "distance"])
    knn_algorithm = trial.suggest_categorical("knn_algorithm", ["ball_tree", "kd_tree", "brute"])
    knn_leaf_size = trial.suggest_int("knn_leaf", 2, 1e3, log=True)

    classifier_obj = KNeighborsClassifier(
        n_neighbors=knn_neighbours,
        weights=knn_weights,
        algorithm=knn_algorithm,
        leaf_size=knn_leaf_size
    )

    classifier_obj.fit(X_train, y_train)
    y_pred = classifier_obj.predict(X_test)
    f1_score_metric = f1_score(y_test, y_pred, average="micro")

    return 1 - f1_score_metric

study = optuna.create_study(direction="minimize")
study.optimize(objective_knn, n_trials=200, gc_after_trial=True, n_jobs=-1)

print(study.best_trial)
print(study.best_value)
trials_df = study.trials_dataframe()
trials_df.to_csv("hpo_knn_github.csv", index=False)
