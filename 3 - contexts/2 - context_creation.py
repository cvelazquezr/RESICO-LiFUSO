import pandas as pd
from sys import argv

class API_Element(object):
    def __init__(self, usage, fqn):
        self.usage = self.replace_characters(usage)
        self.fqn = fqn
        self.context = ""

    def add_context(self, context_data):
        self.context = context_data

    def replace_characters(self, word):
        not_dots = word.replace(".", "|")

        return not_dots

    def __str__(self):
        return self.usage + "\t" + self.context + "\t" + self.fqn + "\n"


if __name__ == '__main__':
    if len(argv) < 3:
        print("Too few arguments, the name of the library and its package pattern are needed.")
    elif len(argv) == 3:
        library = argv[1]
        pattern = argv[2]

        source_folder = "/mansion/cavelazq/PhD/joint_tools/data/api_usages"
        source_file = "{}/{}.tsv".format(source_folder, library)

        target_folder = "/mansion/cavelazq/PhD/joint_tools/data/csv"
        target_file = "{}/{}.tsv".format(target_folder, library)

        # Appending the contexts to the list
        data = pd.read_csv(source_file, sep="\t")
        data = data.dropna()

        contexts = {}
        key = ""

        for _, row in data.iterrows():
            current_method = ""
            current_location = ""
                    
            method = row.method_name
            file_location = row.file_location
            api_usage = row.api_usage
            fqn = row.fqn

            element = API_Element(api_usage, fqn)

            if method != current_method and current_location != file_location:
                key = method + "|" + file_location

            if key in contexts:
                contexts[key].append(element)
            else:
                contexts[key] = [element]

            current_method = method
            current_location = file_location

        data_to_write = "api\tcontext\tfqn\n"

        # Adding the contexts to the elements
        for index, (method_name, context) in enumerate(contexts.items()):
            if (index + 1) % 100_000 == 0:
                print("Processing method {} / {} ...".format(index + 1, len(contexts)))
            
            elements = list(filter(lambda el: el.fqn.startswith(pattern), context))

            if len(elements) > 0:
                index_patterns = [index_context for index_context, element_context in enumerate(context) if element_context in elements]

                for index_element, element in zip(index_patterns, elements):
                    elements_context = context[:index_element] + context[index_element:]
                    usage_elements = list(map(lambda e : e.usage, elements_context))
                    context_generated = "|".join(usage_elements)

                    element.add_context(context_generated)

                    data_to_write += str(element)

        with open(target_file, "w") as f:
            f.writelines(data_to_write)
