process module_pangenome_predict {
    publishDir  "${params.outdir}/${input_data}_predictions", mode: 'copy', overwrite: true

    input:
    path model_test_pangenome_script
    path input_data
    path model_dir
    path threshold_config

    output:
    path "pangenome_predictions.tsv", emit: predictions
    
    script:
    
    """
    python $model_test_pangenome_script \\
        --input_data ${input_data} \\
        --model_dir ${model_dir} \\
        --threshold_config ${threshold_config} 
    """

}

