from pyspark.sql import SparkSession

def ends_star(statement):
    return statement.split(".")[-1] == "*"

def analyse_codes(code_list):
    imports = []

    for code_fragment in code_list:
        splitted_fragment = code_fragment.split("\n")
        lines_import = list(filter(lambda line: line.startswith("import"), splitted_fragment))

        # Analyse the import lines
        statements = []
        for line in lines_import:
            line_splitted = line.split(" ")

            if len(line_splitted) == 2:
                statements.append(line_splitted[1])

        for statement in statements:
            statement = statement.strip()

            if "." in statement:
                if ";" in statement:
                    index_semicolon = statement.index(";")
                    statement = statement[:index_semicolon]
                if not ends_star(statement):
                    imports.append(statement)
    return imports

print("Configuring Spark ...")
spark = SparkSession.builder \
    .master("local[*]") \
    .appName("RESICO") \
    .config("spark.cores.max", "8") \
    .config("spark.executor.memory", "250g") \
    .config("spark.driver.memory", "250g") \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "250g") \
    .config("spark.driver.maxResultSize", "250g") \
    .config("spark.sql.parquet.columnarReaderBatchSize", "2048") \
    .getOrCreate()
print("Done!")

print("Loading all Stack Overflow data ...")
dataset = spark.read.parquet("3-java_answers_vectors.parquet")
print("Done!")

print("Getting the import statements ...")
codes = [row.Codes for row in dataset.select("Codes").collect()]
import_statements = []

for code_list in codes:
    extracted_imports = analyse_codes(code_list)

    if len(extracted_imports) > 0:
        import_statements += extracted_imports

import_statements = list(set(import_statements))
print("Done!")

print("Writing the import statements to a local file ...")
with open("SO_imports.txt", "w") as f:
    for statement in import_statements:
        f.write(statement + "\n")
print("Done!")
