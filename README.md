# README for CIS6930 Assignment 1: The Censoror

**Name:** Pratham Sharma
**UFID:** 99812068

## Assignment Description

This assignment is about creating a system that's going to censor out sensitive info from text documents. What we're targeting are names, dates, phone numbers, and addresses, and we're replacing them with a censorship character, which is. The way it works is pretty straightforward: it processes plain text documents and spits out the censored versions into a directory you specify. It'll also give you some stats about what got censored.

#### Installation Instructions

1. **Clone the Repository:**
   First off, you gotta clone the code repository onto your local machine. Use the commands below, and don't forget to replace `[repository-url]` and `[repository-name]` with the actual URL and name of your repository.

   ```
   git clone [repository-url]
   cd [repository-name]
   ```

2. **Install Dependencies with Pipenv:**
   We're using Pipenv to manage the project's dependencies. If you haven't got Pipenv installed yet, you can install it using pip:

   ```
   pip install pipenv
   ```

   Once you've got that sorted, go ahead and install the project dependencies from the Pipfile in the project directory:

   ```
   pipenv install
   ```

3. **Google Cloud Setup:**
   You need a Google Cloud Platform (GCP) account for this. Create a new project, enable the Natural Language API for it, and then create a service account. Download the JSON key file for your service account and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to this file:

   ```
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
   ```

4. **Install spaCy Model:**
   Next up, you need to install the spaCy model we're using. Run these commands within your Pipenv environment:

   ```
   pipenv run pip install spacy
   pipenv run python -m spacy download en_core_web_md
   ```

5. **Running the Script:**
   To run the script, execute it within the Pipenv environment with the parameters provided. You'll need to adjust the path to your input files as necessary:

   ```
   pipenv run python censoror.py --input 'data/*.txt' --names --dates --phones --address --output 'files/' --stats stderr
   ```

#### How to Run the Code

- **For Multiple Files:**
  If you've got a bunch of `.txt` files in a directory named `data/`, the script can handle all of them in one go.

  ```
  pipenv run python censoror.py --input 'data/*.txt' --names --dates --phones --address --output 'files/' --stats stderr
  ```

- **For Individual Files:**
  You can also run it for a single file by specifying that file in the `--input` argument.

  ```
  pipenv run python censoror.py --input 'data/specific_file.txt' --names --dates --phones --address --output 'files/' --stats stderr
  ```

This setup means all dependencies are neatly wrapped up in Pipenv, making it easier to manage and ensuring that running the script is a breeze across different setups without any dependency conflicts.

### Functions Overview

We've got a bunch of functions in this script. Here's a quick rundown:

- **`censor_entity(text, start_char, end_char)`**: This one's for replacing parts of the text with █, making sure we don't mess up any newline characters in there. It's what we use to actually censor the sensitive bits.

- **`is_likely_phone_number(text)`**: Checks if a string looks like a phone number, considering different formats and separators like spaces and hyphens. It's quite handy for figuring out what needs to be censored as a phone number.

phone number, considering different formats and separators like spaces and hyphens. It's quite handy for figuring out what needs to be censored as a phone number.

- **`censor_phone_numbers(text, stats)`**: This function goes through the text, looking for patterns that match phone numbers. It uses `is_likely_phone_number` to make sure it's not censoring random numbers. Every phone number it censors gets counted and added to the stats.

- **`is_name_strict_google_nlp(name)`**: Uses Google Cloud's Natural Language API to check if a piece of text is definitely a person's name. It's a bit of a double-check to ensure we're not censoring names that aren't actually names.

- **`clean_and_extract_names(doc)`**: After spaCy pulls out what it thinks are names, this function cleans them up and gets them ready for censoring. It's all about making sure we're only censoring actual names.

- **`analyze_entities(text_content)`**: This one's for figuring out if there are addresses or locations in the text by using the Google Cloud Natural Language API. It's key for making sure we censor where people are talking about.

- **`censor_addresses_with_google_nlp(text, stats)`**: Directly censors addresses and locations found by `analyze_entities`. It updates our stats too, so we know how much we're censoring.

- **`preprocess_text_for_dates(text)`**: Gets the text ready so we can better spot and censor dates. Dates can be tricky because of all the different ways people write them.

- **`analyze_entities_dates(text_content)`**: This targets dates using the Google Cloud Natural Language API. Dates are important to censor because they can be pretty sensitive info.

- **`censor_dates_with_google_nlp(text, stats)`**: Censors the dates that `analyze_entities_dates` finds. Like with the other types of sensitive info, it keeps track of how much we're censoring in the stats.

- **`clean_name(name)`**: Cleans up names so they're uniform before we censor them. It's about making sure we don't miss censoring a name just because it's written in a slightly different way.

- **`extract_and_censor_email_names(text, stats)`**: Pulls names out of email addresses in the text and censors them. It's a neat trick to make sure we're not leaving any personal info uncensored.

- **`censor_document(text, censor_flags, stats)`**: The big one. This function takes the whole text and goes through it, censoring all the bits we've told it to based on the flags we set. It's the heart of the script.

- **`output_stats(stats, stats_output)`**: After all that censoring, this function tells you what it did. It can output the stats to stderr, stdout, or a file, depending on what you want.

- **`main(input_pattern, output_dir, censor_flags, stats_output)`**: This is where everything kicks off. It sets up the script, processes the files, and gets everything moving based on the command line arguments you give it.

### About the Model

#### How We Use spaCy

So, in this script, we're leaning pretty heavily on spaCy for the heavy lifting in figuring out where names are in the text documents. It's all thanks to this nifty function called `clean_and_extract_names`, which basically tells spaCy to find all the bits tagged as "PERSON" and then scrubs them up nice and clean for censorship. We're using spaCy's `en_core_web_md` model for this, which is kind of the Goldilocks of their models—not too big, not too small, just right for picking out the stuff we need without hogging all your computer's memory.

#### Google Cloud Natural Language API's Role

Then there's the Google Cloud Natural Language API, which we've got all hooked up and ready to roll with the authentication credentials from a JSON file. You've gotta set up an environment variable (`GOOGLE_APPLICATION_CREDENTIALS`) to point to it, and then you're good to go. This API is super useful for a couple of things in the script:

- **`is_name_strict_google_nlp`**: It double-checks names to make sure they're really, really names before we go blacking them out.
- **`analyze_entities`**: This is for spotting addresses and places in the text, which is pretty handy for making sure we're not leaving any breadcrumbs that could lead back to someone.
- **`analyze_entities_dates`**: It does a similar thing but for dates, so we can keep those under wraps too.

It's like the one-two punch of spaCy and Google Cloud makes this script kinda like a detective and a ninja rolled into one when it comes to finding and hiding sensitive info.

#### Regex

Oh, and we can't forget about regex—regular expressions. These are like the Swiss Army knife in our toolkit, especially for spotting phone numbers and tweaking text. We've got:

- **`censor_phone_numbers`**: This one's all about catching those phone numbers, no matter how they're written, and giving them the ol' censorship treatment.
- **`preprocess_text_for_dates`** and **`clean_and_handle_comma_names`**: They clean up dates and names, making sure everything's nice and tidy for processing. It's like making sure we don't miss anything because it was hidden in a mess.

- **`extract_and_censor_email_names`**: Plus, we're pulling names out of email addresses and making sure they're not giving anything away either.

Between spaCy, Google Cloud, and our regex tricks, we're pretty much covered for making sure we catch all that sensitive info that needs to stay private.

### Bugs and Assumptions

#### Name

- **Recognizing Names**: Sometimes, the script gets a bit tripped up on names that don't fit the usual patterns. It's kinda like when you hear a name for the first time and you're not sure if you heard it right. That's the struggle here, but with text.
- **When Text Gets Too Clingy**: And then there's when the script gets a bit overzealous and starts censoring bits of text hanging out too close to the names. It's like accidentally covering up a bit of the next puzzle piece because you thought it was part of the one you were working on.

#### Addressing Addresses

- **The Case of the Missing Pincodes**: For whatever reason, sometimes the script skips over pincodes or numbers that are chilling with an address. It's like the Google Cloud API didn't get the memo that those numbers are part of the party too.

#### Dates

- **Dates on the Move**: Dates can be sneaky, especially when they try to hide by hopping onto the next line. The script sometimes loses track of them when they pull this stunt, so some dates might dodge the censorship net.

#### What We Might Do About It

- **Smartening Up Our Models**: We could give spaCy a bit of a brain boost with more data or tweak how it picks out names with something called an entity ruler. It's all about making the script smarter at knowing what to hide.

### About Stats

Keeping track of what we censor is pretty key, so we've got this system for counting names, phone numbers, dates, and addresses. It's a bit like keeping score, but for privacy. we are using and show caseing the stats of multiple files which is beiing passed in the command when run.
Comulative in format :-
Censoring Statistics:
Names: some_number
Dates: some_number
Phones: some_number
Addresses: some_number

#### Counting What Counts

- **Names**: Every name spaCy or Google thinks is a name gets a tick on the scoreboard. Whether it's just a first name or a full-on name, it counts as one.
- **Phone Numbers and Dates**: Each one we find and censor gets its own point too. It's straightforward—find, censor, count.
- **Addresses**: Here's where it gets funky. We count every piece of an address separately. So, like, "400 SW Blvd" racks up three points because it's got three bits to it.

### Test Time

When you wanna make sure everything's running like it should, just pop into your virtual environment and hit this up:

```bash
pipenv run python -m pytest
```

It'll run through all the checks to make sure the script's censoring game is still strong.

## Test Suite for Censorship Module

This document outlines the test suite implemented in `test_file.py` for evaluating the functionality of our `censoror` module. The suite focuses on the module's capability to effectively identify and censor sensitive information such as phone numbers, addresses, and names within email addresses.

### Overview of Tests

Our tests leverage `pytest` for execution, employing mock objects from `unittest.mock` to emulate interactions with external services like the Google Cloud Natural Language API. The suite is structured to ensure the `censoror` module's operations conform to expected behaviors across various scenarios.

#### Phone Number Censorship

The `test_censor_phone_numbers` method conducts multiple tests to validate the censoring mechanism for phone numbers. It examines different phone number formats to ensure they're accurately identified and replaced with a corresponding number of censorship marks.

#### Address Censorship Using Mocks

In `test_censor_addresses_with_mock`, we simulate responses from the Google Cloud Natural Language API to test our address censorship feature without actual API requests. This method allows us to assess the functionality's accuracy in detecting and censoring addresses within texts.

#### Email Name Extraction and Censorship

The `test_extract_and_censor_email_names` evaluates the extraction of names from within email addresses and their subsequent censorship. It confirms that the process not only censors names correctly but also updates censorship statistics as expected.
