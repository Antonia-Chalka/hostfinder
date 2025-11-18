process module_pangenome_integrate {
    publishDir  "${params.outdir}/2.genomic_features/pangenome_integrate", mode: 'copy', overwrite: true  
    cache 'lenient'

    input:
    path annotation //from annotation_panaroo.collect()
    path pangenome_dir //  needs to have / in end
    val panaroo_threads


    output:
    path "${annotation.baseName}/", emit: test_dir
    path "${pangenome_dir}/gene_data.csv", emit: gene_data_file_ref
    path "${pangenome_dir}/final_graph.gml", emit: gml_file_ref

    script:
    """
    panaroo-integrate -d '${pangenome_dir}/' -i '${annotation}' -t ${panaroo_threads} -o "${annotation.baseName}"

    """
}
