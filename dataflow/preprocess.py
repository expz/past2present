from __future__ import print_function
import glob
import os


MIN_CHARS_PER_FILE = 9000
OUTFILE_PREFIX = 'data'


def get_next_chunk_no(outfile_dir, outfile_prefix):
    chunk_fns = glob.glob("%s/%s-*.txt" % (outfile_dir, outfile_prefix))
    if not chunk_fns:
        return 1
    last_chunk_fn = os.path.basename(sorted(chunk_fns)[-1])
    return int(last_chunk_fn[len(outfile_prefix) + 1:-4]) + 1


def split_files(infile_dir, outfile_dir, outfile_prefix):
    for fn in sorted(glob.glob("%s/*.txt" % (infile_dir,))):
        with open(fn, 'r') as f:
            chunk_lines = []
            chunk_no = get_next_chunk_no(outfile_dir, outfile_prefix)
            print('starting with chunk %d' % (chunk_no,))
            init_chunk_no = chunk_no
            c = 0
            for line in f:
                c += len(line)
                chunk_lines.append(line)
                if c > MIN_CHARS_PER_FILE:
                    if line.strip() == '':
                        write_chunk(chunk_lines,
                                    chunk_no,
                                    outfile_dir,
                                    outfile_prefix)
                        chunk_no += 1
                        chunk_lines = []
                        c = 0
            if chunk_lines:
                write_chunk(chunk_lines,
                            chunk_no,
                            outfile_dir,
                            outfile_prefix)
            print('wrote %d chunks' % (chunk_no + 1 - init_chunk_no,))


def write_chunk(chunk_lines, chunk_no, outfile_dir, outfile_prefix):
    out_fn = "%s/%s-%05d.txt" % (outfile_dir, outfile_prefix, chunk_no)
    with open(out_fn, 'w') as out_f:
        out_f.write(''.join(chunk_lines))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='break up long text files into small ones < 10kb')
    parser.add_argument(
        '--raw',
        metavar='RAW_DATA_DIR',
        help='directory with text files to break up')
    parser.add_argument(
        '--chunk',
        metavar='CHUNK_DATA_DIR',
        help='directory where to store broken up text files')
    args = parser.parse_args()

    split_files(args.raw, args.chunk, OUTFILE_PREFIX)
