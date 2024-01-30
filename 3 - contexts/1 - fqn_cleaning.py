import json
from sys import argv

if __name__ == '__main__':
    if len(argv) < 3:
        print("Too few arguments, the name of the library and the pattern are needed.")
    elif len(argv) == 3:
        library = argv[1]
        pattern = argv[2]

        source_folder = "/mansion/cavelazq/PhD/joint_tools/data/api_usages/original_data"
        source_file = "{}/{}.tsv".format(source_folder, library)

        target_folder = "/mansion/cavelazq/PhD/joint_tools/data/api_usages"
        target_file = "{}/{}.tsv".format(target_folder, library)

        json_folder = "/mansion/cavelazq/PhD/joint_tools/data/jsons"
        json_file = "{}/{}.json".format(json_folder, library)

        with open(json_file) as f:
            json_content = json.load(f)
            apis_library = list(json_content.keys())
        
        selected_lines = ""

        # Appending the contexts to the list
        with open(source_file) as f:
            line = f.readline() # Ignore the header line
            selected_lines += line + "\n"

            while True:
                line = f.readline()
                if not line:
                    break
                else:
                    line = line.strip()
                    line_divided = line.split("\t")

                    fqn = line_divided[-3]

                    # Check if the FQN is an array, matrix, etc
                    if fqn.endswith('[]'):
                        first_index = fqn.index('[')
                        fqn = fqn[:first_index]

                    if fqn in apis_library:
                        selected_lines += line + "\n"
                    else:
                        if not fqn.startswith(pattern):
                            selected_lines += line + "\n"

        with open(target_file, "w") as f:
            f.writelines(selected_lines)
