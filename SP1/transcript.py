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
        sentence.append('\n')
        sentence_str = ''.join(sentence)
        f.write(sentence_str)

    f.close()

def create_start_end_pauses(sentences_list):
    pass

def create_transcript(sentences_list, EPA_alphabet):
    res = []
    for sentence in sentences_list:
        sentence_transcript = ['|$|']
        words_list = sentence.split(" ")
        for word in words_list:
            word = word.lower()
            word_list = list(word)
            for i in range(len(word_list)):
                char = word[i]
                char_EPA = EPA_alphabet[char]
                word_list[i] = char_EPA

            word_str = ''.join(word_list)
            sentence_transcript.append(word_str + "|")

        res.append(sentence_transcript)

    return res

if __name__ == "__main__":
    #filename = "vety_HDS.ortho.txt"
    filename = "ukazka_HDS.ortho.txt"

    sentences_list_orig = read_input_file(filename)
    EPA_alphabet = rules.EPA_ALPHABET
    res = create_transcript(sentences_list_orig.copy(), EPA_alphabet)

    save_output_file(res, "vety_HDS_transcript.txt")
    print()


