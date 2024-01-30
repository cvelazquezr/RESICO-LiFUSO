<h1 align="center"> Features Lab for Libraries in Maven </h1>

### Introduction

This is the features' laboratory where features can be extracted from libraries in the Maven software ecosystem.
To extract the features from the libraries, first, an extraction phase from their usages is needed and later model training phase on those usages.
These steps are required to assist in the extraction of usages from Stack Overflow (SO) code snippets.
SO snippets are the target of extraction since they have been previously "curated" by the software community, and they provide natural language information which can be further used to describe the extracted features.
After the extraction and training phases, a resolution phase is required where all usages from the libraries as well as their natural language companions are extracted from all code snippets in the SOTorrent dataset.
Finally, our LiFUSO tool will form clusters out of the extracted usages, it will propose named features to the final selection of the clusters to lastly include the features into the visual interface of the tool.

### Steps to follow

This project contains several subprojects for every step described above.
The following is a list describing the order you should follow in case you desire to include more libraries into the analysis and further exploration.

1. **Mine the usages of a library from GitHub repositories:** The folder `1 - dependents_explorer/` contains the necessary scripts to explore potential GitHub repositories using a library. More specifically, the mined projects are those including the library in analysis as part of their dependencies, which doesn't necessarily mean they use it, for example, could be a case of 'bloated' dependencies. The script `explorer.py` requires two arguments, the first one is the name of the library in the analysis and the second one is the URL of the library dependents. This URL can be extracted by accessing the GitHub repository of the library and adding `network/dependents` to that link. A new webpage should appear showing a list of dependent GitHub repositories. In the case that a dropdown appears with libraries in the same family, please select the one with the correct coordinates (i.e., groupID and artifactID):

2. **Cleaning the dependents projects:** Once the projects are mined from the list of dependents repositories in GitHub, a file with the name of the library will be created in `data/repositories`. However, before further exploration within these repositories, it is necessary to remove all forks from the list. This is done by running the script `clean_repositories.py`. The cleaned results are stored in the folder `data/cleaned_repositories` with the same name of the library in the analysis.

3. **Extraction of API usages from the cleaned repositories:** Filtered repositories are used to extract API usages (i.e., method calls, class instantiations and variable usages) from the code. In this case, the Scala project `api_calls_extractor` was developed to extract and store the following information: *project_name, commit_hash, accessed_on, file_location, method_name, start_method_line, end_method_line, api_usage, fqn, api_line, type*. All fields are self-explanatory, except the last that might need some brief explanation. *fqn* refers to the Fully-Qualified Name (FQN) of the API usage, for example `org.apache.pdfbox.multipdf.PDFMergerUtility` for the simple name `PDFMergerUtility`. *api_line* indicates the line number of the API usage in the file where it is used. *type* is the kind of usage of the API (e.g., VariableDeclaration, MethodDeclaration of VariableUsage). This project is a CLI application and can be executed as follows:

```
sbt assembly
java -jar target/scala-scala_version/api_calls_extractor-assembly-1.0.jar --groupID library.groupID --artifactID libraryArtifactID
```

Two arguments are accepted here, namely groupID and artifactID. A more real example of this would be:

```
sbt assembly
java -jar target/scala-scala_version/api_calls_extractor-assembly-1.0.jar --groupID org.apache.pdfbox --artifactID pdfbox
```

With the given coordinates the project will download all versions from the Maven central repository, clone the repositories from GitHub, explore all Java files in the projects, more specifically it will extract usages at the method level using Eclipse JDT, and finally it will save the previously described information as a TSV file in the folder `data/api_usages` with the name of the library. We selected the format TSV for the API usages file since some fqns and api_usages might contain commas which adds some issues for parsing.

4. **Contexts creation:** Extracted API usages allow the creation of contexts around them. The context creation represents a fundamental part of the classifier training and evaluation. The context surrounding an API usage at the method level is formed by concatenating the other API elements which are in the same method. The script `contexts/context_creation.py` assists in the generation of contexts. The name of the library in analysis is passed as argument to this script. The file with the API usages has to be present in the folder 'data/api_usages' for this script to work successfully. 
A new TSV file is created in `data/csv` containing the API usages, their context and their fully-qualified names.

5. **Model training, hyperparameter tuning and saving:** SO code snippets are often incomplete about the type of the variables or the FQNs of the simple names of API classes invoking methods. Regardless of their incompleteness, SO snippets contain valuable natural language information about the API usages which remain unexploited in general. Therefore, this step trains a model on the previous collected information about the context of API usages, tune the hyperparameters to select the optimal model and save the optimal model as well as the simple names of the *fqns* for further conflict analysis. In this case, two word2vec models are trained on the API usages and on the contexts, the *fqns* to predict remain as are. 

6. **Integration of approaches:** The integration of our approach for type resolution _RESICO_ and our feature uncovering approach _LiFUSO_ can be found in the `6 - tools_integration` folder. There, the project `1 - similarity_extractor` extracts the similarity matrices from the code snippets for each library needed to apply LiFUSO and uncover the features from the libraries. A second folder called `2 - LiFUSO` contains our approach for uncovering the features from API usage on Stack Overflow posts with the newly added data (e.g., in the folder `datasets/input/new`) from the previous processing pipelines.
