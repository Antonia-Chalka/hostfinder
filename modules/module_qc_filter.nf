// Filter assemblies based on quast-derived metrics
process module_qc_filter {
    publishDir  "${params.outdir}/1.assembly_quality/good_assemblies/", mode: 'copy', overwrite: true, pattern : "*.${assembly_extension}"
    publishDir  "${params.outdir}/1.assembly_quality/", mode: 'copy', overwrite: true, pattern : 'good_noext_metadata.csv'

    cache 'lenient'

    input:
    path qcs
    path metadata_file
    path assembly_dir, stageAs: "*"
    val assembly_extension
    val as_ln_upr
    val as_ln_lwr
    val ctg_count
    val largest_ctg
    val n50
    val gc_upr
    val gc_lwr

    output:
    path "*.${assembly_extension}", emit: good_assemblies
    path 'good_metadata.csv', emit: good_metadata
    path 'pass_qc.tsv', emit: good_assemblies_list

    script:
    """
    set -euo pipefail
    
    # Validate inputs
    [ -f "$qcs" ] || { echo "ERROR: QC file $qcs not found"; exit 1; }
    [ -f "$metadata_file" ] || { echo "ERROR: Metadata file $metadata_file not found"; exit 1; }
    [ -d "$assembly_dir" ] || { echo "ERROR: Assembly directory ${assembly_dir} not found"; exit 1; }

    # Create list of assemblies that pass qc & Copy them
    awk -F "\t" '{ 
        if( (\$2 < ${ctg_count}) && 
            (\$8 > ${as_ln_lwr} && \$8 < ${as_ln_upr}) && 
            (\$15 > ${largest_ctg}) && 
            (\$17 > ${gc_lwr} && \$17 < ${gc_upr}) && 
            (\$18 > ${n50})) { 
            print 
        } 
    }' "${qcs}" > pass_qc.tsv

# Check if any assemblies passed QC
    [ -s pass_qc.tsv ] || { echo "ERROR: No assemblies passed QC criteria"; exit 100; }



    # Create symlinks for passing assemblies
    while IFS= read -r line; do
        assembly_name=\$(echo "\$line" | cut -f1)
        assembly_path="${assembly_dir}/\${assembly_name}.${assembly_extension}"
        
        # Check if source file exists before creating symlink
        if [ -f "\$assembly_path" ]; then
            cp "\$assembly_path" "\${assembly_name}.${assembly_extension}"
        else
            echo "WARNING: Assembly file '\$assembly_path' not found, skipping"
        fi
    done < pass_qc.tsv
    
    # Add headers to new metadata file by copying the first line of the orginal metadata file
    head -n 1 "${metadata_file}" > good_metadata.csv
    
    # Create list of good assemblies that were successfully linked
    ls -1 *.${assembly_extension} 2>/dev/null > good_assemblies.txt || touch good_assemblies.txt
    
    # Append matching metadata entries
    while IFS= read -r assembly_file; do
        assembly_name=\$(basename "\$assembly_file" .${assembly_extension})
        grep -m 1 -F "\$assembly_name" "${metadata_file}" >> good_metadata.csv || echo "WARNING: No metadata found for \$assembly_name"
    done < good_assemblies.txt


    # Create version with extensions removed
    awk 'NR==1 {print; next} 
        { gsub(/\\.${assembly_extension}/,"", \$1); print }' good_metadata.csv > good_noext_metadata.csv
    
    """
}
