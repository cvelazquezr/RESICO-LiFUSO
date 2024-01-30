from sys import argv


if __name__ == '__main__':
    if len(argv) < 2:
        print("Too few arguments, the name of the library is needed. Make sure there's a file with its name in the repositories folder.")
    elif len(argv) == 2:
        library = argv[1]

        source_folder = "/home/kmilo/Dev/PhD/features-lab/data/repositories"
        source_file = "{}/{}.txt".format(source_folder, library)

        target_folder = "/home/kmilo/Dev/PhD/features-lab/data/cleaned_repositories"
        target_file = "{}/{}.txt".format(target_folder, library)

        lines = list()

        with open(source_file) as f:
            lines_raw = f.readlines()
            lines = list(map(lambda line: line.strip(), lines_raw))

        repository_names = set()

        # Removing forks and duplicated repositories
        with open(target_file, "w") as f:
            for line in lines:
                repository_name = line.split("/")[1]

                if repository_name in repository_names:
                    continue
                else:
                    repository_names.add(repository_name)
                    f.write(line + "\n")
