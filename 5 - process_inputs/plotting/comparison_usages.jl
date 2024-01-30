using CSV, DataFrames, PlotlyJS

# File with the results
results = DataFrame(CSV.File("/Users/kmilo/Dev/PhD/features-lab/data/percentage_usages/results.csv"))

# Plot the results
p = plot([
    bar(name="Coverage-50KC(%)", x=results[!, "Library"], y=results[!, "Coverage-50KC(%)"], text=results[!, "Coverage-50KC(%)"], textposition="outside"),
    bar(name="Coverage-GitHub(%)", x=results[!, "Library"], y=results[!, "Coverage-GitHub(%)"], text=results[!, "Coverage-GitHub(%)"], textposition="outside")
])

update_xaxes!(p, title="Libraries")
update_yaxes!(p, title="API Coverage (%)")
savefig(p, "/Users/kmilo/comparison-coverage.pdf"; format="pdf", width=900, height=500)
