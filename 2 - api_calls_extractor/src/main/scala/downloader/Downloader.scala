package downloader

import requests.Response

class Downloader(groupID: String, artifactID: String, jarsFolder: String):

  val MAVEN_ADDRESS: String = "https://repo1.maven.org/maven2/"

  def downloadAllJARs(): Unit =
    val versions = scrap()
    versions.foreach(version => {
      println(s"Analysing triplet $groupID -> $artifactID -> $version")

      // Download the JAR file with a triple combination
      val jarFile = new JARFile(groupID, artifactID, version)
      val pathJarStr: String = jarFile.pathJar()
      val path: String = s"$jarsFolder/" + pathJarStr
      jarFile.downloadJar(path, MAVEN_ADDRESS + pathJarStr)
    })

  private def scrap(): List[String] =
    val url: String = "https://search.maven.org/solrsearch/select?q=g:%22" + groupID + "%22%20AND%20a:%22" +
      artifactID + "%22&core=gav&rows=200&wt=json"
    val response: Response = requests.get(url)

    if response.statusCode == 200 then
      val jsonData = ujson.read(response.text())

      jsonData("response")("docs") match
        case array: ujson.Arr => 
          array.arr.toArray.map(document => document("v").value.toString).toList
        case _ => List()
    else List()
  
