name         := "similarity_extractor"
version      := "0.1"
scalaVersion := "3.3.0"

libraryDependencies ++= Seq(
  // Utilities
  "com.lihaoyi" %% "requests"   % "0.8.0",
  "com.lihaoyi" %% "ujson"      % "3.1.2",
  "com.lihaoyi" %% "upickle"    % "3.1.2",
  "commons-io"   % "commons-io" % "2.13.0",

  // Read the CSVs
  "org.apache.commons" % "commons-csv" % "1.10.0",

  // Extract information from JARs
  "org.apache.bcel" % "bcel" % "6.7.0",

  // Extract code from HTML
  "org.jsoup" % "jsoup" % "1.16.1",

  // NLP Operations
  "org.apache.opennlp" % "opennlp-tools"    % "2.2.0",
  "edu.stanford.nlp"   % "stanford-corenlp" % "4.5.4",
  "edu.stanford.nlp"   % "stanford-corenlp" % "4.5.4" classifier "models",

  // DeepLearning4j
  "org.deeplearning4j" % "deeplearning4j-core" % "1.0.0-M2.1",
  "org.deeplearning4j" % "deeplearning4j-nlp"  % "1.0.0-M2.1",
  "org.nd4j"           % "nd4j-native"         % "1.0.0-beta7",

  // No logs
  "org.slf4j" % "slf4j-nop" % "2.0.7"
)
