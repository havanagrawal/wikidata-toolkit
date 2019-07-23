# Wikidata Toolkit

## Introduction

This repo contains a few utility scripts that fix consistency issues and missing data on Wikidata, focusing on TV series.

## Organization

```
.
├── __init__.py
├── check_constraints.py
├── clone.py
├── constraints
│   ├── __init__.py
│   └── constraint.py
├── episode_consistency_checker.py
├── model
│   ├── __init__.py
│   ├── factory.py
│   └── television.py
├── properties
│   ├── __init__.py
│   └── wikidata_properties.py
├── sparql
│   ├── __init__.py
│   └── query_builder.py
├── user-config.py
├── user-password.py
└── utils.py
```

## Design

[`constraint.py`](./constraints/constraint.py) contains the abstract definition and a few concrete implementations for the concept of a _Constraint_. This is similar to how Wikidata defines constraints, except that the implementation may contain a way to fix them.

The various scripts (currently at root level) use a SPARQL query to find an item to start from, and then iterate its children, checking for consistencies, and fixing them if the appropriate flag is provided.

[`television.py`](./model/television.py) contains abstract models for the concepts of Episode, Season, Series and more. Each model has some semantic knowledge of the item it encapsulates, as well as the constraints it should be checked for.

## Usage

Checking individual items for constraint failures:

```bash
# Q65604139 = Season 1 of "Dark"
# Q65640227 Q65640226 Q65640224 = Episodes of "Dark"
python3 check_constraints.py Q65640227 Q65640226 Q65640224 Q65604139
```

Checking a series (Jessica Jones) for constraint failures:

```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 --child_type=episode
```

Checking and fixing the seasons of a series for constraint failures

```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 --child_type=season
```
