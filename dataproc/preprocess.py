from benepar.spacy_plugin import BeneparComponent
import glob
import os
from past2present import transform_present_span
import re
import spacy
import spacy.cli as spacy_cli

MIN_SENTENCE_CHAR_LENGTH = 5  # "I am." will qualify, but nothing shorter.


def clean_text(text, CHUNK_CHAR_LENGTH=1000):
    # Replace carraige return and tab characters.
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\t', ' ')
    # Standardize quotes/apostrophes.
    text = re.sub(r"’|‘", "'", re.sub(r"[ ]*`", "'", text))
    # Remove play character prompts like 'WALTER: ...'
    text = re.sub(
        r"^[A-Z0-9‘’'., ]+(?:\([^)]*\))?[:.][ ]*", '', text, flags=re.M)
    # Remove titles which are lines with all-caps.
    text = re.sub(r'^[A-Z0-9.,-?$#!;:\'’"_ ]+$', '', text, flags=re.M)
    # Remove divider lines like '* * * * *' and antiquated punctuation.
    text = re.sub(
        r'^[ ]*[-*=_].*[-*=_][ ]*$',
        '',
        re.sub(':--', ':', re.sub('&c', 'etc', text)),
        flags=re.M)
    # Remove leading spaces, then remove all line breaks except for empty lines.
    text = re.sub('\n(?=[^\n])', ' ', re.sub('^[ ]+', '', text), flags=re.M)
    # Remove footnotes and references
    # (they can be nested one deep: [Note [Note in note]])
    text = re.sub(
        r'\[[^][]+\]', '',
        re.sub(r'\[[^][]+\]', '', re.sub(r'^\[[^ ]+\] .*$', '', text,
                                         flags=re.M)))
    texts = []
    remainder = text
    N = len(remainder)
    start = 0
    end = 0
    while start < N:
        end += CHUNK_CHAR_LENGTH
        while end < N and remainder[end] != '\n':
            end += 1
        # Remove all newlines, double spaces and underscores.
        texts.append(
            re.sub(' [ ]+', ' ', re.sub('\n', ' ',
                                        remainder[start:end])).replace('_', ''))
        start = end
    return texts


def all_data(dirname):
    for fn in glob.glob(os.path.join(dirname, '*.txt')):
        with open(fn, 'r') as f:
            content = ''.join(
                    c for c in f.read() if c.isprintable() or c == '\n').strip()
            for text in clean_text(content):
                yield text


def preprocess(data_dir, output_fn, batch, threads):
    print('preparing text')
    data = all_data(data_dir)
    print('loading parser')
    try:
        nlp = spacy.load('en_core_web_lg')
    except IOError:
        spacy_cli.download('en_core_web_lg')
        nlp = spacy.load('en_core_web_lg')
    nlp.add_pipe(BeneparComponent("benepar_en"))
    with open(output_fn, 'w') as f:
        i = 0
        for doc in nlp.pipe(
                data, batch_size=batch, n_threads=threads):
            # benepar has no pipe() method, so manually invoke the pipe.
            doc = nlp.get_pipe('benepar')(doc)
            for sent in doc.sents:
                if len(sent.text) < MIN_SENTENCE_CHAR_LENGTH:
                    continue
                if i % 25 == 0:
                    print(f'{i}..', end='', flush=True)
                i += 1
                f.write('< ' + sent.text + '\n')
                f.write('> ' + transform_present_span(sent) + '\n')
    print('complete')


if __name__ == '__main__':
    import argparse

    DEFAULT_DATASET_FILENAME = 'dataset.txt'

    parser = argparse.ArgumentParser(
        description='preprocess data for translating past to present')
    parser.add_argument(
        '--only-clean', action='store_true', help='only clean text')
    parser.add_argument('--batch', type=int, default='16', help='batch size')
    parser.add_argument(
        '--threads', type=int, default='2', help='number of threads')
    parser.add_argument(
        'data_dir',
        metavar='DATA_DIR',
        default='/home/user/sync/src/org/theorems/data',
        help='directory of text files to preprocess')
    parser.add_argument(
        'output_file',
        metavar='OUTPUT_FILE',
        default=DEFAULT_DATASET_FILENAME,
        nargs='?',
        help='name of file to write output dataset to')
    args = parser.parse_args()

    if args.only_clean:
        for text in all_data(args.data_dir):
            print(text)
    else:
        preprocess(args.data_dir, args.output_file, args.batch, args.threads)
