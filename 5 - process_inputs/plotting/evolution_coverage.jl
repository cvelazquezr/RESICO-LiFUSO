using CSV, DataFrames, PlotlyJS

function main()
    library = "poi-ooxml"

    # File with the results
    results = DataFrame(CSV.File("/Users/kmilo/Dev/PhD/features-lab/data/percentage_usages/$library.csv"))

    # Fragment the results into multiple chunks of data
    length_data = size(results)[1]

    # Number of bars
    bars = 20

    # Size of each chunk
    chunk_size = Int64(ceil(length_data / bars))
    chunk_size_var = chunk_size

    # Split the data into chunks
    results_chunks_percentage = Array{Float64}(undef, bars) 
    results_chunks_delta = Array{Float64}(undef, bars)
    x_labels = Array{String}(undef, bars)

    index = 1
    i = 1
    flag = false

    while index < length_data
        chunk = results[index:chunk_size_var, :]
        # println(size(chunk))
        max_percentage = round(maximum(chunk[!, "percentage"]), digits=2)
        max_delta = round(maximum(chunk[!, "delta_increased"]), digits=2)

        results_chunks_percentage[i] = max_percentage
        results_chunks_delta[i] = max_delta

        if !flag
            x_labels[i] = "1-$(index + chunk_size - 1)"
        else
            x_labels[i] = "1-$length_data"
        end

        index += chunk_size
        chunk_size_var += chunk_size

        if chunk_size_var > length_data
            chunk_size_var = length_data
            flag = true
        end
        i += 1
    end

    # Plot the coverge through the repositories
    p = plot(
        bar(x=x_labels, y=results_chunks_percentage, text=results_chunks_percentage, textposition="outside"),
        Layout(title="Coverage Evolution Library: $library")
    )

    update_xaxes!(p, title="# Projects")
    update_yaxes!(p, title="API Coverage (%)")

    savefig(p, "/Users/kmilo/evolution-coverage-$library.pdf"; format="pdf", width=900, height=500)
end

main()
