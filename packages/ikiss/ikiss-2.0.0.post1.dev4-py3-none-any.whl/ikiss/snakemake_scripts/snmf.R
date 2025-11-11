# Title     : SNMF
# Objective : run snmf by using kmers selected randomly
# Created by: Tram VI and modify by Julie Orjuela UMR DIADE IRD
# Created on: 01/2024
# SNMF estimates admixture coefficients using sparse Non-Negative Matrix Factorization algorithms, and provide STRUCTURE-like outputs

#### Loading required packages #####
suppressPackageStartupMessages(library("optparse"))

# loading R packages
library("BEDMatrix")
library("lfmm")
library("rlist")
library("stringr")
library('qvalue')
library('LEA')
library('tidyr')
library('stringi')
library('ggplot2')

set.seed(987654321)

#### COMMAND LINE ARGUMENTS PARSING ######
option_list <- list(
  make_option(c("-e", "--bedFile"),
              type = "character",
              default = NULL,
              help = "Path of bed file"),
  make_option(c("-k", "--kmerList"),
              type = "character",
              default = NULL,
              help = "kmer list"),
  make_option(c("-i", "--kmin"),
              type = "integer",
              default = 2,
              help = "Numbers of minimal ancestral populations K"),
  make_option(c("-a", "--kmax"),
              type = "integer",
              default = 6,
              help = "Numbers of maximal ancestral populations K"),
  make_option(c("-r", "--repetitions"),
              type = "integer",
              default = 2,
              help = "Numbers of ancestral populations K"),
  make_option(c("-j", "--best_k"),
              type = "integer",
              default = 2,
              help = "Numbers of best ancestral populations K"),
  make_option(c("-o", "--outFilePath"),
              type = "character",
              default = NULL,
              help = "Path where admixture proportion will be written."),
  make_option(c("-t", "--threads"),
              type = "integer",
              default = 8,
              help = "threads used by snmf"),
  make_option(c("-n", "--name_project"),
              type = "character",
              default = "snmf",
              help = "project name to save R snmf object")
)

myArgs <- parse_args(
OptionParser(usage = "%prog [options]", option_list = option_list,
               description = "run SNMF R package over a subset of random kmers and a bed bim fam file")
               )

# assign parameter values
bed <- myArgs$bedFile
kmer_list <- myArgs$kmerList
out <- myArgs$outFilePath
kmin <- myArgs$kmin
kmax <- myArgs$kmax
repetitions <- myArgs$repetitions
best_k <- myArgs$best_k
threads <- myArgs$threads
name_project <- myArgs$name_project

# controling parametters
if (is.null(bed)) stop("bed file must be provided. Run program with '--help' for more info on usage.")
if (is.null(kmer_list)) stop("kmer list file must be provided. Run program with '--help' for more info on usage.")

### read a random kmer set
matrix <- BEDMatrix(bed, simple_names = T)
kl <- scan(kmer_list)
# reduction de la matrix bedmatrix
genotype = matrix[, sort(kl)]

############# SNMF ##############
snmf_dir <- file.path(".", name_project)

dir.create(snmf_dir, showWarnings = F)
geno_file <- file.path(out)
write.geno(genotype, geno_file)

snmf_kmer <- snmf(geno_file, K = kmin:kmax, CPU = threads, repetitions = repetitions, project = "new", entropy = T)
# plot cross-entropy criterion for all runs in the snmf project
fileplot <- str_replace(out, ".geno", ".snmf.pdf")

pdf(file=fileplot)
# plot cross-entropy criterion of all runs of the project
plot(snmf_kmer, pch = 16, cex = 1.2, col = "lightblue")

## choose best run based on cross entropy
k <- best_k
best_run <- which.min(cross.entropy(snmf_kmer, K = k))
#best_run

## plot ancestry proportion
#ind_order_kmer <- LEA::barchart(snmf_kmer, K = k, run = best_run, plot = T)

my.colors <- c("tomato", "lightblue", "olivedrab", "gold")
barchart(snmf_kmer, K = k, run = best_run,
        border = NA, space = 0, col = my.colors,
        xlab = "Individuals", ylab = "Ancestry proportions",
        main = "Ancestry matrix") -> bp

axis(1, at = 1:length(bp$order),
      labels = bp$order, las = 3,
      cex.axis = .4)

dev.off()