# GOAuTomation (GOAT)

## Overview

GOAT is an Automatic information extraction tool which
downloads PDF appeal documents from the GO database
using GO API and parse specific information from
those documents using NLP and LLM.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [License](#license)
- [Contact](#contact)
- [TODO](#todo)

---

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:TKartist/GOAuTomation.git
   ```

## Usage
- the `quantitative_context_extraction()` of the string_manipulation file is focused specifically on numerical data extraction
- Extracting all texts while maintaining their positional value
- Divides textified PDF as pages
- Token calculator (Token is a unit used in LLMs which are equivalent to one variable; it is different from letter, word, or phrase)
  Hence, to avoid issues, token count may play an important role in debugging and understanding the datastream
- Sending asynchronous call to OpenAI API with designated system message and multiple chunks of user message

## Features



## TODO
- Pull final reports from GO database
- Establish Asynchronous OpenAI api calls with specific system messages
- build a function which can breakdown large (12 pages in average) reports into chunks which the OpenAI API can ingest without hitting the token limitations
- These tasks can be referred to previous tools written in `reimagined-funicular` repository