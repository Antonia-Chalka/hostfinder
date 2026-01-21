process module_pangenome_merge {

    input:
    path pangenome_files

    output:
    path "merged_pangenome.csv", emit: merged_pangenome

    script:
    """
    #!/usr/bin/env python3
    import pandas as pd
    import sys
    import glob

    # Get all matched presence/absence CSV files
    csv_files = sorted(glob.glob("*_gene_presence_absence_matched.csv"))

    if not csv_files:
        print("ERROR: No matched presence/absence CSV files found to merge", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(csv_files)} pangenome files to merge", file=sys.stderr)

    # Read first file
    merged_df = pd.read_csv(csv_files[0], delimiter=',')
    gene_col = 'Gene' if 'Gene' in merged_df.columns else merged_df.columns[0]

    # Merge remaining files
    for csv_file in csv_files[1:]:
        df = pd.read_csv(csv_file, delimiter=',')
        merged_df = merged_df.merge(df, on=gene_col, how='outer')

    # Save merged file
    merged_df.to_csv("merged_pangenome.csv", index=False)
    print(f"Successfully merged {len(csv_files)} files. Output shape: {merged_df.shape}", file=sys.stderr)
    """
}
