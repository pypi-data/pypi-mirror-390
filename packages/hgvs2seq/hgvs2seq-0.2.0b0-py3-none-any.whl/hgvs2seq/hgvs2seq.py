#!/usr/bin/env python3


'''
- step 1
    - If not specified by '-c' option, find HGVS column index
    - Sinon, vérifier si le début de syntaxe correspond bien à une des entrées du dict refseqs
- step 2
    - load the reference file (Ensembl, NCBI, LRG (deprecated))
- step 3, for each query file row:
    - vérifier si la notation HGVS est correcte
        - incorrecte -> message à afficher
        - non prise en charge -> message à afficher
    - compute and add sequence
- step 4
    - outputs sequences (stdout or file, as fasta/tsv format)
    - outputs messages (stderr)


methods:
 - hgvs.find_hgvs_info()
    - retourne l'indice de la colonne hgvs si celle-ci n'est pas indiquée.
    - input:
    - output:
 - hgvs.extract_seq('NM_182763.2:c.688+403C>T')
    - retourne une instance ou un dictionnaire pour notre hgvs
    - gére les formats hgvs non pris en charge
    - gére une notation incompréhensible
    - input:
    - output:
'''


import os
import sys
import gzip
from Bio import SeqIO

import ascii
from usage import usage, chk_args
from query import find_hgvs_info
from sequences import extract_seq


def main():
    ### Manage arguments
    parser=usage()
    args=parser.parse_args()
    chk_args(args, parser)

    ### load HGVS class
    hgvs = HGVS(args)

    if not hgvs.resp['is_ok']:
        output(args, hgvs)
        return

    ### load reference fasta file (ref_versionned = False with GRCh37)
    hgvs.reference_dict, hgvs.ref_versionned = load_ref_fasta_file(args)

    ### check if reference_dict match with query
    if not hgvs.is_ref_match_query():
        sys.exit(f"{COL.RED}Error: the reference and query files do not match:\n"
                f"  first reference item : {next(iter(hgvs.reference_dict))}\n"
                f"  first query entry: {hgvs.info['ref']}")

    ### get sequences
    hgvs.get_seq()

    ### output results
    output(args, hgvs)


def load_ref_fasta_file(args):
    """
    - The reference fasta file must be loaded outside the class to be used as a library.
    - Regular or gzip files are accepted
    """
    reference_dict = {}
    # Open gzipped FASTA file or regular FASTA file
    try:
        if args.ref.endswith('.gz'):
            ref_stream = gzip.open(args.ref, "rt")
        else:
            ref_stream = open(args.ref)
    except FileNotFoundError:
        exit(f"{COL.RED}FileNoFoundError: {args.ref}{COL.END}")
    for record in SeqIO.parse(ref_stream, "fasta"):
        reference_dict[record.id] = record.seq
    ### With Ensembl GRCh37, transcripts have no associated version, whitch is a problem
    ref_versionned = True if len(next(iter(reference_dict)).split('.')) == 2 else False
    return reference_dict, ref_versionned


class HGVS:
    """ Class doc """
    find_hgvs_info = find_hgvs_info
    extract_seq = extract_seq

    def __init__(self, args):
        """ Class initialiser """
        self.args = args
        self.reference_dict = False
        self.resp = {
            "is_ok": True,
            "result": [],
            "warning": [],
            "error": None
        }

        ### find for HGVS index column
        self.info = self.find_hgvs_info()
        if not self.info['status'] == 'found':
            self.resp['is_ok'] = False
            self.resp['error'] = self.info['msg']

        ### Columns added to fasta headers (columns chars are converted as index, ex: AA -> 27)
        self.cols_id = ascii.get_index(args.add_columns)


    ### Run sequence building
    def get_seq(self):
        ### general info to build sequences
        self.corr = 0 if self.args.size % 2 else 1
        self.half = self.args.size // 2
        ### info to output rendered
        col_sep = ' ' if self.args.output_format == 'fa' else '\t'
        
        ### get first line (regular or gzipped file)
        if self.args.query.endswith('.gz'):
            fh = gzip.open(self.args.query, "rt")
        else:
            fh = open(self.args.query, "r")
        
        ### keep header
        if not self.args.no_header:
            header = fh.readline().rstrip().split()
        
        ### if output is as tsv, add header
        if self.args.output_format == 'tsv' and not self.args.no_header:
            colnames = '\t'.join([header[int(i)-1] for i in self.cols_id])
            added_cols = f"\t{colnames}" if self.args.add_columns else ''
            self.resp["result"].append(f"sequence{col_sep}hgvs{col_sep}type{added_cols}")
        
        ### for each row of query file
        nrow = 1
        for row in fh:
            ### get HGVS string
            fields = row.rstrip().split('\t')
            string = ":".join([fields[id] for id in self.info["col_id"]])
            ### build REF and ALT sequences
            ref_seq, alt_seq, warnings = self.extract_seq(string, nrow)
            nrow+=1
            
            ### if ref_seq is None, the item is not treated and the warning is an error
            if not ref_seq:
                self.resp['warning'].append(f"Line {nrow}: Error:{string.split(':')[0]} not found in reference file, ignored")
                continue
            
            ### add result to resp dict
            warn_stdout = f"Warnings:{','.join(warnings)}" if warnings else ''
            warn_file = f"Warnings:{','.join(warnings)}" if warnings and not self.args.no_warnings else ''
            ## append additional selected columns to the header
            col_sep = ' ' if self.args.output_format == 'fa' else '\t'
            added_cols = f"{col_sep}{col_sep.join([fields[num-1] for num in self.cols_id])}" if self.cols_id else ''
            ## append to list according of output format
            if self.args.output_format == "tsv":
                if self.args.out_type in ['ref', 'both']:
                    self.resp['result'].append(f"{ref_seq}{col_sep}{string}_ref {col_sep}ref{added_cols}")
                if self.args.out_type in ['alt', 'both']:
                    self.resp['result'].append(f"{alt_seq}{col_sep}{string}_alt {col_sep}alt{added_cols}")
            else:
                if self.args.out_type in ['ref', 'both']:
                    self.resp['result'].append(f">{string}|ref{added_cols} {warn_file}")
                    self.resp['result'].append(ref_seq)
                if self.args.out_type in ['alt', 'both']:
                    self.resp['result'].append(f">{string}|alt{added_cols} {warn_file}")
                    self.resp['result'].append(alt_seq)
            if warn_stdout:
                self.resp['warning'].append(f"Line {nrow}: {warn_stdout}")


    def is_ref_match_query(self):
        """ Function doc """
        if next(iter(self.reference_dict))[:3] != self.info['ref'][:3]:
            return False
        return True


def output(args, hgvs):
    ### OUTPUT RESULTS
    output = args.output or sys.stdout

    if hgvs.resp["is_ok"]:
        ## output results in file/stdout
        if hgvs.resp["result"]:
            for result in hgvs.resp["result"]:
                print(result, file=output)
            if args.output:
                print(f"\n🧬 {args.output.name} succefully created.\n")
        ### WARNINGS
        if hgvs.resp["warning"]:
            print(f"{COL.PURPLE}⚠️  Warnings:", file=sys.stderr)
            for warning in hgvs.resp["warning"]:
                print(f"  {warning}", file=sys.stderr)
            print(COL.END, file=sys.stderr)
    else:
        print(f"\n☠️  {COL.RED}{hgvs.resp['error']}\n")


class COL:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


if __name__ == "__main__":
    main()
