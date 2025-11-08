# hvgs2seq

From a tabulated file, with an hgvs column (e.g. `NM_000142.4:c.1953G>A`), build a sequence of a 
fixed size (31 by default) around the variant.

- the hgvs could be splitted in two columns (e.g. col 1: `NM_000142.4` and col 2: `c.1953G>A`)
- when the variant is an indel largest than the specified size, the insertion/deletion will be
  truncated
- when the variant is located at the edge of the transcript, it will not be centered.
- not all hgvs nomenclature is covered.

