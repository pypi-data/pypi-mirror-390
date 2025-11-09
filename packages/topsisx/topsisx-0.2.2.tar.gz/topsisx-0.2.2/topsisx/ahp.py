import numpy as np
import pandas as pd

def ahp(pairwise_matrix, verbose=False):
    """
    Compute AHP weights from a pairwise comparison matrix.
    Converts fractional strings like '1/3' to float.
    
    Parameters:
    - pairwise_matrix: DataFrame with pairwise comparisons (can contain strings like '1/3')
    - verbose: If True, print detailed calculation steps
    
    Returns:
    - numpy array of weights
    """
    # Convert fractional strings (like '1/3') to float - FIXED: use map() instead of applymap()
    matrix = pairwise_matrix.map(lambda x: eval(str(x)) if isinstance(x, str) else x).astype(float)

    n = matrix.shape[0]
    
    if verbose:
        print(f"\n📊 AHP Calculation:")
        print(f"   Matrix size: {n}x{n}")
        print("\n   Pairwise comparison matrix:")
        print(matrix)
    
    # Normalize by column sums
    col_sum = matrix.sum(axis=0)
    norm_matrix = matrix / col_sum
    
    if verbose:
        print("\n   Normalized matrix:")
        print(norm_matrix)
    
    # Calculate weights as row averages
    weights = norm_matrix.mean(axis=1).values
    
    if verbose:
        print("\n   ⚖️  Calculated weights:")
        for i, w in enumerate(weights):
            print(f"      Criterion {i+1}: {w:.4f} ({w*100:.2f}%)")
        
        # Calculate consistency ratio
        lambda_max = np.sum(col_sum * weights)
        ci = (lambda_max - n) / (n - 1)
        ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_values.get(n, 1.49)
        cr = ci / ri if ri > 0 else 0
        
        print(f"\n   📐 Consistency Check:")
        print(f"      Consistency Ratio (CR): {cr:.4f}")
        if cr < 0.1:
            print(f"      ✅ Acceptable (CR < 0.1)")
        else:
            print(f"      ⚠️  Warning: CR >= 0.1, review comparisons")
    
    return weights