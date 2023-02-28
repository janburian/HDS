from pathlib import Path
import os

def load_input_txt_file(filename: str):
    sentences_list = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            sentence = line.rstrip()
            sentences_list.append(sentence)
    file.close()

    return sentences_list


if __name__ == "__main__":
    filename = "vety_HDS.ortho.txt"
    sentences_list = load_input_txt_file(filename)
    print()


