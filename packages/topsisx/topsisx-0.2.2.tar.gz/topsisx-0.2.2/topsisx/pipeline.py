import pandas as pd
from topsisx.ahp import ahp
from topsisx.entropy import entropy_weights
from topsisx.topsis import topsis
from topsisx.vikor import vikor

class DecisionPipeline:
    def __init__(self, weights="entropy", method="topsis", verbose=False):
        """
        Initialize DecisionPipeline
        
        Parameters:
        - weights: 'entropy', 'ahp', or 'equal'
        - method: 'topsis' or 'vikor'
        - verbose: Show detailed logs (default: False)
        """
        self.weights_method = weights.lower()
        self.ranking_method = method.lower()
        self.verbose = verbose

    def compute_weights(self, df: pd.DataFrame, pairwise_matrix=None):
        """
        Compute weights based on selected method
        """
        if self.weights_method == "ahp":
            if pairwise_matrix is None:
                raise ValueError("AHP weighting requires a pairwise comparison matrix")
            return ahp(pairwise_matrix, verbose=self.verbose)
        elif self.weights_method == "entropy":
            weights = entropy_weights(df.values)
            if self.verbose:
                print(f"📊 Entropy weights calculated: {weights}")
            return weights
        elif self.weights_method == "equal":
            weights = [1 / df.shape[1]] * df.shape[1]
            if self.verbose:
                print(f"⚖️  Equal weights: {weights}")
            return weights
        else:
            raise ValueError(f"Unsupported weight method: {self.weights_method}")

    def run(self, df: pd.DataFrame, impacts=None, pairwise_matrix=None, **kwargs):
        """
        Run the decision analysis pipeline
        
        Parameters:
        - df: DataFrame with numeric criteria columns ONLY
        - impacts: List of '+' or '-' for each criterion
        - pairwise_matrix: DataFrame for AHP pairwise comparisons (if using AHP)
        - **kwargs: Additional parameters (e.g., v for VIKOR)
        
        Returns:
        - DataFrame with rankings and scores
        """
        if impacts is None:
            raise ValueError("Impacts must be specified")
        
        # Validate impacts
        if len(impacts) != df.shape[1]:
            raise ValueError(
                f"Number of impacts ({len(impacts)}) must match number of criteria ({df.shape[1]}). "
                f"Criteria columns: {', '.join(df.columns.tolist())}"
            )
        
        if not all(i in ['+', '-'] for i in impacts):
            raise ValueError("Impacts must be '+' or '-' only")
        
        if self.verbose:
            print(f"\n🎯 Starting {self.ranking_method.upper()} analysis with {self.weights_method} weights")
            print(f"📊 Data shape: {df.shape}")
            print(f"📋 Criteria: {', '.join(df.columns.tolist())}")
            print(f"⚖️  Impacts: {impacts}")
        
        # Compute weights
        weights = self.compute_weights(df, pairwise_matrix)
        
        if self.verbose:
            print(f"⚖️  Weights: {weights}")
        
        # Run selected method
        if self.ranking_method == "topsis":
            result = topsis(df, weights, impacts)
        elif self.ranking_method == "vikor":
            v = kwargs.get('v', 0.5)
            if self.verbose:
                print(f"📊 VIKOR v parameter: {v}")
            result = vikor(df, weights, impacts, v=v)
        elif self.ranking_method == "ahp":
            # For AHP ranking, we need pairwise matrix
            if pairwise_matrix is None:
                raise ValueError("AHP ranking requires a pairwise comparison matrix")
            result = ahp(pairwise_matrix, verbose=self.verbose)
        else:
            raise ValueError(f"Unsupported ranking method: {self.ranking_method}")
        
        if self.verbose:
            print(f"✅ Analysis complete!")
        
        return result
    
    def compare_methods(self, df: pd.DataFrame, impacts=None, pairwise_matrix=None):
        """
        Compare TOPSIS and VIKOR results
        
        Parameters:
        - df: DataFrame with numeric criteria columns
        - impacts: List of '+' or '-' for each criterion
        - pairwise_matrix: DataFrame for AHP pairwise comparisons (if using AHP)
        
        Returns:
        - Dictionary with topsis, vikor, and comparison results
        """
        weights = self.compute_weights(df, pairwise_matrix)
        
        # Run both methods
        topsis_result = topsis(df, weights, impacts)
        vikor_result = vikor(df, weights, impacts, v=0.5)
        
        # Create comparison
        comparison = pd.DataFrame({
            'Alternative': range(1, len(df) + 1),
            'TOPSIS_Rank': topsis_result['Rank'],
            'VIKOR_Rank': vikor_result['Rank'],
            'Rank_Difference': abs(topsis_result['Rank'] - vikor_result['Rank'])
        })
        
        return {
            'topsis': topsis_result,
            'vikor': vikor_result,
            'comparison': comparison
        }