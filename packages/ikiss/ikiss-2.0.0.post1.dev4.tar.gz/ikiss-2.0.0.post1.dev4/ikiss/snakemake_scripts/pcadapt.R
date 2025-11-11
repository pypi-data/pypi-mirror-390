# Title     : PCAdapt
# Objective : run pcadapt by using kmers selected randomly
# Created by: Julie Orjuela UMR DIADE IRD
# Created on: 26/10/2021

#### Loading required packages #####
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library(Biostrings))

#### COMMAND LINE ARGUMENTS PARSING ######
option_list <- list(
  make_option(c("-e", "--bedFile"),
              type = "character",
              default = NULL,
              help = "Path of bed file"),
  make_option(c("-i", "--bimFile"),
              type = "character",
              default = NULL,
              help = "Path of bim file"),
  make_option(c("-a", "--famFile"),
              type = "character",
              default = NULL,
              help = "Path of fam file"),
  make_option(c("-o", "--outFilePath"),
              type = "character",
              default = NULL,
              help = "Path where output sequence file will be written."),
  make_option(c("-k", "--kmerList"),
              type = "character",
              default = NULL,
              help = "kmer list"),
  make_option(c("-x", "--pcaAxes"),
              type = "character",
              default = 2,
              help = "axes in PCA, 2 by default"),
  make_option(c("-c", "--correction"),
              type = "character",
              default = "FDR",
              help = "correction method to extrac kmers outliers"),
  make_option(c("-f", "--alpha"),
              type = "double",
              default = 0.1,
              help = "alpha cutoff for outlier detection")
)

##### RETRIEVEING PARAMS from optparse #####
myArgs <- parse_args(
  OptionParser(usage = "%prog [options]", option_list = option_list,
               description = "run PCAdapt R package over a subset of random kmers and a bed+bim+fam file"))

# assign parameter values
bed <- myArgs$bedFile
bim <- myArgs$bimFile
fam <- myArgs$famFile
out <- myArgs$outFilePath
kmer_list <- myArgs$kmerList
nb_axes_pca <- strtoi(myArgs$pcaAxes, base=0L)
alpha <- myArgs$alpha
correction <- myArgs$correction

# controling parametters
if(is.null(out)) out <- paste0(gsub("(^.*)\\..*$", "\\1", bedFile), "_pca.csv")
if (is.null(bed)) stop("bed file must be provided. Run program with '--help' for more info on usage.")
if (is.null(bim)) stop("bim file must be provided. Run program with '--help' for more info on usage.")
if (is.null(fam)) stop("fam file must be provided. Run program with '--help' for more info on usage.")

# loading R packages
library("BEDMatrix")
library("pcadapt")
library("stringr")
library("qvalue")

# finding suffix of _BH0.05.pcadapt_outliers.csv file
short_segment_name = sub(pattern = "(.*)_BH0.05.pcadapt_outliers.csv", replacement = "\\1", basename(out))
ss = str_split(short_segment_name, "_")
short_bed_name = paste (ss[[1]][1],"_",ss[[1]][2], sep = "")
segment_nb = ss[[1]][3]

# reading samples file from FAM file
file_to_pop = read.delim(fam, sep = ' ', header = FALSE)
# get nb of samples from samples.txt
nb_samples = length(file_to_pop[[1]])
# giving groups with names
samplelist.names <- unlist(file_to_pop[1])  #convert a row from a dataframe into a horizontal vector ! thanks @yves!
poplist.names <- unlist(file_to_pop[6])

# create a BEDMatrix object the example .bed file
m <- BEDMatrix(bed)

########################## PCA ##############################
# extraction of random kmers found in segment file
kl <- scan(kmer_list)
# data table containing random kmers (extraction by kmer name (number)
kmer_names_list=sort(kl) # kmer number by segment
# reduction de la matrix bedmatrix
s = m[1:nb_samples, sort(kl)]
# PCA with the reduited bedmatrix s
acp <- read.pcadapt(s, type = "lfmm")

pcadapt = pcadapt(input = acp, K = nb_axes_pca)
#attributes(pcadapt)

########################## PLOTS ##############################
# Screen plot
fileplot <- str_replace(out, "_outliers.csv", ".rplot.pdf")
pdf(file=fileplot)
#plot(pcadapt, option = "screeplot")
### score plot
plot(pcadapt, option = "scores", i = 1, j = 2, pop = poplist.names)
#plot(pcadapt, option = "scores", i = 1, j = 2, pop = samplelist.names)
### A Manhattan plot displays −log10 of the p-values.
plot(pcadapt , option = "manhattan", i=1, j=2)
### The user can also check the expected uniform distribution of the p-values using a Q-Q plot
plot(pcadapt, option = "qqplot", i=1, j=2)
### An histogram of p-values confirms that most of the p-values follow an uniform distribution.
### The excess of small p-values indicates the presence of outliers.
hist(pcadapt$pvalues, xlab = "p-values", main = NULL, breaks = 50, col = "orange")
### The presence of outliers is also visible when plotting a histogram of the test statistic 𝐷𝑗.
plot(pcadapt, option = "stat.distribution")


########################## LOADINGS ##############################
pcadapt_cw <- pcadapt(acp, K = nb_axes_pca, method = "componentwise")
plot(pcadapt_cw, option = "stat.distribution", K = nb_axes_pca)
dev.off()
# showing loadings, recovery pvalues matrix
length(pcadapt_cw$pass)
pvalues=pcadapt$pvalues

## Choosing a cutoff for outlier detection
if (correction == 'BONFERONNI')
  {
  ## E.3. Bonferroni correction
  padj <- p.adjust(pvalues, method="bonferroni")
  alpha <- alpha
  outliers <- which(padj < alpha)
  }
if (correction == 'BH') {
  ## E.2. Benjamini-Hochberg Procedure
  padj <- p.adjust(pvalues, method="BH")
  #print (head(padj))
  alpha <- alpha
  outliers <- which(padj < alpha)
}
if (correction == 'FDR') {
  ## E.1. q-values
  qval <- qvalue(pvalues)$qvalues
  alpha <- alpha
  outliers <- which(qval < alpha)
}

### Association between PCs and outliers
## get.pc returns a data frame such that each row contains the index of the genetic
## marker and the principal component the most correlated with it. => thanks @tram
kmer_pc = get.pc(pcadapt, outliers)
klist = list()
for (i in 1:length(kmer_pc$SNP))
  klist <- append(klist, colnames(acp)[kmer_pc$SNP[i]])
kmer_pc$klist <- klist

####### recovey pvalues matrix !!!
# getting a output name to rescue pvalues and scores
filepvalues = str_replace(out, "_outliers.csv", "_pvalues.csv")
filescores = str_replace(out, "_outliers.csv", "_scores.csv")

#print ("====================> FILENAME VECTOR AND SEGMENT")
# doing a vector including original file bed and segment name
filename_vector = rep(c(short_bed_name),times=(length(colnames(acp))))
segment_vector = rep(c(segment_nb),times=(length(colnames(acp))))

# doing a dataframe containing the sequence of kmer, number and file origin as well as pvalues info, use to output
df = data.frame(filename_vector, segment_vector, kmer_names_list, colnames(acp), pcadapt_cw$pvalues )
# changing names to col of df
names(df) = c("bedname", "segment_nb", "kmer_number","sequence","pvalue.X1","pvalue.X2")
names(kmer_pc) = c("kmer_number","PC", "sequence" )

# merging by sequence
mergedf <- merge(df, kmer_pc , by="sequence")
names(mergedf) = c("sequence", "bedname", "segment_nb", "kmer_number","pvalue.X1","pvalue.X2", "kmer_number_index_get.pc", "PC")

### Writing kmer name, sequence and pvalue file from all kmers in segment
write.table(df, filepvalues, quote = FALSE, sep="\t")

### Writing outlier kmers with merged information from df kmer sequence and pvalues
write.table(mergedf, out, quote = FALSE, sep = "\t")

### Writing scores in a file
write.table(pcadapt$scores, filescores, quote = FALSE, sep = "\t")
