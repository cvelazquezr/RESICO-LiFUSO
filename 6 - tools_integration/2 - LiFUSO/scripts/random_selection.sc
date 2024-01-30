import scala.util.Random.nextInt
import java.io.File

import $ivy.`commons-io:commons-io:2.10.0`
import org.apache.commons.io.FileUtils.copyFile


def copyUsages(sourceFolder: File, outFolder: File, number: Int): Unit = {
	val listFiles: Array[File] = sourceFolder.listFiles

	var repositoryNames: Array[String] = Array()
	var randomUsages: Array[File] = Array()

	while(repositoryNames.length < number) {
		val randomUsageIndex: Int = nextInt(listFiles.length)
		val randomUsageFile: File = listFiles(randomUsageIndex)

		val fileName: String = randomUsageFile.getName
		val repoName: String = fileName.split("_").last

		if (!repositoryNames.contains(repoName)) {
			repositoryNames :+= repoName
			randomUsages :+= randomUsageFile
		}
	}

	if (!outFolder.exists()) {
		outFolder.mkdirs()
	}

	randomUsages.foreach(file => {
		val toFile: File = new File(s"${outFolder.getAbsolutePath}/${file.getName}")


		copyFile(file, toFile)
	})

}

val inputFolder: File = new File("datasets/cleaned_usages/usages")
val outputFolder: File = new File("datasets/selected_usages/quartz")

copyUsages(inputFolder, outputFolder, 376)
