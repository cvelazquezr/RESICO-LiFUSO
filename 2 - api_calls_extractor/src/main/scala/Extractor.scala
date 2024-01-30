import scala.io.Source
import scala.sys.process._
import downloader.Downloader

import java.io.{File, FileWriter, BufferedWriter}
import com.parser.extractor.api.{ExtractorAPI, ExtractorContextAPI}
import upickle.default._
import java.io.File

object Extractor:
  def getAPIsLibrary(pathJSONPath: String): List[String] =
    val mappedAPIs: Map[String, List[String]] = read[Map[String, List[String]]](new File(pathJSONPath))
    mappedAPIs.map((fqn, methods) => {
      val namesUpper = methods.filter(name => name(0).isUpper)
      val namesLower = methods.filter(name => name(0).isLower)

      val className = fqn.split("\\.").last
      val appendixNames = namesLower.map(name => s"$className.$name")

      namesUpper ++ appendixNames
    }).toList.flatten

  /*** Computes the coverage of the library given by the number of APIs extracted
  ***/
  def computePercentageLibrary(lines: List[String], apisLibrary: List[String], matchedAPIs: Array[Boolean], indexAPI: Int = 4): (Array[Boolean], Double) = 
    // Gets the API call
    val usages = lines.map(line => line.split("\t")(indexAPI))

    // Checks if the call is within the library's calls
    val usagesAPIs = usages.filter(usage => apisLibrary.contains(usage))

    // Gets the indexes of the library's calls
    val indexMatched = usagesAPIs.map(apisLibrary.indexOf(_))

    // Sets the extracted indexes to true
    indexMatched.foreach(index => matchedAPIs(index) = true)

    // Counts the true indexes and calculates the percentage w.r.t the total
    val numberMatches = matchedAPIs.count(e => e).toDouble
    val percentage = (numberMatches / matchedAPIs.length.toDouble) * 100.0

    (matchedAPIs, percentage)


  def modifyLines(lines: List[String]): List[String] =
    lines.map(line => {
      val dividedLine = line.split("\t")
      val modifiedUsage = removeTypeParams(dividedLine(4))
      val modifiedFQN = removeTypeParams(dividedLine(5))

      dividedLine.update(4, modifiedUsage)
      dividedLine.update(5, modifiedFQN)

      dividedLine.mkString("\t")
    })


  def removeTypeParams(token: String): String =
    if token.contains("<") then
      val indexFirstBracket = token.indexOf("<")
      val indexLastBracket = token.length() - token.reverse.indexOf(">")

      val firstPart = token.slice(0, indexFirstBracket)
      val secondPart = token.slice(indexLastBracket, token.length())

      firstPart + secondPart
    else
      token


  def getCommitHash(repositoryPath: String): String =
    val branchSource = Source.fromFile(new File(s"$repositoryPath/.git/HEAD"))

    val branchFull = branchSource.getLines.toList.head
    val branchName = branchFull.split("/").last

    val headsSource = Source.fromFile(new File(s"$repositoryPath/.git/refs/heads/$branchName"))
    val commitHash = headsSource.getLines.toList.head.trim

    headsSource.close
    branchSource.close

    commitHash

  def configureAndExtract(libraryGroupID: String, libraryArtifactID: String, pattern: String, githHubNumber: Int): Unit =
    val GITHUB_URL = "https://github.com"
    val DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
    val FOLDER_REPOSITORIES = s"$DATA_FOLDER/cleaned_repositories"
    val CLONED_REPOSITORIES_FOLDER = s"$DATA_FOLDER/cloned_repositories"
    val APIS_FOLDER = s"$DATA_FOLDER/jsons"
    val JARS_FOLDER = s"$DATA_FOLDER/jars"
    val JARS_LIBRARY = s"$JARS_FOLDER/${libraryGroupID.replaceAll("\\.", "/")}/$libraryArtifactID"

    val API_USAGES = s"$DATA_FOLDER/api_usages/$libraryArtifactID.tsv"

    println("Downloading the JAR files from all versions ...")
    val downloader = new Downloader(libraryGroupID, libraryArtifactID, JARS_FOLDER)
    downloader.downloadAllJARs()
    println("Done!")

    println("Reading the APIs from the library ...")
    val libraryAPIs = getAPIsLibrary(s"$APIS_FOLDER/$libraryGroupID-$libraryArtifactID.json")
    println("Done!")

    val sourceLibraries = Source.fromFile(s"$FOLDER_REPOSITORIES/$libraryArtifactID.txt")
    val repositories = sourceLibraries.getLines

    var firstRepository = true
    if githHubNumber > 0 then
      firstRepository = false

    var percentageAPIs = 0.0
    var matchedAPIs = Array.fill[Boolean](libraryAPIs.length)(false)

    if !firstRepository then
      println("Calculating the percentage of APIs extracted so far ...")
      // Reads the written file and calculates the percentage based on the stored information
      val sourceFile = Source.fromFile(API_USAGES)
      val currentLines: List[String] = sourceFile.getLines().toList.drop(1) // Dropping the header row

      // Calculates the percentage based on the file
      val (matchedAPIsFile, percentageAPIsFile) = computePercentageLibrary(currentLines, libraryAPIs, matchedAPIs, 7)
      matchedAPIs = matchedAPIsFile
      percentageAPIs = percentageAPIsFile

      println(s"Percentage of the APIs in the library covered until now: $percentageAPIs")

      // Closes the file
      sourceFile.close()

    repositories.drop(githHubNumber).foreach(repository => {
      val repositoryName = repository.split("/").last

      // Checking whether the repository exists
      println(s"Checking the existence of the repository $repository ...")
      var shouldCloneRepository = true

      try
        requests.get(s"$GITHUB_URL/$repository")
      catch
        case _: Exception => shouldCloneRepository = false

      println("Done!")

      // Clone the repositories
      if shouldCloneRepository then
        var raisedException = false
        var LATEST_COMMIT_HASH = ""

        println(s"Cloning the repository $repository ...")
        val repositoryAddress = s"$GITHUB_URL/$repository"
        val destinationFolder: String = s"$CLONED_REPOSITORIES_FOLDER/$repositoryName"

        // Git needs to be installed on the system
        val output = Seq("git", "clone", repositoryAddress, destinationFolder).!
        println("Done!")

        // Extracting the information from the project
        if output == 0 then
          var parseException = false

          try
            LATEST_COMMIT_HASH = getCommitHash(destinationFolder)
          catch
            case _: Exception => raisedException = true

          if !raisedException then
            println("Processing the Java files in the project ...")

            var informationExtracted: List[String] = List()

            try
              val arrayInfoExtracted = ExtractorAPI.extractInformation(destinationFolder, JARS_LIBRARY, pattern, true)
              arrayInfoExtracted.forEach(information => informationExtracted :+= information)
            catch
              case _: Exception => parseException = true

            println("Done!")

            if !parseException then
              if informationExtracted.nonEmpty then
                val executeMaven = Seq("/bin/sh", "-c", 
                  s"cd $destinationFolder && mvn dependency:copy-dependencies -DoutputDirectory=$JARS_FOLDER/projectJars")

                (executeMaven).!

                var allInformationExtracted: List[String] = List()

                try
                  val arrayInfoExtracted = ExtractorContextAPI.extractInformation(destinationFolder, JARS_LIBRARY, pattern)
                  arrayInfoExtracted.forEach(information => allInformationExtracted :+= information)
                catch
                  case _: Exception => parseException = true
                
                // Checking for possible type params and removing them
                val informationModified = modifyLines(allInformationExtracted)

                println("Saving the gathered information to a file ...")
                val writer = new BufferedWriter(new FileWriter(API_USAGES, true))

                if firstRepository then
                  writer.write("project_name\tcommit_hash\taccessed_on\tfile_location\tmethod_name\tstart_method_line\tend_method_line\tapi_usage\tfqn\tapi_line\ttype\n")
                  firstRepository = false

                // Writing the gathered information
                println(s"Number of APIs extracted: ${informationModified.length}")

                // Check all APIs with the information extracted so far
                val (matchedAPIsReturned, percentageAPIsReturned) = computePercentageLibrary(informationModified, libraryAPIs, matchedAPIs)
                matchedAPIs = matchedAPIsReturned
                percentageAPIs = percentageAPIsReturned

                println(s"Percentage of the APIs in the library covered: $percentageAPIs")
                
                informationModified.foreach(extractedLine => {
                  writer.write(s"$repository\t$LATEST_COMMIT_HASH\t${java.time.LocalDate.now.toString}\t$extractedLine\n")
                })
                writer.close()
              else
                println("No APIs were extracted")

              println("Done!")
              println()

          // Delete the folder
          println("Deleting ...")
          Seq("rm", "-rf", destinationFolder).!
          Seq("rm", "-rf", s"$JARS_FOLDER/projectJars").!
          println("Done!")
    })

    sourceLibraries.close()
