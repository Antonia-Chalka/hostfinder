process module_pangenome_match {

    input:
    path merge_script
    path gene_data_file_ref
    path gml_file_ref
    path model_features_file
    path test_dirs


    output:
        path "matched_panaroo_output/*/*_gene_presence_absence_matched.csv", emit: matched_presence_absence

    script:

    """
    python $merge_script \\
    --gene_data_file_ref $gene_data_file_ref \\
    --gml_file_ref $gml_file_ref  \\
    --model_features_file $model_features_file \\
    --test_dirs $test_dirs \\
    --out_dir matched_panaroo_output

    """

}
