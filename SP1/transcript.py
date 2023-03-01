from pathlib import Path
import os

import rules

def read_input_file(filename: str):
    sentences_list = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.rstrip()
            sentences_list.append(sentence)
    file.close()

    return sentences_list

def save_output_file(sentences, filename: str):
    f = open(filename, 'w', encoding='utf-8')

    for sentence in sentences:
        sentence = sentence + '\n'
        f.write(sentence)

    f.close()

def create_start_end_pauses(sentences_list):
    pass

def apply_basic_rules(sentences_list: list, basic_rules: dict):
    res = []
    for sentence in sentences_list:
        sentence = sentence.lower()
        for char in basic_rules:
            char_transcript = basic_rules[char]
            sentence = sentence.replace(char, char_transcript)

        res.append('|$|' + sentence)

    return res

if __name__ == "__main__":
    #input_filename = "vety_HDS.ortho.txt"
    input_filename = "ukazka_HDS.ortho.txt"
    output_filename = "vety_HDS_transcript.txt"

    sentences_list_orig = read_input_file(input_filename)
    basic_rules = rules.BASIC_RULES
    res = apply_basic_rules(sentences_list_orig.copy(), basic_rules)

    save_output_file(res, output_filename)
    print()


