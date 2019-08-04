# The Wikidata Toolkit

## Table of Contents

1. [Introduction](#introduction)
1. [Why Television Series?](#why-television-series)
2. [Design](#design)
3. [Usage](#usage)
    1. [Pre-Requisites](#pre-requisites)
    1. [Sample Commands](#sample-commands)

## Introduction

This repo contains a few utility scripts that fix consistency issues and missing data on Wikidata, focusing on TV series.

It is used by my Wikidata bot a.k.a. [TheFireBenderBot](https://www.wikidata.org/wiki/User:TheFireBenderBot). Check out its [contributions](https://www.wikidata.org/wiki/Special:Contributions/TheFireBenderBot) to get an idea of what it specializes at. Here are some [stats](https://xtools.wmflabs.org/ec/www.wikidata.org/TheFireBenderBot).

## Why Television Series?

As part of working with the OMDB API, I discovered gaps in the results such as missing episodes. [Some replies](https://github.com/omdbapi/OMDb-API/issues/88#issuecomment-413684586) on the issues revealed that they use Wikidata as a backend, which led me to explore Wikidata itself.

In the future, this repo may evolve to encompass more cultural genres such as movies and books.

In general, Wikidata is an incredibly useful open-source data source, and any contribution to the service can have a large, positive impact on all downstream users, including academic projects and research.

## Design

[`constraint.py`](./constraints/constraint.py) contains the abstract definition and a few concrete implementations for the concept of a _Constraint_. This is similar to how Wikidata defines constraints, except that the implementation may contain a way to fix them.

The various scripts (currently at root level) use a SPARQL query to search for items, checking for consistencies, and fixing them.

[`bots`](./bots) contains various Bot implementations that can be used to iterate through Wikidata pages using a generator, and _treat_ them.

[`television.py`](./model/television.py) contains abstract models for the concepts of Episode, Season, Series and more. Each model has some semantic knowledge of the item it encapsulates, as well as the constraints it should be checked for.

[`wikidata_properties.py`](./properties/wikidata_properties.py) has a bunch of constants that encode property codes and a few common ID values. A list of all properties can be found [here](https://www.wikidata.org/wiki/Wikidata:List_of_properties/all_in_one_table)

## Usage

### Pre-Requisites

In order to run the scripts, you need to [create a Bot account](https://www.wikidata.org/wiki/Wikidata:Creating_a_bot) on Wikidata. Bot names usually end with the suffix "Bot". Once you have the appropriate credentials, create the following files:

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

1. Checking individual items for constraint failures:
```bash
# Q65604139 = Season 1 of "Dark"
# Q65640227 Q65640226 Q65640224 = Episodes of "Dark"
python3 check_constraints.py Q65640227 Q65640226 Q65640224 Q65604139
```
2. Checking the episodes of a series (Jessica Jones) for constraint failures:
```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 \
    --child_type=episode
```
3. Checking and fixing the seasons of a series for constraint failures
```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 \
    --child_type=season \
    --autofix
```
4. Checking and fixing the episodes of a series for constraint failures, but wait until all the failures have been reported before fixing all of them at the end.
```bash
# Q18605540 = Jessica Jones
python3 episode_consistency_checker.py Q18605540 \
    --child_type=episode \
    --autofix \
    --accumulate
```
