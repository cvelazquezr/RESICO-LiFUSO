shinyUI(fluidPage(
    # Application title
    titlePanel("Configuration"),
    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
      sidebarPanel (
        selectInput(inputId = "library",
                    label = h4("Libraries:"),
                    choices = c("guava", "httpclient", "jfreechart", "jsoup", "pdfbox", "poi-ooxml", "quartz"),
                    size = 7,
                    selectize = F,
                    selected = "guava"
        ),
        actionButton(inputId = "books", label = "Generate Book"),
        actionButton(inputId = "evaluate", label = "Evaluate"),
      ),
      # Show a plot of the generated distribution
      mainPanel (
        tabsetPanel(
          tabPanel("Exploration",
                   div(
                     style = "position:relative",
                     highchartOutput(outputId = "clustersTreeMapUI") %>%
                       withSpinner(type = 7)
                   ),
                   textOutput(outputId = "distinctionCluster"),
                   tags$ul(
                     htmlOutput(outputId = "namesOutput")
                   ),
                   fluidRow(
                     column(4, align="center", tableOutput("frequentClasses"))
                   ),
                   fluidRow(
                     column(4, align="center", tableOutput("frequentMethods"))
                   ),
                   tags$ul(
                     htmlOutput(outputId = "titlesOutput")
                   )
          ),
          
          tabPanel("Summary",
                   br(),
                   
                   hr(),
                   h4("Metrics"),
                   hr(),
                   
                   textOutput(outputId = "silhouetteScore"),
                   textOutput(outputId = "numberClusters"),
                   htmlOutput(outputId = "popularClass"),
                   htmlOutput(outputId = "popularAPI"),
                   
                   hr(),
                   h4("Population Chart"),
                   hr(),
                   plotOutput(outputId = "populationChart")
                   )
        )
      )
    )
  )
)