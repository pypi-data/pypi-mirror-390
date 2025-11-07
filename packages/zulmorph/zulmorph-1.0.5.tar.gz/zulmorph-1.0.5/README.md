# ZulMorph Morphological Analyser
_A morphological analyser for Zulu_

## Overview

ZulMorph is a finite state morphological analyser for Zulu, originally developed using the Xerox finite state tools lexc and xfst and compiled here with Foma. This Python package is aimed at facilitating inclusion of ZulMorph in larger NLP pipelines.

Zulu words in their surface form are analysed to their base form. Any meaningful word can be input, and the output will be one or more complete morphological analyses of that word.

## Authors and attribution
- Laurette Pretorius <laurette@acm.org>
- Sonja Bosch <seb@hbosch.com>

Please cite the output of ZulMorph as follows:

> Pretorius, L. and Bosch, S. (2018). ZulMorph: Finite state morphological analyser for Zulu [Software]. Web demo at https://portal.sadilar.org/FiniteState/demo/zulmorph/

## Documentation

The tagset and additional documentation can be viewed [here](https://portal.sadilar.org/FiniteState/demo/zulmorph/doc.html#tagset).

## Installation

ZulMorph requires that FOMA be installed. See instructions [here](https://blogs.cornell.edu/finitestatecompling/2016/08/24/installing-foma/).

```bash
pip install zulmorph
```

## Usage

### Command line

As a command line tool, ZulMorph can be used as follows.

```bash
usage: zulmorph [-h] [-f FST] {t,f} input [input ...]

Uses ZulMorph to morphologically analyse isiZulu tokens.

positional arguments:
  {t,f}       indicate if input is [t]oken(s) or [f]ilename(s) (token per
              line)
  input

options:
  -h, --help  show this help message and exit
  -f FST      path to FST (.fom) (default: zul.fom)
```

Example with tokens:

```bash
zulmorph t indoda iyahamba > output.json
```

This will produce a file containing the following.

```json
{
  "indoda": [
    "i[NPrePre][9]n[BPre][9]doda.9-6[NStem]"
  ],
  "iyahamba": [
    "i[SC][9]ya[LongPres]hamb[VRoot]a[VT]",
    "i[SC][4]ya[LongPres]hamb[VRoot]a[VT]"
  ]
}
```

Example with filenames:

```bash
zulmorph f tokens.1.txt tokens.2.txt > output.json
```

### Python library

Usage as part of a Python program is as follows.

```python
from zulmorph import zulmorph as zm

zm.analyse_token("iyahamba")
```
This produces a list of strings representing the analyses.

```python
['i[SC][9]ya[LongPres]hamb[VRoot]a[VT]',
 'i[SC][4]ya[LongPres]hamb[VRoot]a[VT]']
```

Multiple tokens can be provided. This produces a dictionary where the keys are tokens and their values are lists of analyses. The order of the keys follow the order of the tokens in the list, ignoring any duplications that may occur.

```python
from zulmorph import zulmorph as zm

zm.analyse_tokens(["indoda","iyahamba"])
```

Output:
```python
{
  "indoda": [
    "i[NPrePre][9]n[BPre][9]doda.9-6[NStem]"
  ],
  "iyahamba": [
    "i[SC][9]ya[LongPres]hamb[VRoot]a[VT]",
    "i[SC][4]ya[LongPres]hamb[VRoot]a[VT]"
  ]
}
```

## License

See LICENSE distributed with this package.