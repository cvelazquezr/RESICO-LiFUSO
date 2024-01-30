import java.io.{File, PrintWriter}
import scala.io.Source


def join_distill(folderPath: File, fileOut: File): Unit = {
	val filesFolder: Array[File] = folderPath.listFiles

	var usagesFolder: Array[Array[String]] = Array()

	filesFolder.foreach(file => {
		val sourceFile: Source = Source.fromFile(file)
		val linesSource: Array[String] = sourceFile.getLines.toArray

		usagesFolder :+= linesSource

		sourceFile.close
	})

	val usagesLines: Array[String] = usagesFolder.flatten.distinct

	val pw: PrintWriter = new PrintWriter(fileOut)
	usagesLines.foreach(line => pw.write(line + "\n"))
	pw.close
}

val library: String = "quartz"

val inputFolder: File = new File(s"datasets/selected_usages/$library")
val outputFile: File = new File(s"datasets/selected_usages/${library}_joined.txt")

join_distill(inputFolder, outputFile)

