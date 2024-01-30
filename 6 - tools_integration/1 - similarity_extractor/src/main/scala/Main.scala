import api_extraction.API_Extraction_Island
import dictionary.Dictionary
import utils.{API_Usage_Code, API_Usage_Text, FileOperations, Library, VectorAnalysis}
import org.apache.commons.csv.{CSVFormat, CSVParser}
import text_analysis.{PredefinedModels, TextAnalysis, TypedDependencies}

import java.io.{File, FileReader}
import scala.collection.mutable.{Map => MMap}
import scala.io.Source
import upickle.default._
import versions.ScrapVersions

object Main extends App:
  // Defining a library as example
  val library: Library = Library(groupID = "com.google.guava",
    artifactID = "guava")

  // Folder where the artifacts are going to be downloaded
  val DATA_FOLDER: String = "/home/kmilo/Dev/PhD/features-lab/data/"

  // Obtaining the versions of a library
  val scrapper: ScrapVersions = new ScrapVersions(library)
  val libraryVersions: Library = scrapper.scrap()

  // Extracting information from the artifacts as a dictionary
  val dictionary: Dictionary = new Dictionary(library = libraryVersions, dataFolder = DATA_FOLDER)
  dictionary.createDictionary()

  // Reading dictionary
  val sourceDictionary: Source = Source.fromFile(s"$DATA_FOLDER/dictionaries/${library.groupID}" +
    s"|${library.artifactID}.json")
  val informationLibrary: String = sourceDictionary.getLines().mkString("")

  val dictionaryLibrary: MMap[String, Array[String]] = read[MMap[String, Array[String]]](informationLibrary)
  sourceDictionary.close()

  // Read CSV of posts from Stack Overflow
  val csvReader = new FileReader(s"$DATA_FOLDER/so_data/libraries/${library.artifactID}.csv")
  val builder = CSVFormat.Builder.create()
  val formatFile = builder.setHeader("AnswerID", "PostTitle", "AnswerBody", "WithTags").build()

  val parser: CSVParser = CSVParser.parse(csvReader, formatFile)

  // Loading predefined models
  val (posTaggerModel, dictionaryLemmatizer) = PredefinedModels.lemmatization()

  // Form the corpus of words which is then going to be converted into vectors
  var apiUsagesText: Array[API_Usage_Text] = Array()
  var apiUsagesCode: Array[API_Usage_Code] = Array()

  // Make a bag of words per vector which will point out in the direction of a cluster name in
  // later phases of the processing
  var vectorBoW: Array[List[String]] = Array()
  var informationUser: Array[(String, String, String)] = Array()

  parser.forEach(record => {
    // Input for Code Extraction
    val answerBody: String = record.get("AnswerBody")
    val answerID: String = record.get("AnswerID")
    val postRelatedTags: String = record.get("WithTags")

    // API Extraction from the Question Body
    // If there are usages matching the dictionary of public classes and methods, then
    // The text analysis will have to be performed, otherwise the answer should be excluded
    val codesAnswerBody: List[String] = API_Extraction_Island.extractCode(answerBody)

    if codesAnswerBody.nonEmpty then
      val singleSnippet: String = codesAnswerBody.mkString("\n")

      // Checking all types of code snippets with and without `imports`
      val usagesSnippet: List[String] = API_Extraction_Island.extractAPIs(singleSnippet)

      if usagesSnippet.nonEmpty then 
        // If usages are extracted from the parser
        // Filtering usages extracted in the dictionary (only class names are checked here)
        val usagesLibrary: List[String] = usagesSnippet.map(_.trim).filter(
          usage => {
            val receiverName: String = usage.split("\\.").head
            dictionaryLibrary.keys.toList.contains(receiverName)
        })

        if usagesLibrary.nonEmpty then
          // if postRelatedTags.equals("Y") then
          // Input for Text Extraction
          val title: String = record.get("PostTitle")

          // API Usages Code
          val apiUsageCode: API_Usage_Code = new API_Usage_Code(usagesLibrary)

          apiUsagesCode :+= apiUsageCode

          val relevantWordsTitle: List[String] = TypedDependencies.getRelevantWords(
            title, library.artifactID, isTitle = true)

          val relevantWordsABody: List[String] = TypedDependencies.getRelevantWords(
            TextAnalysis.extractBodyNoCode(answerBody).mkString(" "), library.artifactID)

          val bows: List[String] = relevantWordsTitle.concat(relevantWordsABody)
          informationUser :+= (title, s"https://stackoverflow.com/questions/$answerID", postRelatedTags)

          // If there are empty lines in the names, replaced them with <EMPTY>
          if bows.isEmpty then 
            vectorBoW :+= List("<EMPTY>")
          else
            vectorBoW :+= bows
  })

  val usagesCode: List[API_Usage_Code] = apiUsagesCode.toList
  var similarities: Array[Array[Double]] = VectorAnalysis.jaccardSimilarity(usagesCode)

  // Existence of folder to store combinations, in this case, just one type of combinations given previous results
  val combinationsFolder: String = s"$DATA_FOLDER/combinations/${library.artifactID}/apis"
  val combinationsFolderFile: File = new File(combinationsFolder)

  if !combinationsFolderFile.exists() then
    val response = combinationsFolderFile.mkdirs()
    if response then println("Directory created!") else println("Directory creation failure!")

  // Export as files to analyse in RStudio
  FileOperations.writeSimilaritiesTxt(similarities, s"$combinationsFolder/similarity_matrix.csv")
  FileOperations.writeCodeUsagesTxt(usagesCode.map(_.bows), s"$combinationsFolder/code_usages.txt")
  FileOperations.writeNameCandidates(vectorBoW, s"$combinationsFolder/name_candidates.txt")
  FileOperations.writeUserInformation(informationUser, s"$combinationsFolder/extra_information.txt")
  FileOperations.writePath(library.groupID, library.artifactID, s"$DATA_FOLDER/combinations/${library.artifactID}/path.txt")

  println("Done!")
