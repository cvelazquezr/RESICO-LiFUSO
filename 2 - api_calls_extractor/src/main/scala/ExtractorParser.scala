import cats.implicits._
import com.monovore.decline._

object ExtractorParser extends CommandApp(
  name = "API Extractor",
  header = "Extracts the usages of libraries in GitHub repositories",
  main = {
    val libraryGroup = Opts.option[String]("groupID", help = "The library groupID")
    val libraryArtifact = Opts.option[String]("artifactID", help = "The library artifactID")
    val libraryPackagePattern = Opts.option[String]("pattern", help = "The library package pattern")
    val currentGithubRepository = Opts.option[Int]("githubRepo", help = "The current GitHub repository to mine")

    (libraryGroup, libraryArtifact, libraryPackagePattern, currentGithubRepository).mapN { (group, artifact, pattern, githubNumber) =>
      Extractor.configureAndExtract(group, artifact, pattern, githubNumber)
    }
  },
  helpFlag = true,
  version = "1.0"
)
