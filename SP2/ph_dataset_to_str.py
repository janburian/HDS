from pathlib import Path

def phntrn_to_str(input_filename: Path, output_filename: Path):
    with open(input_filename, 'r', encoding='utf-8') as input:
        with open(output_filename, 'w', encoding='utf-8') as output:
            for line in input:
                line = line.split('|')
                sentence = line[1].strip()
                sentence = sentence.replace('$', '')
                output.write(sentence)
        output.close()
    input.close()

phntrn_to_str(Path("test.ph.epa.csv"), Path("test.ph.epa_str.txt"))
