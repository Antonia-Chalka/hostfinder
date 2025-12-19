process module_pymlst_assign {

    input:
    path assembly
    path wgmlst_reference_file

    output:
        path "${assembly.baseName}_wgmlst.tsv", emit: wgmlst_single

    script:

    """
    cp $wgmlst_reference_file wgmlst_ref

    wgmlst add -s "${assembly.baseName}" wgmlst_ref $assembly

    wgMLST mlst wgmlst_ref > ${assembly.baseName}_wgmlst.tsv

    """

}
