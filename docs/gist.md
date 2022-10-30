# Gist

gists are small code snippets and other paste-style docs which are discovered during the development of YASMaPE.

<!--ts-->
   * [Download stock data](#download-stock-data)
   * [Run jupyter notebook from command line](#run-jupyter-notebook-from-command-line)
   * [Creating UML diagrams from docker-compose.yml](#creating-uml-diagrams-from-docker-composeyml)
   * [Creating svg images from snakemake rulegraphs](#creating-svg-images-from-snakemake-rulegraphs)
   * [Add a TOC to Markdown Files](#add-a-toc-to-markdown-files)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->
<!-- Added by: root, at: Sun Oct 30 10:00:28 UTC 2022 -->

<!--te-->

## Download stock data

We download stock data from yahoo finance.

**Example:** Download stock prices using [`curl`](https://curl.se/) for DBK.DE between Sept. 5, 2021 (given by param `period1`) and Sept. 5, 2022 (given by param `period2`):

```
curl -L "https://query1.finance.yahoo.com/v7/finance/download/DBK.DE?period1=1630865082&period2=1662401082&interval=1d&events=history&includeAdjustedClose=true"
```

## Run jupyter notebook from command line

The straight forward approach `jupyter --to notebook --execute </path/to/notebook>` does not work, because it uses `<path/to/...>` as working directory. This is fatal if relative file paths are used.

Using the following approach the notebook starts in the directory, where the command is issued. By trial and error, we found the following params in an example the fastest:

```
 cat /home/jovyan/work/create_feature.ipynb | jupyter nbconvert --to notebook -
-execute --stdin --clear-output
```

Other approaches:

1. Convert and run
```
cat /home/jovyan/work/create_feature.ipynb | jupyter nbconvert --to script --stdin --stdout | grep -v -e "^get_ipython" > ./notebook.py

python3 notebook.py
```

2. Run notebook from stdin
```
 cat /home/jovyan/work/create_feature.ipynb | jupyter nbconvert --to notebook -
-execute --stdin
```

Finally, add `--clear-output`

```
 cat /home/jovyan/work/create_feature.ipynb | jupyter nbconvert --to notebook -
-execute --stdin --clear-output
```

**Example Performance:**

1. Convert and run: 2min 6s (Script conversion: ca. 6s)
1. Run notebook from stdin: ca. 2min 37s
1. Like prev, but add `--clear-output`: ca. 1min 50s

## Creating UML diagrams from `docker-compose.yml`

Source: https://medium.com/@krishnakummar/creating-block-diagrams-from-your-docker-compose-yml-da9d5a2450b4

Replace `/home/user/blog` with directory containing `docker-compose.yml` file.

Container services and their dependencies

```
docker run --rm -it --name dcv -v /home/user/blog:/input pmsipilot/docker-compose-viz render -m image --force docker-compose.yml --output-file=topology.png --no-volumes --no-ports --no-networks
```

.. with port numbers

```
docker run --rm -it --name dcv -v /home/user/blog:/input pmsipilot/docker-compose-viz render -m image --force docker-compose.yml --output-file=topology-ports.png --no-volumes --no-networks
```

.. with volumes

```
docker run --rm -it --name dcv -v /home/user/blog:/input pmsipilot/docker-compose-viz render -m image --force docker-compose.yml --output-file=topology-volumes.png --no-ports --no-networks
```

## Creating svg images from snakemake rulegraphs

Using the command `snakemake --rulegraph` snakemake outputs a dot formatted graph of the DAG formed from the rules. We feed the online REST API from https://quickchart.io/documentation/graphviz-api/ with the dot formatted rulegraph. 

Have a look at [`../src/ludwig/generate_rulegraph.sh`](../src/ludwig/generate_rulegraph.sh).

## Add a TOC to Markdown Files

YASMaPE utilizes [gh-md-toc](https://github.com/ekalinin/github-markdown-toc) to generate and insert a TOC into markdown (`.md`) files.

In the `.md` file add the marker where you want to have the TOC appear.
```
<!--ts-->
<!--te-->
```

Afterwards run the `gh-md-toc` with the following options to include or update the TOC.
```
gh-md-toc --insert --skip-header README.md
```

The YASMaPE image comes with `gh-md-toc` installed.
