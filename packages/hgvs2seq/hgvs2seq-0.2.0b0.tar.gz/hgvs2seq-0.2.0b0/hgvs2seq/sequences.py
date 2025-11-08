#!/usr/bin/env python3

'''
from hgvs string and according reference dictionary, it build sequence around the variant with the 
specified size
'''


import sys      # to debug (print to stderr)


COMP = {"A":"T", "T":"A", "C":"G", "G":"C", }


def extract_seq(self, string, i):
    ### info to return
    ref_seq = None  # REF sequence
    ref_alt = None  # ALT sequence
    warnings = []   # comments to add to fasta header
    
    ### decompose the string
    ref_name, var = string.split(':')
    type_var, var = var.split('.')

    ### Find reference sequence, even version is different
    try:
        reference_seq = self.reference_dict[ref_name]
    except KeyError:
        pattern, version = ref_name.split('.')
        if self.ref_versionned:
            ref_seqs = [ (k,v) for k,v in self.reference_dict.items() if k.startswith(f"{pattern}.")]
            if ref_seqs:
                warnings.append(f"MISSMATCH_VERSION:{version}->{ref_seqs[0][0].split('.')[-1]}")
            ### TODO : case where ref_seqs > 1
        else:
            ### With Ensembl GRCh37, transcripts have not associated version, whitch is a problem
            ref_seqs = [ (k,v) for k,v in self.reference_dict.items() if k == pattern ]
        ### case where refseq is not found in reference
        if not ref_seqs:
            return None, None, f"{pattern} not found in reference file"
        
        ref_name, reference_seq = ref_seqs[0][0], ref_seqs[0][1]        
    
    ### TODO : manage hgvs type (c., p., etc.)
    
    ### find for variant type (>, del, ins, delins, dup, inv)
    for j, char in enumerate(var):
        if not char.isnumeric() and char != '_':
            coord = var[:j]
            var = var[j:]
            break
                
    ### launch function relative to variant type
    # ~ print("coord, var:", coord, var) 
    if var[1] == ">":                   # Mutation
        ref_seq, alt_seq, mesg = get_mut_seq(self.reference_dict, ref_name, int(coord), var, self.corr, self.half, i)
    elif var.endswith("del"):           # deletion
        ref_seq, alt_seq, mesg = get_del_seq(self.args, self.reference_dict, ref_name, coord, var, self.corr, self.half, i)
    elif var.startswith("ins"):         # insertion
        ref_seq, alt_seq, mesg = get_ins_seq(self.args, self.reference_dict, ref_name, coord, var, self.corr, self.half, i)
    elif var.startswith("delins"):      # deletion/insertion
        ref_seq, alt_seq, mesg = get_delins_seq(self.args, self.reference_dict, ref_name, coord, var, self.corr, self.half, i)
    elif var.startswith("dup"):         # duplicate
        ref_seq, alt_seq, mesg = get_dup_seq(self.args, self.reference_dict, ref_name, coord, var, self.corr, self.half, i)
    elif var.startswith("inv"):         # inversion
        ref_seq, alt_seq, mesg = get_inv_seq(self.args, self.reference_dict, ref_name, coord, var, self.corr, self.half, i)
    else:                               # undetermined variant
        # ~ self.resp['warning'].append(f"Line {i+1}: hgvs not supported ({string})")
        return None, None, warnings

    ### add messages returned by functions to warnings
    warnings += mesg
    
    return ref_seq, alt_seq, warnings


def get_mut_seq(annot_dict, transcript, coord, var, corr, half, i):
    mesg = []
    len_transcript = len(annot_dict[transcript])
    ref = var[0]
    alt = var[2]
    offset_5 = coord - half -1
    start = max(0, offset_5)
    end = coord + half - corr
    offset_3_ref = len_transcript - end

    ### mutation is too close to the 5" edge (left)
    if offset_5 < 0:
        end -= offset_5
        mesg.append('NOT_CENTERED')
    
    ### mutation is too close to the 3" edge (right)
    if offset_3_ref < 0:
        mesg.append('NOT_CENTERED')
        start += offset_3_ref
        '''
        TODO : 
        - contrôler lorsque la toute derniere base est dupliquée
        '''

    ref_seq = annot_dict[transcript][start:end]
    alt_seq = annot_dict[transcript][start:coord-1] + alt + annot_dict[transcript][coord:end] 

    return ref_seq, alt_seq, mesg


def get_del_seq(args, annot_dict, transcript, coord, var, corr, half, i):
    mesg = []
    if "_" in coord:
        start_del, end_del = [int(i) for i in coord.split('_')]
        del_size = end_del+1 - start_del
        half_del_size = del_size // 2
        start_del -=1
        len_del = end_del - start_del
        len_transcript = len(annot_dict[transcript])
        offset_5_ref = start_del - half + half_del_size
        offset_5_alt = start_del - half
        
        ### reference start en end position
        ref_start = max(0, offset_5_ref)
        ref_end = ref_start + args.size
        offset_3_ref = len_transcript - ref_end
        
        alt_start = max(0, ref_start - half_del_size)
        alt_end = end_del+1 + half - corr
        offset_3_alt = len_transcript - alt_end
        
        ### deletion is too close to the 5" edge
        if offset_5_alt < 0:
            mesg.append('NOT_CENTERED')
            ### when deletion is larger than kmer
            offset_5_alt = start_del - half
            if offset_5_ref > 0:
                alt_end -= offset_5_alt
            else:
                alt_end += abs(offset_5_ref) + half_del_size
            if alt_start >= start_del:
                mesg.append('ALT_NO_OVERLAPPING_REF')
        
        
        ### deletion is too close to the 3" edge
        if offset_3_ref < 0:
            mesg.append('NOT_CENTERED_REF')
            ref_start += offset_3_ref
            alt_start = ref_start - len_del
            '''
            TODO : 
            - que ce passe t-il quand la déletion est plus grande que le kmer
            '''
        elif offset_3_alt < 0:
            if offset_3_alt < -1:
                mesg.append('NOT_CENTERED_ALT')
            alt_start += offset_3_alt
        
        ref_seq = annot_dict[transcript][ref_start:ref_end]
        alt_seq = annot_dict[transcript][alt_start:start_del] + annot_dict[transcript][end_del:alt_end]

        if del_size > args.size:
            mesg.append('TRUNCATED_REF')
            # ~ MESSAGES["warning"].append((args, i, del_size, "deletion"))       # TODO : add warning message

        return ref_seq, alt_seq, mesg

    else:
        len_transcript = len(annot_dict[transcript])
        # ~ print("coord:", coord)
        coord = int(coord)
        offset_5 = coord - half -1
        ref_start = alt_start = max(0, offset_5)
        ref_end = coord + half - corr
        offset_3_ref = len_transcript - ref_end

        if offset_5 < 0:
            mesg.append('NOT_CENTERED')
            ref_end -= offset_5
        
        ### deletion is too close to the 3" edge
        if offset_3_ref < 0:
            mesg.append('NOT_CENTERED')
            ref_start += offset_3_ref
            alt_start = ref_start -1
            '''
            TODO : 
            - que ce passe t-il quand la déletion est plus grande que le kmer (voir les offset_3 des deletion)
            - contrôler lorsque la toute derniere base est dupliquée
            '''
        
        ref_seq = annot_dict[transcript][ref_start:ref_end]
        alt_seq = annot_dict[transcript][alt_start:coord-1] + annot_dict[transcript][coord:ref_end+1] 

        return ref_seq, alt_seq, mesg


def get_ins_seq(args, annot_dict, transcript, coord, var, corr, half, i):
    mesg = []
    len_transcript = len(annot_dict[transcript])
    ins_seq = var[3:]
    ins_seq_corr = len(ins_seq) % 2
    len_ins = len(ins_seq)
    # ~ len_ins = min(len(ins_seq), args.size)
    half_ins_size = len(ins_seq) // 2

    ### reference start/end positions
    start_ins, end_ins = [int(i) for i in coord.split('_')]
    start_ins -=1
    offset_5_ref = start_ins - half + corr
    ref_start = max(0, offset_5_ref)
    ref_end = ref_start + args.size

    ### alternate start/end position
    alt_start = ref_start + half_ins_size + ins_seq_corr
    alt_end = ref_end - half_ins_size
    offset_3_ref = len_transcript - ref_end
    offset_3_alt = len_transcript - alt_end

    ### insertion is too close to the 5" edge
    if offset_5_ref < 0:
        mesg.append('NOT_CENTERED_REF')
        alt_start = ref_start
        # ~ alt_end = args.size - len_ins
        alt_end = max(args.size - len_ins, 0)
    # ~ if offset_5_alt < 0:
        # ~ mesg.append('NOT_CENTERED_ALT')
        # ~ alt_end = args.size - len_ins 

    ### insertion is too close to the 3" edge
    if offset_3_ref < 0:
        mesg.append('NOT_CENTERED_REF')
        ref_start += offset_3_ref
        if offset_3_alt < 0:
            alt_start = ref_start + len_ins
        '''
        TODO : 
        - que ce passe t-il quand l'insertion est plus grande que le kmer
        - contrôler lorsque la toute derniere base est insérée (si c'est possible)  
        '''

    ref_seq = annot_dict[transcript][ref_start:ref_end]
    alt_seq = annot_dict[transcript][alt_start:start_ins+1] + ins_seq + annot_dict[transcript][end_ins-1:alt_end]

    ### when the insertion exceeded output alt sequence size
    if len_ins > args.size:
        mesg.append('TRUNCATED_ALT')
        ### reduce alt_seq to args.size
        rm_to_alt, rm_to_alt_corr = divmod(len_ins - args.size,  2)  # divmod() => result and modulo
        alt_seq = ins_seq[rm_to_alt:-rm_to_alt - rm_to_alt_corr]

    if len_ins+1 >= args.size:
        mesg.append('ALT_NO_OVERLAPPING_REF')

    # ~ print('\n', transcript, coord, var, file=sys.stderr)
    # ~ print("var:", var, file=sys.stderr)
    # ~ print("ins_seq:", ins_seq, file=sys.stderr)
    # ~ print("len_ins:", len_ins, file=sys.stderr)
    # ~ print("half_ins_size:", half_ins_size)
    # ~ print("message:", mesg, file=sys.stderr)
    # ~ print("offset_5_ref:", offset_5_ref, file=sys.stderr)
    # ~ print("offset_5_alt:", offset_5_alt, file=sys.stderr)
    # ~ print("offset_5 diff:", offset_5_ref - offset_5_alt, file=sys.stderr)
    # ~ print("offset_3:", offset_3, file=sys.stderr)
    # ~ print("offset_3_ref:", offset_3_ref, file=sys.stderr)
    # ~ print("offset_3_alt:", offset_3_alt, file=sys.stderr)
    # ~ print("len transcript, alt_end", len_transcript, alt_end, file=sys.stderr)
    # ~ print("ref_start, ref_end:", ref_start, ref_end, file=sys.stderr)
    # ~ print("alt_start, alt_end:", alt_start, alt_end, file=sys.stderr)
    # ~ print("len_del:", len_del, file=sys.stderr)
    # ~ print("del seq:",annot_dict[transcript][start_del:end_del] , file=sys.stderr)
    # ~ print("diff len (del - ins):", len_del - len_ins, file=sys.stderr)
    # ~ print("alt_start, alt_end:", alt_start, alt_end, file=sys.stderr)
    # ~ print("start_ins, end_ins:", start_ins, end_ins, file=sys.stderr)
    # ~ if len_ins > args.size:
        # ~ print("rm_to_alt:", rm_to_alt, file=sys.stderr)
        # ~ print("rm_to_alt_corr:", rm_to_alt_corr, file=sys.stderr)
    # ~ print(ref_seq, file=sys.stderr)
    # ~ print(alt_seq, file=sys.stderr)
    # ~ print("len_del, del_ins:", len_del, len_ins, file=sys.stderr)
    # ~ print(annot_dict[transcript], file=sys.stderr)

    return ref_seq, alt_seq, mesg


def get_delins_seq(args, annot_dict, transcript, coord, var, corr, half, i):
    '''
    Variable      : example - explanation
    -------------------------------------
    transcript    : ENST001     - transcript name
    coor          : 3320_3325   - coordinates
    var           : delinsATTTC - type (delins) and nucleotindes inserted
    half          : 15          - args.size - 1
    
    ins_seq       : ATCGCT      - nucleotides inserted
    ins_seq_cor   : 0           - 1 if lenght of ins_seq is unpair, else 0
    half_ins_size : 5           - number of nuclotides inserted / 2
    start_ins     : 3320        - position of first nucleotide inserted
    end_ins       : 3325        - position of the last nucleotide inserted
    ref_start     :             - position of the first nucleotide of the reference sequence
    ref_end       :             - position of the last nucleotide of the reference sequence
    alt_start     :             - position of the first nucleotide of the alternate sequence
    alt_end       :             - position of the last nucleotide of the alternate sequence
    '''
    mesg = []
    len_transcript = len(annot_dict[transcript])
    ins_seq = var[6:]
    coords = [int(i) for i in coord.split('_')]

    ### positions of deletions and insertion (-1 : 0 based)
    start_del = start_ins = coords[0]-1
    start_ins -= 1
    end_del = coords[1] if len(coords) == 2 else coords[0]
    end_ins = start_ins + len(ins_seq)
    len_ins = len(ins_seq) 
    half_ins_size = len_ins // 2
    len_del = end_del - start_del
    half_del_size = len_del // 2
    
    ### Alternate started and ended positions
    ins_seq_corr = 1 if len(ins_seq) % 2 else 0 
    # ~ offset_5_alt = start_del - half + half_ins_size  + ins_seq_corr
    offset_5_alt = start_ins - half + half_ins_size + ins_seq_corr + corr
    alt_start = max(0, offset_5_alt)
    alt_end = end_del + half - half_ins_size

    ### Reference started and ended positions
    del_seq_corr = 1 if (start_del - end_del) % 2 else 0
    # ~ offset_5_ref = start_del - half + half_del_size + del_seq_corr
    offset_5_ref = start_del-1 + half_del_size - half + del_seq_corr + corr
    ref_start = max(0, offset_5_ref)
    ref_end = ref_start + args.size
    offset_3_ref = len_transcript - ref_end
    offset_3_alt = len_transcript - alt_end

    ### deletion is too close to the 5" edge (REF)
    if offset_5_ref < 0:
        mesg.append('NOT_CENTERED_REF')
        alt_end += abs(offset_5_ref) + half_del_size
    if offset_5_alt < 0:
        mesg.append('NOT_CENTERED_ALT')
        alt_end = args.size + len_del - len_ins        
        '''
        ### when deletion is larger than kmer
        if offset_5_ref > 0:
            alt_end -= offset_5_alt
        '''
        
    ### delins is too close to the 3" edge
    if offset_3_ref < 0:
        mesg.append('NOT_CENTERED_REF')
        ref_start += offset_3_ref
        alt_start = ref_start - len_del + len_ins 
        '''
        TODO : attention aux multiples cas de figure :
        - insertion plus grande que le kmer
        - deletion plus grande que le kmer
        - insertion + deletion plus grandes que le kmer
        - ...
        '''
    elif alt_end > len_transcript:
        mesg.append('NOT_CENTERED_ALT')
        alt_start += offset_3_alt

    ref_seq = annot_dict[transcript][ref_start:ref_end]
    alt_seq = annot_dict[transcript][alt_start:start_ins+1] + ins_seq + annot_dict[transcript][end_del:alt_end]

    ### Warning when the del/ins exceeded k lenght
    del_size = end_del - start_del
    if  del_size > args.size:
        mesg.append('TRUNCATED_REF')
        # ~ MESSAGES["warning"].append((args, i, del_size, "deletion"))       # TODO : add warning message
    if len_ins > args.size:
        mesg.append('TRUNCATED_ALT')
        # ~ MESSAGES["warning"].append((args, i, len_ins, "insertion"))       # TODO : add warning message
        ### reduce alt_seq to args.size
        rm_to_alt = (len_ins - args.size) // 2
        rm_to_alt_corr = (len_ins - args.size + 1)  % 2
        alt_seq = alt_seq[rm_to_alt:-rm_to_alt+rm_to_alt_corr-1]

    ### when a variant start or finish on the edge, ALT can't wrapps it
    if alt_start >= start_del:
        mesg.append('ALT_NO_OVERLAPPING_REF')

    return ref_seq, alt_seq, mesg


def get_dup_seq(args, annot_dict, transcript, coord, var, corr, half, i):
    mesg = []
    ### position of duplication (-1 : 0 based)
    len_transcript = len(annot_dict[transcript])
    coords = [int(nb) for nb in coord.split('_')]
    start_dup = coords[0]-1
    end_dup = coords[1] if len(coords) == 2 else coords[0]
    len_dup = end_dup - start_dup
    dup_seq = annot_dict[transcript][start_dup:end_dup]
    
    ### Reference start and end positions
    offset_5_ref = start_dup - half + len_dup//2 + corr -1
    ref_start = max(0, offset_5_ref)
    ref_end = ref_start + args.size
    offset_3 = len_transcript - ref_end
    
    ### Alternate start and end positions
    offset_5_alt = start_dup - half + corr + len_dup - 1
    alt_start = max(0, offset_5_alt)
    alt_end = end_dup + half - len_dup
    

    ### Duplicate is too close to the 5" edge
    if offset_5_ref < 0:
        mesg.append('NOT_CENTERED_REF')
    if offset_5_alt < 0:
        mesg.append('NOT_CENTERED_ALT')
        to_add = args.size - alt_end - len_dup
        alt_end += to_add
        '''
        TODO
        - Si le duplicat dépasse, que ce passe t-il
            - peut-être en recentrant, il peut ne plus dépasser
            - ajouter un warning
        '''

    ### duplicate is too close to the 3" edge
    if offset_3 < 0:
        mesg.append('NOT_CENTERED')
        ref_start += offset_3
        alt_start = ref_start + len_dup
        '''
        TODO : 
        - que ce passe t-il quand le duplicat // 2 est plus grand que le kmer
        - que ce passe t-il quand la duplicat est plus grand que le kmer
        - contrôler lorsque la toute derniere base est dupliquée  
        '''

    ### get ref and alt sequences
    ref_seq = annot_dict[transcript][ref_start:ref_end]
    alt_seq = annot_dict[transcript][alt_start:start_dup] + dup_seq + dup_seq + annot_dict[transcript][end_dup:alt_end]

    ### Warning when the duplicate exceeded output sequence
    if len_dup * 2  > args.size:
        if len_dup > args.size: 
            mesg.append('TRUNCATED_REF')
        mesg.append('TRUNCATED_ALT')
        # ~ MESSAGES["warning"].append((args, i, len_dup, "duplication"))       # TODO : add warning message
        ### reduce alt_seq to args.size
        rm_to_alt = (len(alt_seq) - args.size) // 2
        alt_seq = alt_seq[rm_to_alt:-rm_to_alt-1+corr]

    if len_dup*2 + 1 >= args.size:
        mesg.append('ALT_NO_OVERLAPPING_REF')

    return ref_seq, alt_seq, mesg


def get_inv_seq(args, annot_dict, transcript, coord, var, corr, half, i):
    mesg = []
    ### positions of invertion (-1 : 0 based)
    start_inv, end_inv = [int(nb) for nb in coord.split('_')]
    start_inv -= 1
    len_inv = end_inv - start_inv
    corr_len_inv = len_inv % 2

    ### Reference/altenate start and end positions
    start = max(0, start_inv - half + len_inv//2)
    end = start + args.size

    ### position of inversion (-1 : 0 based)
    inv_ref_seq = annot_dict[transcript][start_inv:end_inv]
    inv_alt_seq = ''.join([COMP[nuc] for nuc in inv_ref_seq[::-1]])

    ### get ref and alt sequences
    ref_seq = annot_dict[transcript][start:end]
    alt_seq = annot_dict[transcript][start:start_inv] + inv_alt_seq + annot_dict[transcript][end_inv:end]

    ### Warning when the inversion exceeded output sequence
    if len_inv > args.size:
        mesg.append('TRUNCATED_REF TRUNCATED_ALT')
        # ~ MESSAGES["warning"].append((args, i, len_inv, "inversion"))       # TODO : add warning message
        ### reduce alt_seq to args.size
        rm_to_alt = (len_inv - args.size) // 2
        alt_seq = alt_seq[rm_to_alt:-rm_to_alt-1+corr]

    return ref_seq, alt_seq, mesg


def output_results(args, REF_RESULTS, ALT_RESULTS):
    file = args.out_file or sys.stdout
    match args.out_type:
        case "alt":
            for i,raw in enumerate(REF_RESULTS):
                print(ALT_RESULTS[i], file=file)
        case "ref":
            for i,raw in enumerate(REF_RESULTS):
                print(REF_RESULTS[i], file=file)
        case "both":
            for i,raw in enumerate(REF_RESULTS):
                print(REF_RESULTS[i], file=file)
                print(ALT_RESULTS[i], file=file)


def output_messages(args, MESSAGES):
    if MESSAGES["error"]:
        print("\nERRORS:")
        for args, i, size, type in MESSAGES["warning"]:
            print(f" Line {i+1}: {type.capitalize()} larger than the sequence ({size} > {args.size}).", file=sys.stderr)
    if MESSAGES["warning"]:
        print("\nWARNINGS:")
        for args, i, size, type in MESSAGES["warning"]:
            print(f"- Line {i+1}: {type.capitalize()} larger than the sequence ({size} > {args.size}).", file=sys.stderr)
        

def warning(args, i, size, type):
    print(f"Line {i+1}: {type.capitalize()} larger than the sequence ({size} > {args.size}), output truncated.", file=sys.stderr)


