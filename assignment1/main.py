# import argparse
# import spacy
# import re
# from glob import glob
# import os
# import sys
# from spacy.matcher import Matcher

# # Load spaCy model for names, dates, and other entity recognition
# nlp = spacy.load("en_core_web_sm")

# # Regular expression patterns for phone numbers and addresses
# phone_pattern = re.compile(r'\(?\b\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b')
# address_pattern = re.compile(r'\b\d{1,6}\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b', re.IGNORECASE)

# def initialize_matcher(nlp):
#     matcher = Matcher(nlp.vocab)
#     date_patterns = [
#         [{"SHAPE": "dd"}, {"TEXT": "/"}, {"SHAPE": "dd"}, {"TEXT": "/"}, {"SHAPE": "dddd"}],  # Matches "dd/dd/dddd"
#         [{"TEXT": {"REGEX": "^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"}}, {"SHAPE": "dd"}, {"TEXT": ","}, {"SHAPE": "dddd"}],  # Matches "Month dd, yyyy"
#     ]
#     for pattern in date_patterns:
#         matcher.add("CUSTOM_DATE", [pattern])
#     return matcher

# def censor_phone_numbers(text, stats):
#     matches = re.findall(phone_pattern, text)
#     stats["phones"] += len(matches)
#     return re.sub(phone_pattern, "█" * 12, text), stats

# def censor_addresses(text, stats):
#     matches = re.findall(address_pattern, text)
#     stats["address"] += len(matches)
#     return re.sub(address_pattern, "█" * 10, text), stats

# def censor_entity(text, start_char, end_char):
#     """Helper function to censor a portion of the text based on start and end character indices."""
#     return text[:start_char] + "█" * (end_char - start_char) + text[end_char:]

# def is_valid_date(entity_text):
#     """
#     Check if the entity text represents a valid date and not a postal code or other numeric string.
#     """
#     # Example check: exclude purely numeric strings of 5 characters (common US postal code format)
#     if re.fullmatch(r'\d{5}', entity_text):
#         return False
#     # Add more rules as needed based on observed misclassifications
#     return True

# def censor_document(text, censor_flags, stats, matcher):
#     doc = nlp(text)
    
#     for ent in doc.ents:
#         if ent.label_ == "PERSON" and "--names" in censor_flags:
#             stats["names"] += 1
#             text = censor_entity(text, ent.start_char, ent.end_char)
#         elif ent.label_ == "DATE" and "--dates" in censor_flags and is_valid_date(ent.text):
#             print(f"Validated Date (spaCy NER): '{ent.text}'")
#             stats["dates"] += 1
#             text = censor_entity(text, ent.start_char, ent.end_char)
#         # For entities identified by Matcher, apply similar validation if needed

#     # Handle phone numbers and addresses as before
#     if "--phones" in censor_flags:
#         text, stats = censor_phone_numbers(text, stats)
#     if "--address" in censor_flags:
#         text, stats = censor_addresses(text, stats)

#     return text, stats

# def output_stats(stats, stats_output):
#     stats_message = f"Censoring Statistics:\nNames: {stats['names']}\nDates: {stats['dates']}\nPhones: {stats['phones']}\nAddresses: {stats['address']}\n"
#     if stats_output == "stderr":
#         sys.stderr.write(stats_message)
#     elif stats_output == "stdout":
#         sys.stdout.write(stats_message)
#     else:
#         with open(stats_output, 'w') as f:
#             f.write(stats_message)

# def main(input_pattern, output_dir, censor_flags, stats_output):
#     stats = {"names": 0, "dates": 0, "phones": 0, "address": 0}
#     matcher = initialize_matcher(nlp)

#     files_to_process = []
#     if os.path.isfile(input_pattern):
#         files_to_process.append(input_pattern)
#     else:
#         files_to_process.extend(glob(input_pattern))
    
#     os.makedirs(output_dir, exist_ok=True)
    
#     for file_path in files_to_process:
#         with open(file_path, 'r') as file:
#             text = file.read()
#             censored_text, stats = censor_document(text, censor_flags, stats, matcher)
#             output_file_name = os.path.basename(file_path) + '.censored'
#             output_path = os.path.join(output_dir, output_file_name)
#             with open(output_path, 'w') as output_file:
#                 output_file.write(censored_text)

#     output_stats(stats, stats_output)
#     print(f"Censoring complete. Censored files are saved to {output_dir}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Censor sensitive information from text documents.")
#     parser.add_argument("--input", type=str, required=True, help="File path or glob pattern for input text files.")
#     parser.add_argument("--output", type=str, required=True, help="Directory to store censored files.")
#     parser.add_argument("--names", action='store_true', help="Censor names.")
#     parser.add_argument("--dates", action='store_true', help="Censor dates.")
#     parser.add_argument("--phones", action='store_true', help="Censor phone numbers.")
#     parser.add_argument("--address", action='store_true', help="Censor addresses.")
#     parser.add_argument("--stats", type=str, required=True, help="File or location to write the statistics of the censoring process.")
    
#     args = parser.parse_args()

#     censor_flags = []
#     if args.names:
#         censor_flags.append("--names")
#     if args.dates:
#         censor_flags.append("--dates")
#     if args.phones:
#         censor_flags.append("--phones")
#     if args.address:
#         censor_flags.append("--address")

#     main(args.input, args.output, censor_flags, args.stats)
