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
- Feed the answer OpenAI API gave as a part of the systems message and encourage it to fix its' own inconsistencies and mistakes while repassing the pages
  for it to refer to it as a context.