import networkx as nx
import pandas as pd
import csv
import argparse
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_file_exists(filepath, description):
    if not os.path.exists(filepath):
        logging.error(f"{description} file not found: {filepath}")
        raise FileNotFoundError(f"{description} file not found: {filepath}")
    logging.info(f"{description} file found: {filepath}")

def main(args):
    logging.info("Starting gene matching script")
    
    # Check if reference files exist
    check_file_exists(args.gene_data_file_ref, "Reference gene data")
    check_file_exists(args.gml_file_ref, "Reference GML")
    check_file_exists(args.model_features_file, "Model features")

    check_file_exists(args.model_features_file, "Model features")
    check_file_exists(args.model_features_file, "Model features")
    check_file_exists(args.model_features_file, "Model features")
    

    
    # Reads the model_features_file and stores each line (gene feature) in the features list.
    logging.info("Reading model features file")

    with open(args.model_features_file, 'r') as file:
        features = {line.strip() for line in file}

    logging.info(f"Loaded {len(features)} features")
    
    # Read reference GML file for gene names and ids
    logging.info("Reading reference GML file")

    graph = nx.read_gml(args.gml_file_ref)
    ref_gene_id_name_dict = {}

    for node, data in graph.nodes(data=True):
        # Iterate & Extract the name and geneID from the node attributes
        name = data.get('name', '')
        gene_ids = data.get('geneIDs', '').split(';')
        for gene_id in gene_ids:
            if name in features:
                ref_gene_id_name_dict[gene_id] = name

    logging.info(f"Extracted {len(ref_gene_id_name_dict)} gene ID mappings from reference GML")
    
    all_results = []
    for test_dir in args.test_dirs:
        logging.info(f"Processing test directory: {test_dir}")

        assembly_name = os.path.basename(test_dir)
        gene_data_file_test = os.path.join(test_dir, "gene_data.csv")
        gml_file_test = os.path.join(test_dir, "final_graph.gml")
        presence_absence_file_test = os.path.join(test_dir, "gene_presence_absence.csv")
        
        check_file_exists(gene_data_file_test, "Test gene data")
        check_file_exists(gml_file_test, "Test GML")
        check_file_exists(presence_absence_file_test, "Presence absence")
        
        # Read test GML file for gene names and ids
        logging.info("Reading test GML file")

        graph = nx.read_gml(gml_file_test)
        test_gene_id_name_dict = {}

        for node, data in graph.nodes(data=True):
            name = data.get('name', '')
            gene_ids = data.get('geneIDs', '').split(';')
            for gene_id in gene_ids: # Write each geneID with its corresponding name
                test_gene_id_name_dict[gene_id] = name  

        logging.info(f"Extracted {len(test_gene_id_name_dict)} gene ID mappings from test GML")
        
        # Matching Gene Cluster Names
        gene_id_map = {}
        
        logging.info("Matching gene IDs between reference and test gene data files")
        # Open the 2 gene_data files, clustering_id is the geneID
        with open(args.gene_data_file_ref, 'r') as f1, open(gene_data_file_test, 'r') as f2:
            reader1 = csv.DictReader(f1)
            reader2 = csv.DictReader(f2)
            gene_data_ref = {}
            
            for row1 in reader1:
                # Check if clustering_id matches any geneID from the geneID_name_output.csv file
                if row1['clustering_id'].strip() in ref_gene_id_name_dict:
                    key = (row1['scaffold_name'], row1['annotation_id'], row1['prot_sequence'])
                    gene_data_ref[key] = row1['clustering_id'] # old gene ID
            
            for row in reader2:
                key = (row['scaffold_name'], row['annotation_id'], row['prot_sequence'])
                if key in gene_data_ref: # If key matches, write both geneIDs to the output file
                    gene_id_map[row['clustering_id']] = gene_data_ref[key] # new -> old gene ID

        logging.info(f"Matched {len(gene_id_map)} gene IDs")
        
        refnames_testnames = set() # Initialize a set to store *unique* matched gene cluster names
        
        for test_geneid, ref_geneid in gene_id_map.items():
            ref_name = ref_gene_id_name_dict.get(ref_geneid)
            test_name = test_gene_id_name_dict.get(test_geneid)

            # If the gene cluster for a gene id is not found, throw an error and stop execution
            if not ref_name:
                raise ValueError(f'Reference name not found for ref gene ID: {ref_geneid}')
            if not test_name:
                raise ValueError(f'Reference name not found for test gene ID: {test_name}')
            
            refnames_testnames.add((ref_name, test_name))
        logging.info(f"Found {len(refnames_testnames)} matched gene clusters")
        
        # Writing the dictionary to a CSV file
        output_dir = os.path.join(args.out_dir, assembly_name)
        os.makedirs(output_dir, exist_ok=True)  # Ensure the subdirectory exists

        matched_gene_clusters_file = os.path.join(output_dir, f"{assembly_name}_matched_gene_clusters.csv")
        with open(matched_gene_clusters_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Ref_Name', 'Test_Name'])
            for match in refnames_testnames:
                writer.writerow(match)
        
        logging.info("Processing presence-absence file")
        # Rewrite the gene_presence_absence file and replace the Gene column values with the matched names
        result_df = pd.DataFrame()
        refnames_testnames_dict = {ref_name: test_name for ref_name, test_name in refnames_testnames}
        for chunk in pd.read_csv(presence_absence_file_test, chunksize=100000):
            chunk = chunk[['Gene', 'x']] 
            for index, row in chunk.iterrows():
                matched_rows = []
                test_name = row['Gene']
                # Find all ref_names that map to this test_name
                ref_names = [ref_name for ref_name, tn in refnames_testnames_dict.items() if tn == test_name] 
                if ref_names:
                    for ref_name in ref_names:
                        new_row = row.copy()
                        new_row['Gene'] = ref_name
                        matched_rows.append(new_row)
                    
                    result_df = pd.concat([result_df, pd.DataFrame(matched_rows)], ignore_index=True)
        
        result_df = result_df.rename(columns={'x': assembly_name})
        all_results.append(result_df) 
        result_df.to_csv(os.path.join(output_dir, f"{assembly_name}_gene_presence_absence_matched.csv"), index=False)
    
    logging.info("Collating binary presence-absence files")
    binary_df = pd.concat(all_results, ignore_index=True) 
    binary_df[assembly_name] = binary_df[assembly_name].fillna('').astype(str)
    binary_df[assembly_name] = (binary_df[assembly_name] != '').astype(int)
    binary_df.to_csv(os.path.join(args.out_dir, "3.gene_presence_binary.csv"), index=False)

    logging.info(f"Binary gene presence-absence file written to {args.out_dir}")
    
    logging.info("Script completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gene matching script for Panaroo data")
    parser.add_argument('--gene_data_file_ref', required=True, help="Path to the reference gene data file")
    parser.add_argument('--gml_file_ref', required=True, help="Path to the reference GML file")
    parser.add_argument('--model_features_file', required=True, help="Path to the model features file")
    parser.add_argument('--test_dirs', nargs='+', required=True, help="Paths to test directories. Must contain gene_data.csv, final_graph.gml and a presence_absence.csv file")
    parser.add_argument('--out_dir', required=True, help="Output directory for result files")
    
    args = parser.parse_args()
    main(args)