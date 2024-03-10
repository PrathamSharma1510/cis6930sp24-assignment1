# CIS6930 Assignment 1: The Censoror

## Name
Pratham Sharma

## UFID
99812068

## Assignment Description

In this assignment, we're tasked with developing a system capable of censoring sensitive information from text documents. The types of data we aim to obscure include names, dates, phone numbers, and addresses, which are replaced with the censorship character █. The process is simple: the system processes plain text documents and outputs censored versions to a designated directory. Additionally, it compiles statistics regarding the censored content.

## Installation Instructions

### Clone the Repository
To get started, clone the repository to your local machine. Remember to replace `[repository-url]` and `[repository-name]` with your repository details.

```bash
git clone [repository-url]
cd [repository-name]
```

### Install Dependencies with Pipenv
This project uses Pipenv for dependency management. Install Pipenv via pip if you haven't already:

```bash
pip install pipenv
```

Then, install the dependencies from the Pipfile in your project directory:

```bash
pipenv install
```

### Google Cloud Setup
Set up a Google Cloud Platform (GCP) account, create a new project, enable the Natural Language API, and create a service account. Download the service account's JSON key file and point the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to it:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-file.json"
```

### Install spaCy Model
Install the required spaCy model within your Pipenv environment:

```bash
pipenv run pip install spacy
pipenv run python -m spacy download en_core_web_md
```

### Running the Script
To run the script with the provided parameters, adjust the path to your input files as necessary:

```bash
pipenv run python censoror.py --input 'data/*.txt' --names --dates --phones --address --output 'files/' --stats stderr
```

## How to Run the Code

### For Multiple Files
Process all `.txt` files in a `data/` directory:

```bash
pipenv run python censoror.py --input 'data/*.txt' --names --dates --phones --address --output 'files/' --stats stderr
```

### For Individual Files
Specify an individual file in the `--input` argument:

```bash
pipenv run python censoror.py --input 'data/specific_file.txt' --names --dates --phones --address --output 'files/' --stats stderr
```

## Functions Overview

The script includes various functions for identifying and censoring sensitive information:

- `censor_entity()`: Censors specified text segments.
- `is_likely_phone_number()`: Identifies potential phone numbers.
- `censor_phone_numbers()`: Censors phone numbers and updates stats.
- `is_name_strict_google_nlp()`: Validates names using Google NLP.
- `clean_and_extract_names()`: Prepares names for censorship.
- `analyze_entities()`: Identifies addresses and locations.
- `censor_addresses_with_google_nlp()`: Censors addresses and locations.
- `preprocess_text_for_dates()`: Prepares text for date recognition.
- `analyze_entities_dates()`: Detects date entities.
- `censor_dates_with_google_nlp()`: Censors dates and updates stats.
- `clean_name()`: Standardizes name format for censorship.
- `extract_and_censor_email_names()`: Censors names within emails.
- `censor_document()`: Main censorship function applying all flags.
- `output_stats()`: Outputs statistics of censored information.
- `main()`: Entry point to set up and run the script.

## About the Model

The script utilizes spaCy's `en_core_web_md` model and the Google Cloud Natural Language API for entity detection and censorship. Regex patterns aid in identifying phone numbers and formatting text.

## Bugs and Assumptions

Challenges include name recognition limitations, adjacent text censorship, and addressing nuances with pincodes. The script assumes the accuracy of underlying technologies and may not cover all global naming conventions or formats.

## Statistics

The script tracks the count of censored instances for each category, offering insight into the extent of sensitive information handled.

## Running Tests

Run tests using Pytest within the virtual environment:

```bash
pipenv run python -m pytest
```

## Test Files Overview

Test files verify the script's censoring capabilities using Pytest and mock objects to simulate spaCy and Google NLP behavior, ensuring functionality and accuracy.
```

When you place this content into your README.md file on GitHub, it will display with proper formatting, such as headers, code blocks, and lists. Remember to substitute `[repository-url]` and `[repository-name]` with your actual repository information before publishing.