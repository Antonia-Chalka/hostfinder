process module_panaroo_merge {

    input:
    path folders
    val panaroo_threads
    
    output:
    path "panaroo_out", emit: out
    
    script:
    """
    panaroo-merge -d $folders -o "panaroo_out" -t $panaroo_threads  --merge_paralogs

    """
}