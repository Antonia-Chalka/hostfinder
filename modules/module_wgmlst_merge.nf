process module_wgmlst_merge {

    input:
    path wgmlst_files

    output:
    path "merged_wgmlst.tsv", emit: merged_wgmlst

    script:
    """
    #!/usr/bin/env python3
    import pandas as pd
    import sys

    # Get all wgmlst TSV files
    import glob
    tsv_files = sorted(glob.glob("*.tsv"))

    if not tsv_files:
        print("ERROR: No TSV files found to merge", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(tsv_files)} wgMLST files to merge", file=sys.stderr)

    # Read first file
    merged_df = pd.read_csv(tsv_files[0], delimiter='\t')
    gene_col = merged_df.columns[0]  # First column should be Gene or #GeneId

    # Merge remaining files
    for tsv_file in tsv_files[1:]:
        df = pd.read_csv(tsv_file, delimiter='\t')
        merged_df = merged_df.merge(df, on=gene_col, how='outer')

    # Save merged file
    merged_df.to_csv("merged_wgmlst.tsv", sep='\t', index=False)
    print(f"Successfully merged {len(tsv_files)} files. Output shape: {merged_df.shape}", file=sys.stderr)
    """
}
