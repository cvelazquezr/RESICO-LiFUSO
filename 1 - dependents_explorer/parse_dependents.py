from sys import argv

def process_line(line: str):
    link = line.split("|")[1].strip()
    repo_name = link.split("/")[-2:]

    return "/".join(repo_name)


if __name__ == '__main__':
    if len(argv) < 2:
        print("Too few arguments, the name of the library is needed. Make sure there's a file with its name in the repositories folder.")
    elif len(argv) == 2:
        library = argv[1]

        source_folder = "/home/kmilo/Dev/PhD/features-lab/data/dependents"
        source_file = "{}/{}_dependents.txt".format(source_folder, library)

        target_folder = "/home/kmilo/Dev/PhD/features-lab/data/repositories"
        target_file = "{}/{}.txt".format(target_folder, library)

        lines = list()

        with open(source_file) as f:
            lines_raw = f.readlines()
            lines = list(map(lambda line: process_line(line.strip()), lines_raw))

        repository_names = set()

        # Writing repository names
        with open(target_file, "w") as f:
            for line in lines:
                f.write(line + "\n")
