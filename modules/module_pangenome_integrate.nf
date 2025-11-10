process module_pangenome_integrate {
    publishDir  "${params.outdir}/2.genomic_features/pangenome_integrate", mode: 'copy', overwrite: true  
    cache 'lenient'

    input:
    path annotation //from annotation_panaroo.collect()
    path pangenome_dir //  needs to have / in end
    val panaroo_threads


    output:
    path "${annotation.baseName}/gene_presence_absence_roary.csv", emit: pv_csv
    path "${annotation.baseName}/gene_presence_absence.Rtab", emit: pv_rtab
    path "${annotation.baseName}/combined_DNA_CDS.fasta", emit: combined_DNA_CDS
    path "${annotation.baseName}/final_graph.gml", emit: final_graph
    path "${annotation.baseName}/gene_data.csv", emit: gene_data
    path "${annotation.baseName}/gene_presence_absence.csv", emit: gene_presence_absence
    path "${annotation.baseName}/struct_presence_absence.Rtab", emit: struct_presence_absence
    path "${annotation.baseName}/summary_statistics.txt", emit: summary_statistics

    script:
    """
    panaroo-integrate -d '${pangenome_dir}/' -i '${annotation}' -t ${panaroo_threads} -o "${annotation.baseName}"

    """
}
