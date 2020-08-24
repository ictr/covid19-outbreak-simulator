#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)

library(ggplot2)
library(ggExtra)

plot_time_vs_size <- function(logfile, title, output) {
    data <- read.table(logfile, sep = "\t", header = 1)
    end_count <- data[data["event"] == "END", ]
    end_count$target <- as.numeric(as.character(end_count$target))


    p <- ggplot(end_count, aes(x = time, y = target)) +
        geom_point(size = 0.2, color = "slateblue") +
        theme(legend.position = "none") +
        xlab("Days") +
        ylab("Remaining Population Size") +
        ggtitle(paste0("\n", title))

    p1 <- ggMarginal(p,
        type = "histogram",
        xparams = list(bins = 120),
        yparams = list(bins = 64),
        fill = "slateblue",
        color = "slateblue"
    )

    ggsave(output, plot = p1)
}

plot <- plot_time_vs_size(logfile = args[1], title = args[2], output = args[3])
