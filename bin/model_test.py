import pandas as pd
import pickle
import argparse

# TODO Potentially remove?
def preprocess_data(df):
    melted_data = df.melt(id_vars=['Gene' if 'Gene' in df.columns else '#GeneId'], var_name='assemblies', value_name='value')
    trans = melted_data.pivot(index='assemblies', columns='Gene' if 'Gene' in df.columns else '#GeneId', values='value')
    trans.reset_index(inplace=True)
    trans.index.name = None
    nunique = trans.nunique()
    cols_to_drop = nunique[nunique == 1].index
    trans_reduced = trans.drop(cols_to_drop, axis=1)
    trans_reduced = trans_reduced.fillna(0)
    return trans_reduced

def main():
    parser = argparse.ArgumentParser(description='Run model predictions on gene presence/absence data')
    parser.add_argument('--model-file', required=True, help='Path to the trained model file (pickle format)')
    parser.add_argument('--input-data', required=True, help='Path to the input gene presence/absence data (csv format)')
    parser.add_argument('--host', required=True, help='Host name for labeling predictions')
    parser.add_argument('--threshold', type=float, default=0.5, help='Threshold for binary classification (default: 0.5)')
    parser.add_argument('--output-file', default='test_predictions_by_assembly.tsv', help='Output file path (default: test_predictions_by_assembly.tsv)')
    parser.add_argument('--index-column', default='assemblies', help='Column name to use as index after preprocessing (default: assemblies)')

    args = parser.parse_args()

    # Load model file
    with open(args.model_file, 'rb') as file:
        model = pickle.load(file)
    
    # Load and preprocess data
    test_data = pd.read_csv(args.input_data, delimiter='\t') #TODO maybe change delimiter
    test_data = preprocess_data(test_data)
    test_data.set_index(args.index_column, drop=True, inplace=True)
    
    # Prepare features
    X = test_data[model.feature_names_in_]

    # Predictions
    test_pred_proba = model.predict_proba(X)

    # Build results dataframe
    results = pd.DataFrame({
        'Assembly': X.index,
        f"{args.host}_prediction": test_pred_proba[:,1] >= args.threshold,
        f"{args.host}_confidence_score": test_pred_proba[:,1]
    })

    # Save results
    results.to_csv(args.output_file, sep='\t', index=False)

if __name__ == "__main__":
    main()
