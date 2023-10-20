**KmerExploR** visualization of your RNA-seq basic features is separated into several sections/subsections:

**Basic Features**


* Poly A / Ribo D: are my RNA-seq data based on poly-A selection protocol or ribo-depletion ?
* Orientation: are my RNA-seq libraries stranded or not ?
* Y chromosome: what is/are the gender(s) corresponding to my samples ?
* Read position biases: is there a read coverage bias from 5' to 3' ends ?


** Contamination**

* HeLa: are my RNA-seq data contaminated by HeLa (presence of HeLa-derived human papillomavirus 18) ?
* Mycoplasma: are my RNA-seq data contaminated by mycoplasmas ?
* Virus: are my RNA-seq data contaminated by viruses such as hepatitis B virus ?
* Species: what is/are the species present into my samples ?

For each subsection, a graph shows the quantification of predictor genes (Y axis, mean k-mer counts normalized
 per billion of k-mers in the sample) in each RNA-seq sample of your dataset (X axis). More details on the
 predictor genes and their selection to answer a specific biological question are described into the corresponding
 subsections.

*Citation: [Kmerator Suite](https://pubmed.ncbi.nlm.nih.gov/34179780/){: target="_blank"}.*