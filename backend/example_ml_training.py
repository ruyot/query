"""
Example: Training a simple ranking model using the prepared data.

This example demonstrates how to use the JSONL output from prepare_ranking_data.py
to train a machine learning model for ranking predictions.

Requirements:
    pip install pandas scikit-learn numpy
"""
import json
import sys
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
except ImportError:
    print("Error: This example requires pandas, scikit-learn, and numpy.")
    print("Install with: pip install pandas scikit-learn numpy")
    sys.exit(1)


def load_jsonl(file_path: str) -> pd.DataFrame:
    """Load JSONL file into a pandas DataFrame."""
    print(f"Loading data from {file_path}...")
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} documents")
    return df


def prepare_features(df: pd.DataFrame) -> tuple:
    """
    Prepare features and target variable for training.
    
    This is a simple example. In production, you'd want to:
    - Engineer more features (query length, content quality, etc.)
    - Handle categorical variables properly
    - Normalize/scale features
    - Handle missing values
    """
    print("\nPreparing features...")
    
    # For this example, we'll use simple features
    # In practice, you'd add more: query features, content features, etc.
    
    # Feature engineering
    df['rank_inverse'] = 1.0 / df['rank']
    df['rank_log'] = np.log1p(df['rank'])
    df['has_description'] = df['description'].notna().astype(int)
    df['title_length'] = df['title'].str.len()
    df['category_is_video'] = (df['category'] == 'video').astype(int)
    
    # Select features
    feature_columns = [
        'rank',
        'rank_inverse',
        'rank_log',
        'recency_score',
        'has_description',
        'title_length',
        'category_is_video',
        'user_engagement_score'
    ]
    
    X = df[feature_columns]
    y = df['relevance_score']
    
    print(f"Features: {feature_columns}")
    print(f"Target: relevance_score")
    
    return X, y, feature_columns


def train_models(X_train, X_test, y_train, y_test, feature_names):
    """Train multiple models and compare performance."""
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    
    print("\n" + "=" * 70)
    print("Training Models")
    print("=" * 70)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Evaluate
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)
        test_r2 = r2_score(y_test, y_pred_test)
        
        results[name] = {
            'model': model,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'test_r2': test_r2
        }
        
        print(f"  Train RMSE: {train_rmse:.6f}")
        print(f"  Test RMSE:  {test_rmse:.6f}")
        print(f"  Test MAE:   {test_mae:.6f}")
        print(f"  Test R²:    {test_r2:.6f}")
        
        # Feature importance (if available)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            print(f"\n  Top 3 important features:")
            indices = np.argsort(importances)[::-1][:3]
            for i, idx in enumerate(indices, 1):
                print(f"    {i}. {feature_names[idx]}: {importances[idx]:.4f}")
    
    return results


def display_results(results):
    """Display comparison of model results."""
    print("\n" + "=" * 70)
    print("Model Comparison")
    print("=" * 70)
    
    print(f"\n{'Model':<25} {'RMSE':<12} {'MAE':<12} {'R²':<12}")
    print("-" * 70)
    
    for name, metrics in results.items():
        print(f"{name:<25} {metrics['test_rmse']:<12.6f} {metrics['test_mae']:<12.6f} {metrics['test_r2']:<12.6f}")
    
    # Find best model
    best_model_name = min(results.keys(), key=lambda k: results[k]['test_rmse'])
    print(f"\n✨ Best model: {best_model_name}")


def demonstrate_predictions(model, X_test, y_test, df_test):
    """Show some example predictions."""
    print("\n" + "=" * 70)
    print("Example Predictions")
    print("=" * 70)
    
    # Make predictions
    predictions = model.predict(X_test)
    
    # Show first 5 examples
    print(f"\n{'Rank':<8} {'Title':<40} {'Actual':<12} {'Predicted':<12} {'Error':<12}")
    print("-" * 90)
    
    for i in range(min(5, len(X_test))):
        idx = df_test.index[i]
        rank = df_test.loc[idx, 'rank']
        title = df_test.loc[idx, 'title'][:38]
        actual = y_test.iloc[i]
        pred = predictions[i]
        error = abs(actual - pred)
        
        print(f"{rank:<8} {title:<40} {actual:<12.6f} {pred:<12.6f} {error:<12.6f}")


def main():
    """Main execution flow."""
    print("=" * 70)
    print("  Ranking Model Training Example")
    print("=" * 70)
    
    # Check if data file exists
    data_file = 'output/ranking_training_data.jsonl'
    if not Path(data_file).exists():
        print(f"\nError: {data_file} not found!")
        print("Please run prepare_ranking_data.py first to generate the training data.")
        print("The file will be created in the 'output' folder.")
        sys.exit(1)
    
    # Load data
    df = load_jsonl(data_file)
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    
    # Split data
    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Train models
    results = train_models(X_train, X_test, y_train, y_test, feature_names)
    
    # Display comparison
    display_results(results)
    
    # Show example predictions with best model
    best_model_name = min(results.keys(), key=lambda k: results[k]['test_rmse'])
    best_model = results[best_model_name]['model']
    
    # Get test data with original DataFrame info
    test_indices = y_test.index
    df_test = df.loc[test_indices].reset_index(drop=True)
    X_test_reset = X_test.reset_index(drop=True)
    y_test_reset = y_test.reset_index(drop=True)
    
    demonstrate_predictions(best_model, X_test_reset, y_test_reset, df_test)
    
    print("\n" + "=" * 70)
    print("  Training Complete!")
    print("=" * 70)
    
    print("\n💡 Next Steps:")
    print("  1. Add more features (query features, content analysis, etc.)")
    print("  2. Tune hyperparameters for better performance")
    print("  3. Try deep learning models (neural networks)")
    print("  4. Implement cross-validation")
    print("  5. Deploy the model for real-time ranking")
    print()


if __name__ == "__main__":
    main()

