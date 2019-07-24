# The Wikidata Toolkit

## Table of Contents

1. [Introduction](#introduction)
2. [Design](#design)
3. [Usage](#usage)
    1. [Pre-Requisites](#pre-requisites)
    1. [Sample Commands](#sample-commands)

## Introduction

This repo contains a few utility scripts that fix consistency issues and missing data on Wikidata, focusing on TV series.

It is used by my Wikidata bot a.k.a. [TheFireBenderBot](https://www.wikidata.org/wiki/User:TheFireBenderBot).

## Design

[`constraint.py`](./constraints/constraint.py) contains the abstract definition and a few concrete implementations for the concept of a _Constraint_. This is similar to how Wikidata defines constraints, except that the implementation may contain a way to fix them.

The various scripts (currently at root level) use a SPARQL query to find an item to start from, and then iterate its children, checking for consistencies, and fixing them if the appropriate flag is provided.

[`television.py`](./model/television.py) contains abstract models for the concepts of Episode, Season, Series and more. Each model has some semantic knowledge of the item it encapsulates, as well as the constraints it should be checked for.

[`wikidata_properties.py`](./properties/wikidata_properties.py) has a bunch of constants that encode property codes and a few common ID values. A list of all properties can be found [here](https://www.wikidata.org/wiki/Wikidata:List_of_properties/all_in_one_table)

## Usage

### Pre-Requisites

In order to run the scripts, you need to [create a Bot account]() on Wikidata. Bot names usually end with the suffix "Bot". Once you have the appropriate credentials, create the following files:

[`user-config.py`](https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py)

```python
family = 'wikidata'
mylang = 'wikidata'

usernames['wikidata']['wikidata'] = u'YourBotName'
password_file = "user-password.py"
```

[`user-password.py`](https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords)

```python
(u'YourBotName', BotPassword(u'YourBotName', u'YourBotPassword'))
```

OR

```python
(u'YourUserName@YourBotName', u'YourBotPassword')
```

Also see the [Wikidata page on Bots](https://www.wikidata.org/wiki/Wikidata:Bots)

### Sample Commands

Checking individual items for constraint failures:

```bash
# Q65604139 = Season 1 of "Dark"
# Q65640227 Q65640226 Q65640224 = Episodes of "Dark"
python3 check_constraints.py Q65640227 Q65640226 Q65640224 Q65604139
```

Checking the episodes of a series (Jessica Jones) for constraint failures:

```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 \
    --child_type=episode
```

Checking and fixing the seasons of a series for constraint failures

```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 \
    --child_type=season \
    --autofix
```
