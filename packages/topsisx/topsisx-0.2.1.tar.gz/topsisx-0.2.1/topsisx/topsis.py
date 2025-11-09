import numpy as np
import pandas as pd

def topsis(data, weights, impacts):
    """
    Perform TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).

    Parameters:
    - data: Pandas DataFrame or 2D list/array with numerical criteria values.
    - weights: List of criteria weights (should sum to 1 or will be normalized).
    - impacts: List of '+' (benefit) or '-' (cost) for each criterion.

    Returns:
    - DataFrame with scores and ranks.
    """

    # Convert to DataFrame if needed
    if isinstance(data, (list, np.ndarray)):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a DataFrame, list, or NumPy array.")

    # Make a copy to avoid modifying original
    df = data.copy()
    
    # Validate weights
    weights = np.array(weights, dtype=float)
    if len(weights) != df.shape[1]:
        raise ValueError(f"Number of weights ({len(weights)}) must match number of criteria ({df.shape[1]}).")
    if weights.sum() != 1:
        weights = weights / weights.sum()

    # Validate impacts
    if len(impacts) != df.shape[1]:
        raise ValueError(f"Number of impacts ({len(impacts)}) must match number of criteria ({df.shape[1]}).")
    if not all(i in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be '+' or '-' only.")

    # Convert to numpy for calculations
    matrix = df.values.astype(float)
    
    # Step 1: Normalize data (vector normalization)
    norm_matrix = matrix / np.sqrt((matrix ** 2).sum(axis=0))

    # Step 2: Apply weights
    weighted_matrix = norm_matrix * weights

    # Step 3: Determine ideal best and ideal worst
    ideal_best = np.zeros(df.shape[1])
    ideal_worst = np.zeros(df.shape[1])
    
    for i in range(df.shape[1]):
        if impacts[i] == '+':
            ideal_best[i] = weighted_matrix[:, i].max()
            ideal_worst[i] = weighted_matrix[:, i].min()
        else:
            ideal_best[i] = weighted_matrix[:, i].min()
            ideal_worst[i] = weighted_matrix[:, i].max()

    # Step 4: Calculate Euclidean distances
    dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))

    # Step 5: Calculate similarity scores
    scores = dist_worst / (dist_best + dist_worst + 1e-10)  # Add small value to avoid division by zero

    # Step 6: Create result dataframe
    result = df.copy()
    result['Topsis_Score'] = scores
    
    # FIXED: Convert scores to pandas Series before using .rank()
    scores_series = pd.Series(scores)
    result['Rank'] = scores_series.rank(ascending=False, method='min').astype(int)

    return result.sort_values(by='Rank').reset_index(drop=True)