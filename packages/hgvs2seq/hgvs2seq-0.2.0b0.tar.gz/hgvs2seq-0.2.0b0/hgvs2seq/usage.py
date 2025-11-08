# usage.py

import os
import sys
import argparse

import info


def chk_args(args, parser):
    if args.col and len(args.col) not in [1,2]:
        parser.print_usage()
        sys.exit("Error: option '-c|--col|--column' takes 1 or 2 arguments")
    if not os.path.isfile(args.query):
        parser.print_usage()
        sys.exit(f"Error: {args.query!r} must be a valid tsv file.")


show_messages = (
    "\033[1mMessage Explanations\033[0m\n"
    " Warning:                the sequence is created but notice the message.\n"
    " Error:                  the sequence is not created.\n"
    " MISSMATCH_VERSION:      for example, query:NM_032539.2 but reference is NM_032539.5.\n"
    " ALT_NO_OVERLAPPING_REF: the insertion is larger than the output sequence size, no reference nucleotide appears.\n"
    " NOT_CENTERED:           the variant is on one edge of the RNA sequence and has slipped to the side.\n"
    " TRUNCATED_REF:          the del/inv/dup variant is larger than output sequence size.\n"
    " TRUNCATED_ALT:          the ins/inv/dup variant is larger than output sequence size.\n"
)


def usage():
    """
    Help function with argument parser.
    https://docs.python.org/3/howto/argparse.html?highlight=argparse
    """
    doc_sep = '=' * 72
    parser = argparse.ArgumentParser(description= f'{doc_sep}{info.__doc__}{doc_sep}',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("-q", "--query",
                        help="Query as TSV format",
                        required=True,
                       )
    parser.add_argument("-r", "--ref", "--reference",
                        help="Annotation Fasta File, according the query",
                        required=True,
                       )
    parser.add_argument("-t", "--out-type",
                        type=str,
                        choices=["ref", "alt", "both"],
                        default="alt" ,
                        help="result contain only ALT, REF, or both sequences (defaul: alt)",
                       )
    parser.add_argument('-c', '--col', '--column',
                        help=("column index of the HGVS notation. The first column is '1' (or 'A'). "
                            "If HGVS is splitted in two columns (refseq & variant) specify the two "
                            "columns, for example '5 10': 5 is the column for the reference "
                            "(ex: NM_004006.2) and 10 is the column for the variant (ex: c.93+1G>T). "
                            "'E J' is the same. If not specified, hgvs2seq will try to find it "
                            "(one column only)."),
                        nargs="+",
                        ),
    parser.add_argument("-s", "--size",
                        type=int,
                        help="Output sequence size (default: 31)",
                        default=31,
                       )
    parser.add_argument("-a", "--add-columns",
                        help="Add one or more columns to header (ex: '-a 3 AA' will add columns "
                             "3 and 27). The first column is '1' (or 'A')",
                        nargs= '+',
                        )
    parser.add_argument('-o', '--output',
                        help="output file name (default: stdout)",
                        type=argparse.FileType('w'),
                       )
    parser.add_argument("-f", "--output-format",
                        choices=['fa', 'tsv'],
                        default='fa',
                        help=f"Output file format (default: fa)",
                        )
    parser.add_argument('-n', '--no-header',
                        action="store_true",
                        help="Query file has no header",
                        )
    parser.add_argument('-w', '--no-warnings',
                        action="store_true",
                        help="do not add warnings to fasta headers",
                        )
    parser.add_argument('-m', '--show-messages',
                        action="version",
                        version=show_messages,
                        help="Show Message explanations and quit",
                        )
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{info.VERSION}",
                       )
    ### Go to "usage()" without arguments or stdin
    if len(sys.argv) == 1 and sys.stdin.isatty():
        parser.print_help()
        sys.exit()
    return parser

