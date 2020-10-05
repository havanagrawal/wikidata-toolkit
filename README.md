# The Wikidata Toolkit

![Python version](https://img.shields.io/badge/python-3.7+-blue.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python project with WikiBot implementations to fix consistency issues on Wikidata.

## Table of Contents

1. [Introduction](#introduction)
1. [Design](#design)
1. [Usage](#usage)
    1. [Pre-Requisites](#pre-requisites)
    1. [Sample Commands](#sample-commands)
    1. [Canned Scripts](#canned-scripts)
1. [Contributing](#contributing)

## Introduction

This repo contains a few utility scripts that fix consistency issues and missing data on [Wikidata](https://www.wikidata.org), focusing on TV series.

It is used by my Wikidata bot a.k.a. [TheFireBenderBot](https://www.wikidata.org/wiki/User:TheFireBenderBot). Check out its [contributions](https://www.wikidata.org/wiki/Special:Contributions/TheFireBenderBot) to get an idea of what it specializes at. Here are some [stats](https://xtools.wmflabs.org/ec/www.wikidata.org/TheFireBenderBot).

## Design

![Architecture Diagram](./classes.png)

[`constraint.py`](./constraints/api.py) contains the abstract definition for the concept of a _Constraint_. This is similar to how Wikidata defines constraints, except that the implementation may contain a way to fix them.

[`general.py`](./constraints/general.py) and [`tv.py`](./constraints/tv.py) contain a few concrete implementations for constraints.

[`bots`](./bots) contains various Bot implementations that can be used to iterate through Wikidata pages using a generator, and _treat_ (process) them.

[`television.py`](./model/television.py) contains abstract models for the concepts of Episode, Season, Series and more. Each model has some semantic knowledge of the item it encapsulates, as well as the constraints it should be checked for.

[`wikidata_properties.py`](./properties/wikidata_properties.py) has a bunch of constants that encode property codes and a few common ID values. A list of all properties can be found [here](https://www.wikidata.org/wiki/Wikidata:List_of_properties/all_in_one_table)

## Usage

### Pre-Requisites

#### Account Setup

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

#### Requirements

Next, you need to install dependencies using the `requirements.txt` file. This is best done using a virtualenv and pip3:

```bash
virtualenv pywiki
source pywiki/bin/activate
pip3 install -r requirements.txt
```

### Sample Commands

#### Checking and Fixing Constraints

1. Checking individual items for constraint failures:
    ```bash
    # Q65604139 = Season 1 of "Dark"
    # Q65640227 Q65640226 Q65640224 = Episodes of "Dark"
    python3 check_constraints.py Q65640227 Q65640226 Q65640224 Q65604139
    ```
1. Checking the episodes of a series (Jessica Jones) for constraint failures:
    ```bash
    # Q18605540 = Jessica Jones
    python3 check_tv_show.py Q18605540 \
        --child_type=episode
    ```
1. Checking and fixing the seasons of a series for constraint failures
    ```bash
    # Q18605540 = Jessica Jones
    python3 check_tv_show.py Q18605540 \
        --child_type=season \
        --autofix
    ```
1. Checking and fixing the episodes of a series for constraint failures, but wait until all the failures have been reported before fixing all of them at the end.
    ```bash
    # Q18605540 = Jessica Jones
    python3 check_tv_show.py Q18605540 \
        --child_type=episode \
        --autofix \
        --accumulate
    ```
1. Fixing only the titles of episodes of a series
    ```bash
    # Q18605540 = Jessica Jones
    python3 check_tv_show.py Q18605540 \
        --child_type=episode \
        --autofix \
        --accumulate \
        --filter title
    ```
    An equivalent command is
    ```bash
    # Q18605540 = Jessica Jones
    python3 check_tv_show.py Q18605540 \
        --child_type=episode \
        --autofix \
        --accumulate \
        --filter P1476
    ```


#### Fetching/Updating Data from Wikipedia

1. Get the list of episodes for The Neighborhood:
    ```bash
    # This will write out two files
    # the-neighborhood-tv-series_S01.csv and
    # the-neighborhood-tv-series_S02.csv
    python3 list_episodes.py "https://en.wikipedia.org/wiki/The_Neighborhood_(TV_series)" --episode-counts=21,22
    ```

1. Create the episodes in Wikidata:
    ```bash
    python3 create_episodes.py Q7753382 Q99419240 the-neighborhood-tv-series_S01.csv --quickstatements
    ```

### Canned Scripts

A few fixes are fairly straightforward, and should not require supervision. The [`canned`](./canned) folder exposes these fixes in the form of scripts that can be run directly without any arguments. If you want to see what changes will be made, run the script with the `--dry` flag.

Example:
```bash
# Dry run mode, won't update labels
python3 -m canned.fix_missing_labels --dry

# Run after confirming that the changes look correct
python3 -m canned.fix_missing_labels

### Contributing

#### Hacktoberfest

Hello there! If you are a Hacktoberfest 🎃 participant and wish to contribute to this repository, you can
1. Pick [an issue with the `hacktoberfest` label](https://github.com/havanagrawal/wikidata-toolkit/issues?q=is%3Aissue+is%3Aopen+label%3Ahacktoberfest)
2. Fork this repository
3. Clone this repository to your local machine
4. **Create a new branch**
5. Work on the issue on this new branch
6. Push your branch to your fork
7. Send a PR!