# 2021-benchmarking-dev

To run:

download the code:
```
git clone https://github.com/bluegenes/2021-benchmarking-dev.git
cd 2021-benchmarking-dev
```

Creat the conda/mamba env
```
mamba env create -f environment.yml
conda activate benchsets
```

Then open jupyter lab:
```
jupyter-lab
```

The `notebooks/evolpaths-taxonomic-distribution.ipynb` notebook makes interactive sankey plots.
The `notebooks/notebooks/sunburst-and-lineages-of-interest.ipynb` makes interactive sunburst plots.

Run the cells in each notebook to produce the plots.
