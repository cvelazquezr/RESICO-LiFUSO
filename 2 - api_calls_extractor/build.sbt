name := "api_calls_extractor"
version := "1.0"
scalaVersion := "3.1.1"

libraryDependencies ++= Seq(
  // Utilities
  "com.monovore" %% "decline" % "2.3.0",
  "com.lihaoyi" %% "upickle" % "2.0.0",
  "com.lihaoyi" %% "requests" % "0.7.1",
  "commons-io" % "commons-io" % "2.11.0"
)

Compile / unmanagedJars += file("lib/eclipse_jdt_statement_parser.jar")
