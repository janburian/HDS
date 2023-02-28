from pathlib import Path
import os

def read_input_file(filename: str):
    sentences_list = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.rstrip()
            sentences_list.append(sentence)
    file.close()

    return sentences_list

def save_output_file(filename: str):
    pass

if __name__ == "__main__":
    filename = "vety_HDS.ortho.txt"
    sentences_list = read_input_file(filename)
    print()


