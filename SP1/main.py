import argparse
from pathlib import Path
import os

# Modules import
import rules
import phonetic_transcription

if __name__ == "__main__":
    # CMD
    # parser = argparse.ArgumentParser(
    #     prog='Phonetic transcription',
    #     description='Creates phonetic transcription from the input text.',
    # )
    #
    # parser.add_argument('-p', '--path_input_text', metavar='path_input', type=str,
    #                     help='a path to the input file')
    #
    # parser.add_argument('-s', '--path_phntrn', metavar='path_phntrn', type=str,
    #                     help='a path to the output file')
    #
    # args = parser.parse_args()
    #
    # # From CMD
    # input_path = Path(args.path_input_text)
    # output_path = args.path_phntrn
    #
    # if output_path is None:
    #     output_filename = input_path.name.replace("ortho", "phntrn")
    #     output_path = os.path.join(input_path.parent, output_filename)

    # Debugging
    # input_path = "vety_HDS.ortho.txt"
    # input_path = "ukazka_HDS.ortho.txt"
    # input_path = "test.txt"
    input_path = "spodoba_znelosti.txt"
    output_path = "vety_HDS_transcript.txt"

    # Reading sentences
    sentences_list_orig = phonetic_transcription.read_input_file(input_path)

    # Importing basic rules
    basic_rules = rules.BASIC_RULES

    # Processing
    res = phonetic_transcription.apply_basic_rules(sentences_list_orig.copy(), basic_rules)
    res = phonetic_transcription.apply_alophones(res)
    res = phonetic_transcription.apply_assimilation(res)
    res = phonetic_transcription.check_prepositions(res)

    # Saving output
    phonetic_transcription.save_output_file(res, output_path)
