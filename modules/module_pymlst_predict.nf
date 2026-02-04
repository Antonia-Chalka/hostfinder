process module_pymlst_predict {
    publishDir  "${params.outdir}/${input_data}_predictions", mode: 'copy', overwrite: true

    input:
    
    val model_test_wgmlst_script
    path input_data
    val model_dir
    val threshold_config

    output:
    path "wgmlst_predictions.tsv", emit: predictions
    
    script:
    def output_dir = "model_predictions_output"
    
    """
    mkdir -p ${output_dir}
    
    python $model_test_wgmlst_script \\
        --input_data ${input_data} \\
        --model_dir ${model_dir} \\
        --threshold_config ${threshold_config} \\ 
    """

}





