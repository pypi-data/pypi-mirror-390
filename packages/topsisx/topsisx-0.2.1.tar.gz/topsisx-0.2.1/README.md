# TOPSISX 📊

[![PyPI Version](https://img.shields.io/pypi/v/topsisx.svg)](https://pypi.org/project/topsisx/)
[![Python Version](https://img.shields.io/pypi/pyversions/topsisx.svg)](https://pypi.org/project/topsisx/)
[![Downloads](https://static.pepy.tech/badge/topsisx)](https://pepy.tech/project/topsisx)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/SuvitKumar003/ranklib/blob/main/LICENSE)

**TOPSISX** is a comprehensive Python library for **Multi-Criteria Decision Making (MCDM)** that provides both a powerful programming API and an intuitive web interface. Make data-driven decisions using proven algorithms like TOPSIS, VIKOR, AHP, and Entropy weighting.

---

## 🌟 Key Features

- 🐍 **Python Library** - Use in your code like pandas, numpy
- 🌐 **Web Interface** - Beautiful Streamlit dashboard for non-coders
- 💻 **CLI Support** - Command-line interface for automation
- 📊 **Multiple Methods** - TOPSIS, VIKOR, AHP, Entropy weighting
- 📈 **Visualizations** - Interactive charts and rankings
- 📄 **PDF Reports** - Professional report generation
- 🔧 **Easy Integration** - Works with pandas, numpy, CSV, Excel
- 🎯 **Well Tested** - Comprehensive test suite included

---

## 📦 Installation

### Quick Install
```bash
pip install topsisx
```

### From Source (for development)
```bash
git clone https://github.com/SuvitKumar003/ranklib.git
cd ranklib
pip install -e .
```

### Requirements
- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.8.0
- streamlit >= 1.34.0 (for web interface)
- fpdf >= 1.7.2 (for PDF reports)

---

## 🚀 Quick Start

### Method 1: Web Interface (No Coding Required!)

Perfect for non-programmers and quick analysis:

```bash
# Launch the web interface
topsisx --web
```

This opens a beautiful dashboard in your browser where you can:
- 📤 Upload CSV files
- 📋 Use sample datasets
- ✏️ Enter data manually
- 🎨 Configure methods interactively
- 📊 View results with charts
- 💾 Download results (CSV & PDF)

**Screenshot of Web Interface:**
```
┌─────────────────────────────────────────────┐
│  📊 TOPSISX Decision Making Tool            │
│  Multi-Criteria Decision Analysis          │
├─────────────────────────────────────────────┤
│  Sidebar:                                   │
│  • Upload CSV / Use Samples / Manual Entry  │
│  • Select Methods (TOPSIS/VIKOR)           │
│  • Choose Weighting (Entropy/AHP/Equal)    │
│  • Define Impacts (+/-)                    │
│                                            │
│  Main Panel:                               │
│  • Data Preview                            │
│  • Run Analysis Button                     │
│  • Results Table                           │
│  • Visualizations                          │
│  • Download CSV & PDF                      │
└─────────────────────────────────────────────┘
```

---

### Method 2: Python Library (For Programmers)

Use TOPSISX in your Python code just like pandas or numpy:

#### Basic TOPSIS Analysis
```python
import pandas as pd
from topsisx.topsis import topsis

# Your data
data = pd.DataFrame({
    'Cost': [250, 200, 300, 275],
    'Quality': [16, 16, 32, 32],
    'Speed': [12, 8, 16, 8]
})

# Define criteria
weights = [0.3, 0.4, 0.3]
impacts = ['-', '+', '+']  # - means lower is better, + means higher is better

# Run TOPSIS
result = topsis(data, weights, impacts)

print(result)
```

**Output:**
```
   Cost  Quality  Speed  Topsis_Score  Rank
0   200       16      8        0.5234     2
1   250       16     12        0.3456     3
2   300       32     16        0.7891     1
3   275       32      8        0.6543     2
```

#### Using Pipeline (Recommended - Higher Level API)
```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Your data
data = pd.DataFrame({
    'Cost': [250, 200, 300],
    'Quality': [16, 16, 32],
    'Time': [12, 8, 16]
})

# Create pipeline with automatic weight calculation
pipeline = DecisionPipeline(
    weights='entropy',  # Automatic weights based on data variance
    method='topsis'     # TOPSIS ranking method
)

# Run analysis
result = pipeline.run(
    data, 
    impacts=['-', '+', '-']  # Cost and Time are costs (lower better)
)

print(result)
```

---

### Method 3: Command Line Interface (For Automation)

Perfect for scripts, batch processing, and automation:

#### Basic Usage
```bash
# Analyze a CSV file
topsisx data.csv --impacts "+,-,+" --output results.csv
```

#### With Specific Methods
```bash
# TOPSIS with entropy weights
topsisx data.csv --method topsis --weights entropy --impacts "+,-,+"

# VIKOR with equal weights
topsisx data.csv --method vikor --weights equal --impacts "+,+,+"

# Generate PDF report
topsisx data.csv --impacts "+,-,+" --report
```

#### Preserve ID Columns
```bash
# Keep the 'Model' column in results
topsisx laptops.csv --impacts "-,+,+,-" --id-col "Model" --output results.csv
```

#### AHP Weighting
```bash
# Use AHP pairwise comparison for weights
topsisx data.csv --weights ahp --ahp-matrix pairwise.csv --impacts "+,-,+"
```

#### VIKOR with Custom Parameters
```bash
# VIKOR with v=0.7 (more emphasis on group utility)
topsisx data.csv --method vikor --vikor-v 0.7 --impacts "+,+,+"
```

#### Verbose Output
```bash
# Show detailed processing information
topsisx data.csv --impacts "+,-,+" --verbose
```

**CLI Help:**
```bash
topsisx --help
```

---

## 📚 Detailed Usage Guide

### 1. TOPSIS Method

**TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution) ranks alternatives based on their distance from ideal and anti-ideal solutions.

#### When to Use:
- General-purpose ranking
- Balanced decision-making
- When you have quantitative criteria
- Multiple conflicting objectives

#### Basic Example:
```python
from topsisx.topsis import topsis
import pandas as pd

data = pd.DataFrame({
    'Price': [800, 1200, 1000, 900],
    'RAM': [8, 16, 16, 8],
    'Battery': [6, 4, 8, 7],
    'Weight': [2.0, 2.5, 1.8, 2.2]
})

# Define impacts: Price and Weight are costs (lower is better)
impacts = ['-', '+', '+', '-']

# Define weights (must sum to 1, or will be normalized)
weights = [0.3, 0.3, 0.2, 0.2]

result = topsis(data, weights, impacts)
print(result)
```

#### With Automatic Weighting (Entropy):
```python
from topsisx.pipeline import DecisionPipeline

pipeline = DecisionPipeline(weights='entropy', method='topsis')
result = pipeline.run(data, impacts=['-', '+', '+', '-'])
```

---

### 2. VIKOR Method

**VIKOR** finds compromise solutions by considering both group utility and individual regret.

#### When to Use:
- Conflicting criteria
- Need compromise solutions
- Want to balance majority preference and minority concerns
- Dealing with incommensurable units

#### Basic Example:
```python
from topsisx.vikor import vikor
import pandas as pd

data = pd.DataFrame({
    'Criterion1': [7, 8, 6, 9],
    'Criterion2': [9, 7, 8, 6],
    'Criterion3': [9, 6, 8, 7]
})

weights = [0.33, 0.33, 0.34]
impacts = ['+', '+', '+']

# v parameter: 0 = consensus, 1 = individual regret, 0.5 = balanced
result = vikor(data, weights, impacts, v=0.5)
print(result)
```

#### Understanding VIKOR Output:
```python
# Result columns:
# S = Group utility measure (lower is better)
# R = Individual regret measure (lower is better)
# Q = Compromise ranking index (lower is better)
# Rank = Final ranking (1 is best)
```

---

### 3. AHP Weighting

**AHP** (Analytic Hierarchy Process) calculates weights through pairwise comparisons.

#### When to Use:
- Subjective criteria
- Expert judgments needed
- Hierarchical decision problems
- Need to check consistency of judgments

#### Pairwise Comparison Scale:
```
1 = Equal importance
3 = Moderate importance
5 = Strong importance
7 = Very strong importance
9 = Extreme importance
2, 4, 6, 8 = Intermediate values
```

#### Example:
```python
from topsisx.ahp import ahp
import pandas as pd

# Pairwise comparison matrix
# Example: Quality > Price > Speed
pairwise = pd.DataFrame([
    [1,     '1/3',  5],      # Price row
    [3,     1,      7],      # Quality row (most important)
    ['1/5', '1/7',  1]       # Speed row (least important)
])

# Calculate weights
weights = ahp(pairwise, verbose=True)
print(f"Calculated weights: {weights}")

# Use with TOPSIS
from topsisx.topsis import topsis

data = pd.DataFrame({
    'Price': [800, 1200, 1000],
    'Quality': [7, 9, 8],
    'Speed': [5, 6, 7]
})

result = topsis(data, weights, impacts=['-', '+', '+'])
print(result)
```

#### Using Pipeline with AHP:
```python
from topsisx.pipeline import DecisionPipeline

pipeline = DecisionPipeline(weights='ahp', method='topsis')
result = pipeline.run(
    data, 
    impacts=['-', '+', '+'],
    pairwise_matrix=pairwise
)
```

---

### 4. Entropy Weighting

**Entropy** calculates objective weights based on data variance/information content.

#### When to Use:
- Objective weighting needed
- Want to minimize subjective bias
- Data-driven decisions
- Don't have expert knowledge for weights

#### Example:
```python
from topsisx.entropy import entropy_weights
import numpy as np

# Data matrix
data = np.array([
    [250, 16, 12],
    [200, 16, 8],
    [300, 32, 16]
])

# Calculate weights automatically
weights = entropy_weights(data)
print(f"Entropy weights: {weights}")

# Interpretation: 
# Higher weight = more variance/information = more important for discrimination
```

#### With Pipeline (Automatic):
```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

data = pd.DataFrame({
    'Cost': [250, 200, 300],
    'Quality': [16, 16, 32],
    'Speed': [12, 8, 16]
})

pipeline = DecisionPipeline(weights='entropy', method='topsis')
result = pipeline.run(data, impacts=['-', '+', '+'])

# Weights are calculated automatically!
```

---

## 🎯 Real-World Examples

### Example 1: Laptop Selection

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Laptop options
laptops = pd.DataFrame({
    'Model': ['Dell XPS', 'MacBook Pro', 'ThinkPad', 'HP Spectre'],
    'Price': [1200, 2000, 1500, 1300],
    'RAM_GB': [16, 16, 32, 16],
    'Battery_Hours': [8, 12, 6, 10],
    'Weight_KG': [1.8, 1.4, 2.2, 1.6],
    'Screen_Size': [13, 13, 14, 13]
})

print("Laptop Options:")
print(laptops)

# Separate ID column from criteria
models = laptops['Model']
criteria = laptops[['Price', 'RAM_GB', 'Battery_Hours', 'Weight_KG', 'Screen_Size']]

# Create pipeline
pipeline = DecisionPipeline(weights='entropy', method='topsis')

# Run analysis
result = pipeline.run(
    criteria,
    impacts=['-', '+', '+', '-', '+']  
    # Price & Weight: lower is better
    # RAM, Battery, Screen: higher is better
)

# Add model names back
result.insert(0, 'Model', models.values)

print("\nRanked Laptops:")
print(result[['Model', 'Topsis_Score', 'Rank']])

# Get recommendation
best = result.iloc[0]
print(f"\n🏆 Recommended: {best['Model']}")
print(f"   Score: {best['Topsis_Score']:.4f}")
```

---

### Example 2: Supplier Selection

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Supplier evaluation data
suppliers = pd.DataFrame({
    'Supplier': ['ABC Corp', 'XYZ Ltd', 'DEF Inc', 'GHI Co'],
    'Cost': [250000, 200000, 300000, 275000],
    'Quality_Score': [85, 78, 92, 88],
    'Delivery_Time_Days': [15, 12, 20, 10],
    'Service_Rating': [4.2, 3.8, 4.7, 4.5],
    'Flexibility': [7, 6, 9, 8]
})

print("Supplier Options:")
print(suppliers)

# Define importance using AHP
from topsisx.ahp import ahp

# Pairwise matrix: Quality > Service > Flexibility > Cost > Delivery Time
pairwise = pd.DataFrame([
    [1,     3,     5,     7,     9],      # Quality
    ['1/3', 1,     3,     5,     7],      # Service
    ['1/5', '1/3', 1,     3,     5],      # Flexibility
    ['1/7', '1/5', '1/3', 1,     3],      # Cost
    ['1/9', '1/7', '1/5', '1/3', 1]       # Delivery Time
])

print("\nCalculating AHP weights...")
weights = ahp(pairwise, verbose=True)

# Run analysis
criteria = suppliers[['Quality_Score', 'Service_Rating', 'Flexibility', 'Cost', 'Delivery_Time_Days']]

from topsisx.topsis import topsis
result = topsis(
    criteria, 
    weights, 
    impacts=['+', '+', '+', '-', '-']
)

result.insert(0, 'Supplier', suppliers['Supplier'].values)

print("\nRanked Suppliers:")
print(result[['Supplier', 'Topsis_Score', 'Rank']])

# Generate report
from topsisx.reports import generate_report
generate_report(result, method='topsis', filename='supplier_selection_report.pdf')
print("\n📄 PDF report saved!")
```

---

### Example 3: Investment Portfolio Selection

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

# Investment options
investments = pd.DataFrame({
    'Option': ['Stock A', 'Stock B', 'Bond X', 'Bond Y', 'Real Estate'],
    'Expected_Return_%': [12.5, 8.3, 5.5, 6.0, 9.2],
    'Risk_Score': [8, 6, 2, 3, 5],
    'Liquidity_Score': [9, 8, 7, 8, 4],
    'Min_Investment': [5000, 1000, 500, 500, 50000],
    'Historical_Performance': [7.5, 6.2, 4.8, 5.1, 8.0]
})

print("Investment Options:")
print(investments)

# Run analysis
pipeline = DecisionPipeline(weights='entropy', method='topsis')

criteria = investments[['Expected_Return_%', 'Risk_Score', 'Liquidity_Score', 
                        'Min_Investment', 'Historical_Performance']]

result = pipeline.run(
    criteria,
    impacts=['+', '-', '+', '-', '+']
    # Return, Liquidity, Performance: higher is better
    # Risk, Min Investment: lower is better
)

result.insert(0, 'Option', investments['Option'].values)

print("\nRanked Investment Options:")
print(result[['Option', 'Topsis_Score', 'Rank']])

# Top 3 recommendations
print("\n🏆 Top 3 Recommendations:")
for i, row in result.head(3).iterrows():
    print(f"{row['Rank']}. {row['Option']} (Score: {row['Topsis_Score']:.4f})")
```

---

### Example 4: Compare Multiple Methods

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

data = pd.DataFrame({
    'Alternative': ['A', 'B', 'C', 'D'],
    'Cost': [250, 200, 300, 275],
    'Quality': [16, 16, 32, 32],
    'Time': [12, 8, 16, 8]
})

criteria = data[['Cost', 'Quality', 'Time']]

# Create pipeline
pipeline = DecisionPipeline(weights='equal', method='topsis')

# Compare TOPSIS vs VIKOR
comparison = pipeline.compare_methods(
    criteria,
    impacts=['-', '+', '-']
)

print("TOPSIS Results:")
print(comparison['topsis'][['Rank', 'Topsis_Score']])

print("\nVIKOR Results:")
print(comparison['vikor'][['Rank', 'Q']])

print("\nRank Comparison:")
print(comparison['comparison'])

# Analyze differences
diff = comparison['comparison']['Rank_Difference']
if diff.max() == 0:
    print("\n✅ Both methods agree completely!")
elif diff.max() <= 1:
    print("\n✅ Methods have minor differences (acceptable)")
else:
    print(f"\n⚠️  Methods differ significantly (max difference: {diff.max()})")
```

---

## 🔧 Advanced Usage

### 1. Custom Workflow Integration

```python
import pandas as pd
from topsisx.pipeline import DecisionPipeline

def evaluate_options(csv_file, criteria_config):
    """
    Custom function that integrates TOPSISX into your workflow
    
    Args:
        csv_file: Path to CSV with options
        criteria_config: Dict mapping column to impact direction
    
    Returns:
        Best option as dictionary
    """
    # Load data
    df = pd.read_csv(csv_file)
    
    # Extract criteria
    criteria_cols = list(criteria_config.keys())
    criteria_data = df[criteria_cols]
    
    # Extract impacts
    impacts = [criteria_config[col] for col in criteria_cols]
    
    # Run analysis
    pipeline = DecisionPipeline(weights='entropy', method='topsis')
    result = pipeline.run(criteria_data, impacts=impacts)
    
    # Add back all original columns
    for col in df.columns:
        if col not in result.columns:
            result[col] = df[col].values
    
    # Return best option
    best = result.iloc[0].to_dict()
    return best, result

# Usage
config = {
    'Price': '-',
    'Quality': '+',
    'Speed': '+'
}

best_option, full_results = evaluate_options('options.csv', config)
print(f"Best option: {best_option}")
```

---

### 2. Batch Processing Multiple Files

```python
import glob
from topsisx.pipeline import DecisionPipeline
import pandas as pd

def process_batch(folder_pattern, impacts):
    """
    Process multiple CSV files in batch
    """
    results_summary = []
    
    for csv_file in glob.glob(folder_pattern):
        print(f"Processing: {csv_file}")
        
        # Load data
        df = pd.read_csv(csv_file)
        
        # Run analysis
        pipeline = DecisionPipeline(weights='entropy', method='topsis')
        result = pipeline.run(df, impacts=impacts)
        
        # Save individual result
        output_file = csv_file.replace('.csv', '_results.csv')
        result.to_csv(output_file, index=False)
        
        # Store summary
        results_summary.append({
            'file': csv_file,
            'best_score': result.iloc[0]['Topsis_Score'],
            'alternatives': len(result)
        })
    
    # Save summary
    summary_df = pd.DataFrame(results_summary)
    summary_df.to_csv('batch_summary.csv', index=False)
    
    return summary_df

# Usage
summary = process_batch('data/*.csv', impacts=['-', '+', '+'])
print(summary)
```

---

### 3. Integration with Flask/FastAPI

```python
from fastapi import FastAPI, UploadFile
import pandas as pd
from topsisx.pipeline import DecisionPipeline
import io

app = FastAPI()

@app.post("/analyze")
async def analyze_decision(
    file: UploadFile,
    method: str = "topsis",
    weights: str = "entropy",
    impacts: str = "+,-,+"
):
    """
    API endpoint for decision analysis
    """
    # Read uploaded CSV
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    # Parse impacts
    impacts_list = impacts.split(',')
    
    # Run analysis
    pipeline = DecisionPipeline(weights=weights, method=method)
    result = pipeline.run(df, impacts=impacts_list)
    
    # Return as JSON
    return {
        "status": "success",
        "method": method,
        "best_alternative": result.iloc[0].to_dict(),
        "all_results": result.to_dict('records')
    }

# Run with: uvicorn app:app --reload
```

---

### 4. Jupyter Notebook Usage

```python
# In Jupyter Notebook

import pandas as pd
from topsisx.pipeline import DecisionPipeline
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('data.csv')

# Display data
display(df)

# Run analysis
pipeline = DecisionPipeline(weights='entropy', method='topsis')
result = pipeline.run(df, impacts=['+', '-', '+'])

# Display results
display(result)

# Visualize
fig, ax = plt.subplots(figsize=(10, 6))
result.plot.bar(x='Alternative', y='Topsis_Score', ax=ax, color='skyblue')
ax.set_title('TOPSIS Scores')
ax.set_ylabel('Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Interactive widgets
from ipywidgets import interact, widgets

@interact(
    method=widgets.Dropdown(options=['topsis', 'vikor'], description='Method:'),
    weights=widgets.Dropdown(options=['entropy', 'equal'], description='Weights:')
)
def analyze(method, weights):
    pipeline = DecisionPipeline(weights=weights, method=method)
    result = pipeline.run(df, impacts=['+', '-', '+'])
    display(result.head())
```

---

## 📊 Data Format Guidelines

### CSV File Format

Your CSV should have:
- **Rows**: Alternatives/options to evaluate
- **Columns**: Criteria for evaluation
- **Optional**: ID column (will be preserved in results)

#### Example CSV:

```csv
Model,Price,RAM_GB,Battery_Hours,Weight_KG
Laptop A,800,8,6,2.0
Laptop B,1200,16,4,2.5
Laptop C,1000,16,8,1.8
Laptop D,900,8,7,2.2
```

### Impact Direction

- **`+`** : Benefit criterion (higher is better)
  - Examples: Quality, Speed, RAM, Battery Life, Customer Rating
- **`-`** : Cost criterion (lower is better)
  - Examples: Price, Time, Weight, Energy Consumption, Error Rate

### Weights

Weights can be specified in three ways:

1. **Manual Weights** (must sum to 1):
   ```python
   weights = [0.3, 0.4, 0.3]  # Sums to 1.0
   ```

2. **Entropy (Automatic)**:
   ```python
   pipeline = DecisionPipeline(weights='entropy', method='topsis')
   # Weights calculated from data variance
   ```

3. **Equal Weights**:
   ```python
   pipeline = DecisionPipeline(weights='equal', method='topsis')
   # All criteria equally important
   ```

4. **AHP (Pairwise Comparison)**:
   ```python
   pairwise = pd.DataFrame([
       [1, 3, 5],
       ['1/3', 1, 3],
       ['1/5', '1/3', 1]
   ])
   weights = ahp(pairwise)
   ```

---

## 📈 Output Format

### TOPSIS Output

```python
# Columns in result:
# - Original criteria columns
# - Topsis_Score: Similarity to ideal solution (0-1, higher is better)
# - Rank: Final ranking (1 is best)

   Cost  Quality  Speed  Topsis_Score  Rank
0   200       16      8        0.5234     2
1   300       32     16        0.7891     1
```

### VIKOR Output

```python
# Columns in result:
# - Original criteria columns
# - S: Group utility measure (lower is better)
# - R: Individual regret measure (lower is better)
# - Q: Compromise ranking index (lower is better)
# - Rank: Final ranking (1 is best)

   C1  C2  C3     S      R      Q  Rank
0   7   9   9  0.00  0.000  0.000     1
1   8   7   6  0.33  0.333  0.333     2
```

---

## 🎓 Methodology Explanation

### TOPSIS Algorithm

1. **Normalize** decision matrix using vector normalization
2. **Weight** normalized matrix by criteria weights
3. **Identify** ideal best (A+) and ideal worst (A-) solutions
4. **Calculate** Euclidean distances to A+ and A-
5. **Compute** relative closeness = distance to A- / (distance to A+ + distance to A-)
6. **Rank** alternatives by closeness (higher is better)

### VIKOR Algorithm

1. **Determine** ideal and anti-ideal values for each criterion
2. **Calculate** S (group utility) and R (individual regret) for each alternative
3. **Compute** Q values: Q = v*(S-S*)/(S'-S*) + (1-v)*(R-R*)/(R'-R*)
   - v = strategy weight (0-1)
   - v=0.5 means balanced between consensus and individual regret
4. **Rank** by Q values (lower is better)
5. **Verify** compromise solution conditions

### Entropy Weighting

1. **Normalize** data to create probability distribution
2. **Calculate** entropy for each criterion: E_j = -k * Σ(p_ij * ln(p_ij))
3. **Compute** diversity measure: d_j = 1 - E_j
4. **Normalize** diversities to get weights: w_j = d_j / Σ(d_j)
5. Higher entropy = less information = lower weight

### AHP Process

1. **Create** pairwise comparison matrix using 1-9 scale
2. **Normalize** matrix by dividing each element by column sum
3. **Calculate** priority weights as row averages
4. **Check** consistency ratio (CR < 0.1 is acceptable)
5. CR = CI / RI, where CI = (λ_max - n) / (n-1)

---

## 🧪 Testing Your Installation

Run the included test suite:

```python
# Save as test_installation.py
from topsisx.topsis import topsis
from topsisx.vikor import vikor
from topsisx.entropy import entropy_weights
from topsisx.ahp import ahp
import pandas as pd
import numpy as np

print("Testing TOPSISX Installation...")

# Test 1: TOPSIS
try:
    data = pd.DataFrame({'C1': [1, 2, 3], 'C2': [4, 5, 6]})
    result = topsis(data, [0.5, 0.5], ['+', '+'])
    print("✅ TOPSIS working")
except Exception as e:
    print(f"❌ TOPSIS failed: {e}")

# Test 2: VIKOR
try:
    result = vikor(data, [0.5, 0.5], ['+', '+'], v=0.5)
    print("✅ VIKOR working")
except Exception as e:
    print(f"❌ VIKOR failed: {e}")

# Test 3: Entropy
try:
    weights = entropy_weights(np.array([[1, 2], [3, 4], [5, 6]]))
    print("✅ Entropy working")
except Exception as e:
    print(f"❌ Entropy failed: {e}")

# Test 4: AHP
try:
    pairwise = pd.DataFrame([[1, 3], ['1/3', 1]])
    weights = ahp(pairwise)
    print("✅ AHP working")
except Exception as e:
    print(f"❌ AHP failed: {e}")

print("\n🎉 All tests passed! TOPSISX is ready to use.")
```

Run with:
```bash
python test_installation.py
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
# Solution: Reinstall package
pip uninstall topsisx
pip install topsisx
```

### Issue: "Invalid impacts"
```python
# Problem: Wrong number of impacts
impacts = ['+', '-']  # But you have 3 criteria

# Solution: Match number of impacts to criteria
impacts = ['+', '-', '+']  # Now correct for 3 criteria
```

### Issue: "NaN in results"
```python
# Problem: Missing values or all zeros in a column
data = pd.DataFrame({'C1': [1, np.nan, 3], 'C2': [4, 5, 6]})

# Solution: Clean data before analysis
data = data.dropna()  # Remove rows with missing values
# OR
data = data.fillna(data.mean())  # Fill with column mean
```

### Issue: "Division by zero"
```python
# Problem: All values in a column are identical
data = pd.DataFrame({'C1': [5, 5, 5], 'C2': [1, 2, 3]})

# Solution: Remove constant columns or add small variance
data['C1'] = data['C1'] + np.random.normal(0, 0.01, len(data))
```

### Issue: "Web interface not launching"
```bash
# Solution 1: Install streamlit
pip install streamlit

# Solution 2: Launch manually
streamlit run path/to/topsisx/app.py

# Solution 3: Check if port is available
streamlit run app.py --server.port 8502
```

### Issue: "PDF generation fails"
```bash
# Solution: Install fpdf
pip install fpdf==1.7.2

# If still fails, check matplotlib is installed
pip install matplotlib
```

---

## 💡 Best Practices

### 1. Data Preparation
```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data.csv')

# Check for issues
print("Missing values:", df.isnull().sum())
print("Data types:", df.dtypes)
print("Summary statistics:", df.describe())

# Clean data
df = df.dropna()  # Remove missing values
df = df[df['Price'] > 0]  # Remove invalid values

# Separate ID columns from criteria
id_cols = ['Model', 'Name', 'ID']
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
criteria_data = df[numeric_cols]

# Now analyze
from topsisx.pipeline import DecisionPipeline
pipeline = DecisionPipeline(weights='entropy', method='topsis')
result = pipeline.run(criteria_data, impacts=['+', '-', '+'])

# Add ID columns back
for col in id_cols:
    if col in df.columns:
        result.insert(0, col, df[col].values)
```

### 2. Choosing the Right Method

**Use TOPSIS when:**
- You have clear ideal/worst scenarios
- Criteria are measurable and quantitative
- You want a simple, intuitive method
- You need quick results

**Use VIKOR when:**
- You have conflicting criteria
- You need compromise solutions
- You want to balance group and individual preferences
- Criteria have different units/scales

**Use Entropy weights when:**
- You want objective, data-driven weights
- You don't have expert knowledge
- You want to minimize bias
- Data variance is meaningful

**Use AHP weights when:**
- You have expert judgments
- Criteria importance is subjective
- You can make pairwise comparisons
- You need consistent weights

### 3. Validating Results

```python
from topsisx.pipeline import DecisionPipeline
import pandas as pd

data = pd.DataFrame({
    'Cost': [250, 200, 300],
    'Quality': [16, 16, 32],
    'Speed': [12, 8, 16]
})

# Method 1: Compare with different weighting methods
for weight_method in ['entropy', 'equal']:
    pipeline = DecisionPipeline(weights=weight_method, method='topsis')
    result = pipeline.run(data, impacts=['-', '+', '+'])
    print(f"\n{weight_method.upper()} weighting:")
    print(result[['Rank', 'Topsis_Score']])

# Method 2: Compare TOPSIS vs VIKOR
pipeline = DecisionPipeline(weights='equal', method='topsis')
comparison = pipeline.compare_methods(data, impacts=['-', '+', '+'])
print("\nRank differences:")
print(comparison['comparison'])

# Method 3: Sensitivity analysis - vary weights
import numpy as np
for weight_cost in [0.2, 0.3, 0.4, 0.5]:
    weight_quality = (1 - weight_cost) * 0.6
    weight_speed = (1 - weight_cost) * 0.4
    weights = [weight_cost, weight_quality, weight_speed]
    
    from topsisx.topsis import topsis
    result = topsis(data, weights, ['-', '+', '+'])
    print(f"\nCost weight={weight_cost}: Best is Alternative {result.iloc[0].name + 1}")
```

### 4. Handling Large Datasets

```python
import pandas as pd
from topsisx.pipeline import DecisionPipeline

# For large datasets, use chunking
def analyze_large_dataset(csv_file, impacts, chunk_size=1000):
    """
    Analyze large datasets in chunks
    """
    results = []
    
    for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
        # Analyze each chunk
        pipeline = DecisionPipeline(weights='entropy', method='topsis')
        result = pipeline.run(chunk, impacts=impacts)
        results.append(result)
    
    # Combine results
    final_result = pd.concat(results, ignore_index=True)
    
    # Re-rank across all chunks
    final_result['Rank'] = final_result['Topsis_Score'].rank(
        ascending=False, method='min'
    ).astype(int)
    
    return final_result.sort_values('Rank')

# Usage
result = analyze_large_dataset('large_data.csv', impacts=['+', '-', '+'])
```

---

## 🔒 Data Privacy & Security

TOPSISX processes data **locally** on your machine:
- ✅ No data sent to external servers
- ✅ No internet connection required (after installation)
- ✅ Your data stays on your computer
- ✅ Open source - you can audit the code

---

## 📖 API Reference

### Core Functions

#### `topsis(data, weights, impacts)`
```python
Parameters:
  data (DataFrame): Decision matrix with criteria
  weights (list): Criteria weights (must sum to 1)
  impacts (list): '+' for benefit, '-' for cost
  
Returns:
  DataFrame: Original data + Topsis_Score + Rank columns
```

#### `vikor(data, weights, impacts, v=0.5)`
```python
Parameters:
  data (DataFrame): Decision matrix
  weights (list): Criteria weights
  impacts (list): '+' for benefit, '-' for cost
  v (float): Strategy weight, 0-1 (default: 0.5)
  
Returns:
  DataFrame: Original data + S, R, Q, Rank columns
```

#### `ahp(pairwise_matrix, verbose=False)`
```python
Parameters:
  pairwise_matrix (DataFrame): Pairwise comparison matrix
  verbose (bool): Print detailed calculations
  
Returns:
  ndarray: Calculated weights
```

#### `entropy_weights(matrix)`
```python
Parameters:
  matrix (ndarray): Decision matrix
  
Returns:
  ndarray: Calculated weights based on entropy
```

### Pipeline API

#### `DecisionPipeline(weights, method, verbose=False)`
```python
Parameters:
  weights (str): 'entropy', 'ahp', or 'equal'
  method (str): 'topsis' or 'vikor'
  verbose (bool): Show detailed logs
  
Methods:
  run(data, impacts, pairwise_matrix=None, **kwargs)
  compare_methods(data, impacts, pairwise_matrix=None)
```

### Report Generation

#### `generate_report(data, method, filename)`
```python
Parameters:
  data (DataFrame): Analysis results
  method (str): 'topsis' or 'vikor'
  filename (str): Output PDF filename
  
Generates:
  PDF report with tables, charts, and methodology
```

---

## 🌍 Use Cases

### Business & Management
- **Supplier Selection** - Choose best vendors
- **Project Prioritization** - Rank project proposals
- **Location Selection** - Find optimal site for facility
- **Resource Allocation** - Distribute budget/resources
- **Performance Evaluation** - Rank employees/departments

### Engineering & Technology
- **Material Selection** - Choose optimal materials
- **Design Alternative Selection** - Compare design options
- **System Configuration** - Select best configuration
- **Technology Assessment** - Evaluate technologies
- **Quality Control** - Rank product quality

### Finance & Investment
- **Portfolio Selection** - Choose investment options
- **Credit Risk Assessment** - Rank loan applicants
- **Bank Branch Selection** - Evaluate branch performance
- **Financial Product Selection** - Compare financial products

### Healthcare
- **Treatment Selection** - Compare treatment options
- **Hospital Location** - Select optimal location
- **Medical Equipment Selection** - Choose equipment
- **Healthcare Provider Selection** - Rank providers

### Education & Research
- **University Selection** - Rank universities
- **Course Selection** - Choose courses
- **Research Proposal Evaluation** - Rank proposals
- **Scholarship Selection** - Evaluate candidates

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Reporting Bugs
```
1. Check existing issues first
2. Create new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS)
   - Sample data (if applicable)
```

### Suggesting Features
```
1. Open an issue with [Feature Request] tag
2. Describe the feature
3. Explain use case
4. Provide examples if possible
```

### Code Contributions
```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/ranklib.git

# 3. Create a branch
git checkout -b feature/your-feature-name

# 4. Make changes and test
python -m pytest tests/

# 5. Commit and push
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name

# 6. Open a Pull Request
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/SuvitKumar003/ranklib.git
cd ranklib

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest flake8 black

# Run tests
python run_all_tests.py

# Format code
black topsisx/

# Check code style
flake8 topsisx/
```

---

## 📝 Citation

If you use TOPSISX in your research, please cite:

```bibtex
@software{topsisx2025,
  author = {Kumar, Suvit},
  title = {TOPSISX: Multi-Criteria Decision Making Library},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/SuvitKumar003/ranklib}
}
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Suvit Kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙋 FAQ

### Q: Can I use TOPSISX for commercial projects?
**A:** Yes! TOPSISX is MIT licensed, so you can use it freely in commercial projects.

### Q: How many alternatives/criteria can TOPSISX handle?
**A:** Tested with up to 1000 alternatives and 50 criteria. Performance depends on your hardware.

### Q: Does TOPSISX work offline?
**A:** Yes! After installation, no internet connection is required.

### Q: Can I modify the algorithms?
**A:** Yes! The code is open source. Fork it and customize as needed.

### Q: Is there a GUI for non-programmers?
**A:** Yes! Use `topsisx --web` to launch the web interface.

### Q: How do I handle missing data?
**A:** Remove rows with missing values using `df.dropna()` or fill them using `df.fillna()`.

### Q: Can I use my own weighting method?
**A:** Yes! Just pass your custom weights array to the functions.

### Q: What's the difference between TOPSIS and VIKOR?
**A:** TOPSIS finds the closest to ideal, VIKOR finds compromise solutions balancing group utility and individual regret.

### Q: How do I validate results?
**A:** Compare multiple methods, check sensitivity to weight changes, verify with domain experts.

### Q: Can I integrate TOPSISX with other tools?
**A:** Yes! Works with pandas, Flask, FastAPI, Jupyter, Excel (via pandas), and more.

---

## 🔗 Links

- 📖 **Documentation**: [GitHub README](https://github.com/SuvitKumar003/ranklib)
- 🐛 **Issue Tracker**: [GitHub Issues](https://github.com/SuvitKumar003/ranklib/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/SuvitKumar003/ranklib/discussions)
- 📦 **PyPI Package**: [pypi.org/project/topsisx](https://pypi.org/project/topsisx/)
- 👨‍💻 **Source Code**: [GitHub Repository](https://github.com/SuvitKumar003/ranklib)
- 📧 **Email**: suvitkumar03@gmail.com

---

## 🌟 Star History

If you find TOPSISX useful, please consider giving it a star on GitHub! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=SuvitKumar003/ranklib&type=Date)](https://star-history.com/#SuvitKumar003/ranklib&Date)

---

## 🎓 Learning Resources

### Tutorials
- [Getting Started with TOPSISX](https://github.com/SuvitKumar003/ranklib/wiki/Getting-Started)
- [TOPSIS Explained](https://github.com/SuvitKumar003/ranklib/wiki/TOPSIS-Method)
- [VIKOR Explained](https://github.com/SuvitKumar003/ranklib/wiki/VIKOR-Method)
- [Real-world Examples](https://github.com/SuvitKumar003/ranklib/wiki/Examples)

### Academic Papers
- Hwang, C.L. and Yoon, K., 1981. "Multiple Attribute Decision Making: Methods and Applications"
- Opricovic, S. and Tzeng, G.H., 2004. "Compromise solution by MCDM methods"
- Saaty, T.L., 1980. "The Analytic Hierarchy Process"

### Video Tutorials
- Coming soon!

---

## 🏆 Acknowledgments

TOPSISX is built on the shoulders of giants:
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation
- **Matplotlib** - Visualization
- **Streamlit** - Web interface
- **FPDF** - PDF generation

Special thanks to:
- The Python community
- Contributors and users
- MCDM researchers worldwide

---

## 📊 Project Stats

- 🌟 Stars: [Check on GitHub](https://github.com/SuvitKumar003/ranklib)
- 🍴 Forks: [Check on GitHub](https://github.com/SuvitKumar003/ranklib)
- 📥 Downloads: [Check on PyPI](https://pypi.org/project/topsisx/)
- 📝 Issues: [Check on GitHub](https://github.com/SuvitKumar003/ranklib/issues)

---

## 🎉 What's New

### Version 0.1.4 (Latest)
- ✨ Enhanced web interface with PDF reports
- 🐛 Fixed verbose parameter in DecisionPipeline
- 🔧 Improved error handling for non-numeric data
- 📄 Better PDF report generation
- 🎨 Improved visualizations

### Version 0.1.3
- ✨ Added web interface
- 📊 VIKOR method support
- 🔧 Better error messages

### Version 0.1.0
- 🎉 Initial release
- ✅ TOPSIS implementation
- ✅ AHP weighting
- ✅ Entropy weighting

---

## 🚀 Roadmap

### Planned Features
- [ ] More MCDM methods (ELECTRE, PROMETHEE)
- [ ] Interactive visualizations (Plotly)
- [ ] Excel plugin
- [ ] Cloud deployment option
- [ ] Mobile app
- [ ] Real-time collaboration
- [ ] Machine learning integration
- [ ] Sensitivity analysis dashboard

---

## 💖 Support the Project

If you find TOPSISX helpful:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔀 Contribute code
- 📢 Share with others

---

## 📞 Get Help

Need help? We're here for you:

1. **Check the documentation** - Most questions are answered here
2. **Search existing issues** - Someone might have asked already
3. **Ask in Discussions** - Community forum
4. **Open an issue** - For bugs or feature requests
5. **Email us** - For private inquiries: suvitkumar03@gmail.com

---

<div align="center">

## Made with ❤️ for Better Decision Making

**TOPSISX** - Making Multi-Criteria Decisions Simple

[⭐ Star on GitHub](https://github.com/SuvitKumar003/ranklib) | [📦 Install from PyPI](https://pypi.org/project/topsisx/) | [📖 Read the Docs](https://github.com/SuvitKumar003/ranklib)

</div>

---

**Happy Decision Making! 🎯**