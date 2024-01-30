import os
import pandas as pd

if __name__ == '__main__':
    # Directory containing the TSV files
    DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data/csv"
    
    # Get all TSV files in a directory
    files = [file_name for file_name in os.listdir(DATA_FOLDER) if file_name.endswith('.tsv')]

    global_df = pd.DataFrame()

    for file_name in files:
        print("Analyzing file: {}".format(file_name))
        df_file = pd.read_csv(os.path.join(DATA_FOLDER, file_name), sep="\t")

        global_df = pd.concat([global_df, df_file], ignore_index=True)

    # Save the global dataframe
    print("Saving all data ...")
    global_df.to_csv(os.path.join(DATA_FOLDER, "data.tsv"), sep="\t", index=False)
    print("Done!")
