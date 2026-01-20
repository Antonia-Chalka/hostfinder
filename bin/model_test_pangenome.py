import pandas as pd
import pickle
import argparse
import os
import glob
import json


def main():
    parser = argparse.ArgumentParser(description='Run predictions for multiple models with different thresholds')
    parser.add_argument('--input_data', required=True, help='Path to input csv file')
    parser.add_argument('--model_dir', required=True, help='Directory containing pkl model files')
    parser.add_argument('--threshold_config', help='JSON file with model-specific thresholds (optional)')
    args = parser.parse_args()
    
    # Read input data
    test_data = pd.read_csv(args.input_data, delimiter=',')

    gene_col = 'Gene' if 'Gene' in test_data.columns else '#GeneId'
    melted_data = test_data.melt(id_vars=[gene_col], var_name='assemblies', value_name='value')
    trans = melted_data.pivot(index='assemblies', columns=gene_col, values='value')
    # Convert to binary: present (any non-empty value) = 1, absent (NaN) = 0
    trans_reduced = trans.notna().astype(int)

    # Load threshold configuration if provided
    thresholds = {}
    if args.threshold_config:
        with open(args.threshold_config, 'r') as f:
            thresholds = json.load(f)

    # Find all pkl model files in the directory
    model_files = glob.glob(os.path.join(args.model_dir, "*.pkl"))
    
    if not model_files:
        print(f"No .pkl files found in {args.model_dir}")
        return
    
    print(f"Found {len(model_files)} model files")

    all_assemblies = trans_reduced.index
    combined_results = pd.DataFrame(index=all_assemblies)

    for model_file in model_files:
        print(f"Processing model: {model_file}")
        
        # Load model
        with open(model_file, 'rb') as file:
            model = pickle.load(file)
        
        # Extract host name from model filename (without extension)
        host_name = os.path.splitext(os.path.basename(model_file))[0]
        
        # Get threshold for this model (try different possible keys)
        threshold = thresholds[host_name]

        print(f"Using threshold {threshold} for {host_name}")
        
        # Reindex data to match model features (missing features filled with 0 = absent)
        X = trans_reduced.reindex(columns=model.feature_names_in_, fill_value=0)
        
        # Make predictions
        test_pred_proba = model.predict_proba(X)
        
        # Add columns to combined results
        combined_results[f"{host_name}_prediction"] = test_pred_proba[:,1] >= threshold
        combined_results[f"{host_name}_confidence_score"] = test_pred_proba[:,1]
        combined_results[f"{host_name}_threshold_used"] = threshold
        
    # Reset index to make assemblies a column
    combined_results = combined_results.reset_index()
    combined_results = combined_results.rename(columns={'index': 'Assembly'})

    # Save combined results
    combined_results.to_csv("pangenome_predictions.tsv", sep='\t', index=False)

if __name__ == "__main__":
    main()
