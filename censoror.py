import argparse
import re
import os
from glob import glob
import sys
import spacy
from google.cloud import language_v1 

# Set your Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "deassignment-416700-19803083548f.json"

# Load the spaCy language model
nlp = spacy.load("en_core_web_md")

# Compile a regex pattern for phone numbers with various formats
phone_pattern = re.compile(
    r'''
    (\+\d{1,3}[\s-]?)?                      # Optional international prefix
    (\(?\d{3}\)?[\s-]?)?                    # Optional area code
    (\d{3}[\s-]?\d{4}|\d{2,4}[\s-]?\d{2,4}[\s-]?\d{2,4}) # Main number
    ''', re.VERBOSE | re.IGNORECASE)

def censor_entity(text, start_char, end_char):
    """Replace a portion of the text with a censorship mask, avoiding new lines."""
    segment = text[start_char:end_char]
    newline_pos = segment.find('\n')
    
    # Adjust the end character if a newline is found within the segment
    if newline_pos != -1:
        end_char = start_char + newline_pos
    
    return text[:start_char] + "█" * (end_char - start_char) + text[end_char:]

def is_likely_phone_number(text):
    """Check if a piece of text likely represents a phone number."""
    return re.match(r'\+\d{1,4}\s\d+', text) or any(sep in text for sep in ['-', ' ']) and len(re.sub(r'\D', '', text)) >= 7

def censor_phone_numbers(text, stats):
    """Find and censor phone numbers in the text."""
    phone_matches = re.finditer(phone_pattern, text)
    for match in phone_matches:
        matched_text = match.group().strip()
        if is_likely_phone_number(matched_text):
            stats["phones"] += 1
            text = censor_entity(text, match.start(), match.end())
    return text, stats

def is_name_strict_google_nlp(name):
    """Check if a given name is strictly recognized as a PERSON using Google Cloud Natural Language API."""
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=name, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_entities(document=document)
    return any(entity.type == language_v1.Entity.Type.PERSON for entity in response.entities)

def clean_and_extract_names(doc):
    """Extract and clean names found by spaCy, optionally verifying with Google NLP."""
    cleaned_names = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" or is_name_strict_google_nlp(ent.text):
            name = clean_and_handle_comma_names(ent.text)
            if name:  # Ensure the cleaned name is not empty
                cleaned_names.append((name, ent.start_char, ent.end_char))
    return cleaned_names

def clean_and_handle_comma_names(name):
    """Clean names, especially handling comma-separated and email format names."""
    email_regex = re.compile(r'\"?(.+?)\"?\s*<(.+)>')
    match = email_regex.match(name)
    if match:
        name_part, email_part = match.groups()
        name_part = clean_name(name_part)  # Clean name to remove unwanted characters
        if ',' in name_part:
            parts = [part.strip() for part in name_part.split(',')]
            if len(parts) == 2:
                name_part = ' '.join(parts[::-1])  # Reverse for "Lastname, Firstname" format
        name = f"{name_part} <{email_part}>"
    else:
        name = clean_name(name)  # Directly clean names not in email format
        if ',' in name:
            parts = [part.strip() for part in name.split(',')]
            if len(parts) == 2:
                name = ' '.join(parts[::-1])
    return name

def analyze_entities(text_content):
    """Use Google Cloud Natural Language API to detect entities in text, focusing on addresses and locations."""
    client = language_v1.LanguageServiceClient()
    document = {"content": text_content, "type_": language_v1.Document.Type.PLAIN_TEXT}
    response = client.analyze_entities(document=document)
    addresses = [(entity.name, entity.salience) for entity in response.entities if entity.type_ in [language_v1.Entity.Type.ADDRESS, language_v1.Entity.Type.LOCATION]]
    return addresses

def censor_addresses_with_google_nlp(text, stats):
    """Find and censor addresses in the text using Google Cloud Natural Language API."""
    addresses = analyze_entities(text)
    for address, _ in addresses:
        address_pattern = re.escape(address)
        text = re.sub(address_pattern, "█" * len(address), text)
        stats["address"] += 1
    return text, stats

def preprocess_text_for_dates(text):
    """Preprocess the text to normalize date formats and fix common issues."""
    text = re.sub(r'\s+([:/])\s+', r'\1', text)  # Normalize spaces around date separators
    text = re.sub(r'\b(\d{1,2})[stndrh]{2}\b', r'\1', text, flags=re.IGNORECASE)  # Remove ordinal suffixes from dates
    # Normalize potential date formats by reducing unnecessary line breaks
    date_linebreak_pattern = re.compile(
        r'(\d{1,2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b)\s*\n\s*(\d{1,2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b|\d{4})',
        re.IGNORECASE)
    preprocessed_text = re.sub(date_linebreak_pattern, r'\1 \2', text)
    # Handle newline issues with timestamps
    timestamp_pattern = re.compile(r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s*\n', re.IGNORECASE)
    preprocessed_text = re.sub(timestamp_pattern, r'\1 ', preprocessed_text)
    return preprocessed_text

def analyze_entities_dates(text_content):
    """Detect date entities in the text using Google Cloud Natural Language API."""
    client = language_v1.LanguageServiceClient()
    document = {"content": text_content, "type_": language_v1.Document.Type.PLAIN_TEXT}
    response = client.analyze_entities(document=document)
    dates = [(entity.name, entity.salience) for entity in response.entities if entity.type_ == language_v1.Entity.Type.DATE]
    return dates

def censor_dates_with_google_nlp(text, stats):
    """Find and censor dates in the text using Google Cloud Natural Language API."""
    preprocessed_text = preprocess_text_for_dates(text)
    dates = analyze_entities_dates(preprocessed_text)
    for date_text, _ in dates:
        stats["dates"] += 1
        start_index = text.find(date_text)
        if start_index != -1:
            end_index = start_index + len(date_text)
            text = text[:start_index] + "█" * (end_index - start_index) + text[end_index:]
    return text, stats

def clean_name(name):
    """Clean the name by removing unwanted characters and normalizing whitespace."""
    name = re.sub(r'[<>"\']', '', name)  # Remove unwanted characters
    name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
    return name

def extract_and_censor_email_names(text, stats):
    """Extract email addresses from the text and censor the name part."""
    email_pattern = re.compile(r'<?(\b[A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})>?')
    matches = email_pattern.finditer(text)
    for match in matches:
        full_email = match.group(0)
        name_part, domain_part = match.groups()
        name_part_cleaned = clean_name(name_part.replace('.', ' ').replace('_', ' ').title())
        if ',' in name_part_cleaned:
            parts = name_part_cleaned.split(',')
            name_part_cleaned = ' '.join(parts[::-1]).strip()
        censored_name_part = "█" * len(name_part_cleaned)
        name_start, name_end = match.span(1)
        text = text[:name_start] + censored_name_part + text[name_end:]
        stats["names"] += 1
    return text, stats

def censor_document(text, censor_flags, stats):
    """Censor sensitive information from the document based on the specified flags."""
    if stats is None:
        stats = {"names": 0, "dates": 0, "phones": 0, "address": 0}
    
    if "--dates" in censor_flags:
        text, stats = censor_dates_with_google_nlp(text, stats)

    doc = nlp(text)

    if "--names" in censor_flags:
        text, stats = extract_and_censor_email_names(text, stats)
        cleaned_names = clean_and_extract_names(doc)
        for name, start_char, end_char in cleaned_names:
            stats["names"] += 1
            text = censor_entity(text, start_char, end_char)

    if "--phones" in censor_flags:
        text, stats = censor_phone_numbers(text, stats)

    if "--address" in censor_flags:
        text, stats = censor_addresses_with_google_nlp(text, stats)

    return text, stats

def output_stats(stats, stats_output):
    """Output the censorship statistics to the specified location."""
    stats_message = f"Censoring Statistics:\nNames: {stats['names']}\nDates: {stats['dates']}\nPhones: {stats['phones']}\nAddresses: {stats['address']}\n"
    if stats_output == "stderr":
        sys.stderr.write(stats_message)
    elif stats_output == "stdout":
        sys.stdout.write(stats_message)
    else:
        with open(stats_output, 'w') as f:
            f.write(stats_message)

def main(input_pattern, output_dir, censor_flags, stats_output):
    """Main function to censor documents based on input patterns and flags."""
    stats = {"names": 0, "dates": 0, "phones": 0, "address": 0}
    files_to_process = glob(input_pattern) if not os.path.isfile(input_pattern) else [input_pattern]

    os.makedirs(output_dir, exist_ok=True)

    for file_path in files_to_process:
        with open(file_path, 'r') as file:
            text = file.read()
            censored_text, stats = censor_document(text, censor_flags, stats)
            output_file_name = os.path.basename(file_path) + '.censored'
            with open(os.path.join(output_dir, output_file_name), 'w') as output_file:
                output_file.write(censored_text)

    output_stats(stats, stats_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Censor sensitive information from text documents.")
    parser.add_argument("--input", type=str, required=True, help="Glob pattern or file path for input text files.")
    parser.add_argument("--output", type=str, required=True, help="Directory to store censored files.")
    parser.add_argument("--names", action='store_true', help="Censor names in the document.")
    parser.add_argument("--dates", action='store_true', help="Censor dates in the document.")
    parser.add_argument("--phones", action='store_true', help="Censor phone numbers in the document.")
    parser.add_argument("--address", action='store_true', help="Censor addresses in the document.")
    parser.add_argument("--stats", type=str, required=True, help="Location to output the censoring statistics.")
    
    args = parser.parse_args()

    censor_flags = []
    for flag in ["--names", "--dates", "--phones", "--address"]:
        if getattr(args, flag.strip("--")):
            censor_flags.append(flag)

    main(args.input, args.output, censor_flags, args.stats)

