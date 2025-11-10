process module_panaroo_batch {

    input:
    path folder  
    val panaroo_threads

    output:
    path "*_panaroo_out", emit: out
    
    script:
    """
    panaroo -i $folder/*.gff -o "${folder}_panaroo_out"  --clean-mode moderate -t $panaroo_threads --remove-invalid-genes --merge_paralogs
    
    """
}
