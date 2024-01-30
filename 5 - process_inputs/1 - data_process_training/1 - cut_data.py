import numpy as np
import pandas as pd

DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
TRANSFORMED_DATA_FOLDER = DATA_FOLDER + "/transformed_input"

# Number of occurrences of each label
NUMBER_OF_OCCURRENCES = 10

data = pd.read_csv(TRANSFORMED_DATA_FOLDER + "/data.csv", header=None)
data_np = data.to_numpy()

# Class column of the data
class_label = [int(number) for number in list(data_np[:, 20])]

# Checking the class distribution of the data
occurences = list(np.bincount(class_label))

# Cutting the data to a minimum provided by the number of occurrences
selected_dfs = []

for i in range(len(occurences)):
    if occurences[i] < NUMBER_OF_OCCURRENCES:
        continue
    else:
        selected_data = data[data[20] == i]
        # # Get the indexes of the selected data
        # indexes = np.random.choice(selected_data.shape[0], NUMBER_OF_OCCURRENCES, replace=False)
        # random_data = selected_data.iloc[indexes]
        selected_dfs.append(selected_data)

selected_records = pd.concat(selected_dfs)

# Save the balanced dataset to disk
selected_records.to_csv(TRANSFORMED_DATA_FOLDER + "/cutted_data.csv", index=False)
