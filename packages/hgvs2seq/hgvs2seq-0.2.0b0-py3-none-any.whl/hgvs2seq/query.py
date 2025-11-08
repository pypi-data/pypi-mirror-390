"""
references sequences : 
 - RefSeq : NC_#.#, NT_#.#, NW_#.#, NG_#.#, NM_#.#, NR_#.#, NP_#.#
 - Ensembl : ENST#.#, ENSG#.#, ENSP#.#
 - LRG : LRG_#, LRG_#t#, LRG_#p#
Reference Sequence Types : c., g., m., n., o., p., r.
 - DNA
    g. = linear genomic reference sequence
    o. = circular genomic reference sequence
    m. = mitochondrial reference (special case of a circular genomic reference sequence)
    c. = coding DNA reference sequence (based on a protein coding transcript)
    n. = non-coding DNA reference sequence (based on a transcript not coding for a protein)
 - RNA
    r. = RNA reference sequence
 - protein
    p. = protein reference sequence

lien : https://hgvs-nomenclature.org/stable/background/refseq/
"""

import gzip
import ascii


REF_ALL = (
    'NM_', 'NC_', 'NT_', 'NW_', 'NG_', 'NR_', 'NP_',  # NCBI refseq
    'ENST', 'ENSG', 'ENSP',                           # Ensembl
    'LRG_',                                           # LRG 
)
REF_HANDLED = {
    'NM_':  {'src':'ncbi',    'type': 'transcript'},
    #'NR_':  {'ref':'ncbi',    'type': 'transcript'},
    # 'NG_':  {'ref':'ncbi',    'type': 'genomic'},
    'ENST': {'src':'ensembl', 'type': 'transcript'},
    #'ENSG': {'ref':'ensembl', 'type': 'genomic'},
    # 'LRG_': {'ref':'lrg',    'type': 'genomic'},
}
SEQTYPE_ALL = ('c.', 'g.', 'm.', 'n.', 'o.', 'p.', 'r.')
SEQTYPE_HANDLED = ('c.',)


sep = '\t'

### find for the 
def find_hgvs_info(self):
    """
    - if HGVS column number(s) is not given, parse each fields to detect it. 
    - check syntax
    """
    ### return object initialisation
    hgvs_info = {
        'status': 'not found',
        'col_id': False,
        'source': False,
        'ref_type': False,
        'prefix': False,
        'ref': False,
        'var': False,
        'msg': 'unexpected error',
    }
    
    ### get first line (regular or gzipped file)
    if self.args.query.endswith('.gz'):
        with gzip.open(self.args.query, "rt") as fh:
            header = fh.readline().rstrip() if not self.args.no_header else None
            line = fh.readline().rstrip().split(sep)
    else:
        with open(self.args.query, "r") as fh:
            header = fh.readline().rstrip() if not self.args.no_header else None
            line = fh.readline().rstrip().split(sep)

    ### HGVS column is given
    if self.args.col:
        col_id = [id-1 for id in ascii.get_index(self.args.col)]
        string = ":".join([line[id] for id in col_id])
        candidate = get_hgvs(string)

    ### HGVS column is not given: try to found it
    else:
        levels = {'not found':0, 'uncomplete':1, 'unmanaged':2, 'found':3}
        status = lambda x,y: x if levels[x] > levels[y] else y
        for _id, field in enumerate(line):
            candidate = get_hgvs(field)
            hgvs_info['status'] = status(candidate['status'], hgvs_info['status'])
            if candidate['status'] == 'found':
                col_id = [_id,]
                break
        ''' TODO IMPROVMENT
        if unmanaged or uncomplete REF, return the information, whith field count for each case
        '''

    if candidate['status'] == 'found':
        hgvs_info['status'] = candidate['status']
        hgvs_info['col_id'] = col_id
        hgvs_info['source'] = candidate['source']
        hgvs_info['ref_type'] = candidate['ref_type']
        hgvs_info['prefix'] = candidate['prefix']
        hgvs_info['ref'] = candidate['ref']
        hgvs_info['var'] = candidate['var']
        hgvs_info['msg'] = None
    else:
        hgvs_info['col_id'] = ascii.get_index(self.args.col)
        hgvs_info['msg'] = f"Error HGVS column ({candidate['status']})"

    ### return objet with:
    return hgvs_info


def get_hgvs(string):
    """ Function doc """
    hgvs = {
        'status':   'not found',  # 'not found', 'uncomplete', 'unmanaged', 'found'
        'source':   False,        # 'ensembl', 'ncbi', 'lrg'
        'ref_type': False,        # 'transcript', 'genomic', 'protein'
        'prefix':   False,        # 'c.', 'g.'
        'ref':      False,        # reference (ex: NM_004006.2))
        'var':      False,        # variant (ex: c.4375C>T)
    }
    
    ### Validate Syntax
    for ref_h in REF_HANDLED:
        ### Check syntax for Reference Sequence
        if string.startswith(ref_h):                                # is ref is managed ?
                                                                    # TODO: better ref control  
            ref, *var = string.split(':')
            if var:
                prefix = var[0][:2]
                ### Check syntax for Variant Sequence
                if prefix in SEQTYPE_HANDLED:                     # ref and prefix OK
                                                                    # TODO: better var control
                    hgvs['status'] = 'found'
                    hgvs['source'] = REF_HANDLED[ref_h]['src']
                    hgvs['ref_type'] = REF_HANDLED[ref_h]['type']
                    hgvs['prefix'] = prefix
                    hgvs['ref'] = ref
                    hgvs['var'] = var[0][2:]
                else:
                    hgvs['status'] = 'unmanaged' if prefix in SEQTYPE_ALL else 'unmanaged' 
            else:                                                   # ref only (miss var)
                hgvs['status'] = 'uncomplete'
        else:                                                       # ref is real but unmanaged
            for ref_a in REF_ALL:
                if string.startswith(ref_a) and ref_a not in REF_HANDLED:
                    hgvs['status'] = 'unmanaged'
    return hgvs
    

