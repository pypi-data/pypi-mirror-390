import numpy as np
import pandas as pd

def vikor(data, weights, impacts, v=0.5):
    """
    VIKOR ranking method for multi-criteria decision-making.
    
    Parameters:
    - data: DataFrame or numpy array with criteria values
    - weights: Array of criteria weights
    - impacts: List of '+' (benefit) or '-' (cost) for each criterion
    - v: Strategy weight (0-1), default 0.5
         v=0 focuses on maximum group utility (consensus)
         v=1 focuses on minimum individual regret
    
    Returns:
    - DataFrame with S, R, Q scores and ranks (in ORIGINAL row order)
    
    Notes:
    - Lower Q values indicate better alternatives
    - S represents group utility
    - R represents individual regret
    - Results maintain the original input row order
    """
    # Convert to DataFrame if needed
    if isinstance(data, (list, np.ndarray)):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a DataFrame, list, or NumPy array.")
    
    # Make a copy to avoid modifying original
    df = data.copy()
    
    # Validate inputs
    matrix = df.values.astype(float)
    weights = np.array(weights, dtype=float)
    
    if len(weights) != matrix.shape[1]:
        raise ValueError(f"Number of weights ({len(weights)}) must match number of criteria ({matrix.shape[1]}).")
    
    if len(impacts) != matrix.shape[1]:
        raise ValueError(f"Number of impacts ({len(impacts)}) must match number of criteria ({matrix.shape[1]}).")
    
    if not all(i in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be '+' or '-' only.")
    
    # Normalize weights if needed
    if abs(weights.sum() - 1.0) > 1e-6:
        weights = weights / weights.sum()
    
    # Calculate ideal and anti-ideal for each criterion
    ideal = np.zeros(matrix.shape[1])
    anti_ideal = np.zeros(matrix.shape[1])
    
    for j in range(matrix.shape[1]):
        if impacts[j] == '+':
            # Benefit criterion: higher is better
            ideal[j] = np.max(matrix[:, j])
            anti_ideal[j] = np.min(matrix[:, j])
        else:
            # Cost criterion: lower is better
            ideal[j] = np.min(matrix[:, j])
            anti_ideal[j] = np.max(matrix[:, j])
    
    # Calculate S (group utility) and R (individual regret)
    S = np.zeros(matrix.shape[0])
    R = np.zeros(matrix.shape[0])
    
    for i in range(matrix.shape[0]):
        # Calculate weighted normalized distances for each alternative
        weighted_distances = weights * (ideal - matrix[i, :]) / (ideal - anti_ideal + 1e-10)
        S[i] = np.sum(weighted_distances)  # Sum for group utility
        R[i] = np.max(weighted_distances)  # Max for individual regret
    
    # Calculate Q values using the strategy weight v
    S_star = np.min(S)   # Best group utility
    S_minus = np.max(S)  # Worst group utility
    R_star = np.min(R)   # Best individual regret
    R_minus = np.max(R)  # Worst individual regret
    
    # VIKOR Q formula: compromise between S and R
    Q = v * (S - S_star) / (S_minus - S_star + 1e-10) + \
        (1 - v) * (R - R_star) / (R_minus - R_star + 1e-10)
    
    # Create result dataframe with original data
    result = df.copy()
    result['S'] = S
    result['R'] = R
    result['Q'] = Q
    
    # Rank by Q (lower Q is better)
    Q_series = pd.Series(Q)
    result['Rank'] = Q_series.rank(ascending=True, method='min').astype(int)
    
    # Return in ORIGINAL order (no sorting)
    return result