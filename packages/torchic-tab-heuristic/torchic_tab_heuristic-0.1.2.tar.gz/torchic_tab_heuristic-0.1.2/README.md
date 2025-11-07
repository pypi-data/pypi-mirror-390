# TorchicTab Heuristic

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
[![Python Versions](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-blue.svg)](https://www.python.org/)

**TorchicTab** is a semantic table annotation system that automatically understands the content of a table and assigns semantic tags to its elements with high accuracy. It was originally developed for the [SemTab](https://www.cs.ox.ac.uk/isg/challenges/sem-tab/) challenge. You can find more about the full system in our dedicated [article](https://dtai.cs.kuleuven.be/stories/post/anastasia-dimou/torchictab/) and [paper](https://ceur-ws.org/Vol-3557/paper2.pdf).

This repository contains TorchicTab-Heuristic, the TorchicTab subsystem that annotates tables, using the Wikidata knowledge graph as a reference knowledge base. TorchicTab-Heuristic produces annotations for the following semantic annotation tasks:
- The Cell Entity Annotation (CEA) task associates a table cell with an entity.
- The Column Type Annotation (CTA) task assigns a semantic type to a column.
- The Column Property Annotation (CPA) task discovers a semantic relation contained in the RDF graph that best represents the relation between two columns.
- The Topic Detection (TD) task identifies the topic of a table that lacks a subject column and assigns a class.

![TorchicTab-Heuristic Overview](resources/system.png)


## Installation 

TorchicTab-Heuristic requires a Python 3.9, 3.10 or 3.11 version. In case of conflicts, create a new virtual environment. For example, if you use conda, run:

```bash
conda create -n torchictab_env python=3.11
```
```bash
conda activate torchictab_env
```

Simple installation:

```bash
pip install torchic_tab_heuristic
```

Optional: 

TorchicTab also allows the creation of an Elasticsearch index which contains all Wikidata entity-labels pairs. This allows for enhanced lookup tecnhiques leveraging powerful Elasticsearch functionalities, such as fuzzy querying. To use TorchicTab-Heuristic with Elasticsearch:

- Download a Wikidata RDF dump from [Zenodo](https://doi.org/10.5281/zenodo.4282940)
- Install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch). Recommended version: Elasticsearch 8
- Process `config.py` file to configure index name and RDF dump adress. 
- Run elasticsearch server:

    ```bash
    cd elasticsearch-X.X.X
    ./bin/elasticsearch
    ```

- Create the elasticsearch index: 

    ```bash
    python elasticsearch/create_index.py
    ```

## Usage

Example usage of TorchicTab-Heuristic with Wikidata:

Without Elasticsearch

```bash
python examples/sta_demo.py -i "examples/tables/cities.csv"
```

With Elasticsearch

```bash
python examples/sta_demo.py -i "examples/tables/cities.csv" -e
```

## Cite

Thank you for reading! To cite our resource:

    @InProceedings{dasoulas2023torchictab,
        author    = {Dasoulas, Ioannis and Yang, Duo and Duan, Xuemin and Dimou, Anastasia},
        journal = {CEUR Workshop Proceedings},
        publisher = {CEUR Workshop Proceedings},
        title = {TorchicTab: Semantic Table Annotation with Wikidata and Language Models},
        year = {2023-11-02},
        }