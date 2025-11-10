process module_file_batch {

    input:
        path merge_script
        path gml_file_ref
        path model_features_file
        path test_dirs

        val batch_size

    output:
        path out_dir

    script:

    """

    python ./code/panaroo_merge_process.py \
    --gene_data_file_ref  ./data/2.bacterial_pangenome/gene_data.csv \
    --gml_file_ref ./data/2.bacterial_pangenome/final_graph.gml \
    --model_features_file ./data/4.3.panphage_model_out_v3/feature_bacteria.txt \
    --test_dirs ./data/5.testing/<test_folder>/2.pangenome/1.panaroo_merge_out \
    --out_dir ./data/5.testing/<test_folder>/2.pangenome/2.panaroo_match/

    """

}
