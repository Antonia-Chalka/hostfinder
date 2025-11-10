process module_file_batch {

    input:
        path files
        val batch_size

    output:
        path "folder_*" , emit: folders

    script:

    """
    file_list=(${files})

    count=0
    folder_num=1
    mkdir -p folder_1

    for file in \${file_list[@]}; do
        cp \$file "folder_\$folder_num/"
        
        count=\$((count+1))
        echo \$count 

        echo $batch_size
        
            
        if [ \$count -eq $batch_size ]; then
            echo "New folder created"
            folder_num=\$((folder_num+1))
            mkdir -p "folder_\$folder_num"
            count=0
        fi

        echo "aaa"
    done

    """

}
