"""
TOPSISX Web Interface
Launch with: streamlit run app.py
Or after pip install: topsisx --web
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from topsisx.pipeline import DecisionPipeline
from topsisx.topsis import topsis
from topsisx.vikor import vikor
from topsisx.ahp import ahp
from topsisx.entropy import entropy_weights

# Page configuration
st.set_page_config(
    page_title="TOPSISX - Decision Making Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

def create_sample_data():
    """Create sample datasets for demonstration"""
    samples = {
        "Laptop Selection": pd.DataFrame({
            'Model': ['Laptop A', 'Laptop B', 'Laptop C', 'Laptop D'],
            'Price': [800, 1200, 1000, 900],
            'RAM_GB': [8, 16, 16, 8],
            'Battery_Hours': [6, 4, 8, 7],
            'Weight_KG': [2.0, 2.5, 1.8, 2.2]
        }),
        "Supplier Selection": pd.DataFrame({
            'Supplier': ['S1', 'S2', 'S3', 'S4', 'S5'],
            'Cost': [250, 200, 300, 275, 225],
            'Quality': [16, 16, 32, 32, 16],
            'Delivery_Time': [12, 8, 16, 8, 16],
            'Service_Rating': [5, 3, 4, 4, 2]
        }),
        "Investment Options": pd.DataFrame({
            'Option': ['Stock A', 'Stock B', 'Stock C', 'Bond X', 'Bond Y'],
            'Expected_Return': [12.5, 8.3, 15.2, 5.5, 6.0],
            'Risk_Level': [7, 4, 9, 2, 3],
            'Liquidity': [8, 9, 6, 7, 8],
            'Min_Investment': [1000, 500, 2000, 100, 200]
        })
    }
    return samples

def plot_ideal_distances(result_df, analysis_data, method_name):
    """
    Create visualization showing distance from ideal best and ideal worst
    for TOPSIS method
    """
    if method_name.upper() != "TOPSIS" or analysis_data is None:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Get distances
    dist_best = analysis_data.get('dist_best', [])
    dist_worst = analysis_data.get('dist_worst', [])
    
    if len(dist_best) == 0 or len(dist_worst) == 0:
        return None
    
    # Create labels for alternatives
    labels = [f"Alt {i+1}" for i in range(len(result_df))]
    
    # Get alternative names if available
    for col in result_df.columns:
        if col not in ['Rank', 'Topsis_Score', 'Q', 'S', 'R'] and result_df[col].dtype == 'object':
            labels = [str(val)[:20] for val in result_df[col].values]
            break
    
    x = np.arange(len(labels))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar(x - width/2, dist_best, width, label='Distance from Ideal Best', 
                   color='#ff6b6b', alpha=0.8)
    bars2 = ax.bar(x + width/2, dist_worst, width, label='Distance from Ideal Worst', 
                   color='#4ecdc4', alpha=0.8)
    
    # Customize
    ax.set_xlabel('Alternatives', fontsize=12, fontweight='bold')
    ax.set_ylabel('Distance', fontsize=12, fontweight='bold')
    ax.set_title('TOPSIS: Distance from Ideal Solutions', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    return fig

def get_download_link(df, filename, file_label):
    """Generate download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'
    return href

# Main UI
st.markdown('<h1 class="main-header">📊 TOPSISX Decision Making Tool</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Criteria Decision Analysis Made Simple</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/decision.png", width=80)
    st.title("⚙️ Configuration")
    
    # Data input method
    st.subheader("1️⃣ Data Input")
    input_method = st.radio(
        "Choose input method:",
        ["Upload CSV", "Use Sample Data", "Manual Entry"],
        help="Select how you want to provide your decision data"
    )
    
    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload your CSV file",
            type=['csv'],
            help="CSV should have alternatives as rows and criteria as columns"
        )
        
        if uploaded_file:
            try:
                st.session_state.data = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(st.session_state.data)} rows")
            except Exception as e:
                st.error(f"Error loading file: {e}")
    
    elif input_method == "Use Sample Data":
        samples = create_sample_data()
        sample_choice = st.selectbox("Select sample dataset:", list(samples.keys()))
        st.session_state.data = samples[sample_choice]
        st.info(f"📋 Loaded: {sample_choice}")
    
    else:  # Manual Entry
        st.info("👉 Go to main panel to enter data manually")
    
    st.markdown("---")
    
    # Method selection
    st.subheader("2️⃣ Method Selection")
    
    weighting_method = st.selectbox(
        "Weighting Method:",
        ["Entropy", "Equal", "Manual", "AHP"],
        help="How to calculate criteria importance"
    )
    
    ranking_method = st.selectbox(
        "Ranking Method:",
        ["TOPSIS", "VIKOR"],
        help="Algorithm for ranking alternatives"
    )
    
    # VIKOR parameter
    if ranking_method == "VIKOR":
        v_param = st.slider(
            "Strategy Weight (v)",
            0.0, 1.0, 0.5, 0.1,
            help="v=0: consensus, v=1: individual regret"
        )
    else:
        v_param = 0.5
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About TOPSISX"):
        st.markdown("""
        **TOPSISX** is a comprehensive toolkit for Multi-Criteria Decision Making (MCDM).
        
        **Methods Supported:**
        - **TOPSIS**: Ranks based on distance from ideal solution
        - **VIKOR**: Finds compromise solutions
        - **AHP**: Pairwise comparison for weights
        - **Entropy**: Objective weight calculation
        
        **Version**: 0.2.2 
        **Author**: Suvit Kumar
        """)

# Main content area
if input_method == "Manual Entry":
    st.header("📝 Manual Data Entry")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        n_alternatives = st.number_input("Number of Alternatives", 2, 20, 3)
    with col2:
        n_criteria = st.number_input("Number of Criteria", 2, 10, 3)
    
    st.subheader("Enter your data:")
    
    # Create empty dataframe for manual entry
    criteria_names = [st.text_input(f"Criterion {i+1} name", f"C{i+1}", key=f"crit_{i}") 
                      for i in range(n_criteria)]
    
    data_dict = {}
    for i, name in enumerate(criteria_names):
        data_dict[name] = [st.number_input(
            f"Alt {j+1} - {name}", 
            value=0.0, 
            key=f"val_{i}_{j}"
        ) for j in range(n_alternatives)]
    
    if st.button("📥 Load Manual Data"):
        st.session_state.data = pd.DataFrame(data_dict)
        st.success("✅ Data loaded successfully!")

# Display and process data
if st.session_state.data is not None:
    df = st.session_state.data.copy()
    
    st.header("📋 Input Data")
    st.dataframe(df, use_container_width=True)
    
    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("⚠️ Need at least 2 numeric criteria columns for analysis!")
    else:
        st.success(f"✅ Found {len(numeric_cols)} numeric criteria: {', '.join(numeric_cols)}")
        
        if non_numeric_cols:
            st.info(f"📌 Non-numeric columns (will be preserved): {', '.join(non_numeric_cols)}")
        
        # Impact selection
        st.subheader("3️⃣ Define Impacts")
        st.info("📌 '+' means higher is better (benefit), '-' means lower is better (cost)")
        
        impacts = []
        cols = st.columns(min(4, len(numeric_cols)))
        for i, col_name in enumerate(numeric_cols):
            with cols[i % len(cols)]:
                impact = st.selectbox(
                    f"{col_name}",
                    ['+', '-'],
                    key=f"impact_{i}",
                    help=f"Impact direction for {col_name}"
                )
                impacts.append(impact)
        
        # Manual weights input if needed
        manual_weights = None
        if weighting_method == "Manual":
            st.subheader("4️⃣ Enter Manual Weights")
            st.info("💡 Enter weights for each criterion (must sum to 1.0)")
            
            manual_weights = []
            weight_cols = st.columns(min(4, len(numeric_cols)))
            
            for i, col_name in enumerate(numeric_cols):
                with weight_cols[i % len(weight_cols)]:
                    weight = st.number_input(
                        f"{col_name}",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0/len(numeric_cols),
                        step=0.01,
                        key=f"weight_{i}",
                        help=f"Weight for {col_name}"
                    )
                    manual_weights.append(weight)
            
            # Display weight sum
            weight_sum = sum(manual_weights)
            if abs(weight_sum - 1.0) > 0.01:
                st.warning(f"⚠️ Weights sum to {weight_sum:.3f} (should be 1.0). They will be normalized automatically.")
            else:
                st.success(f"✅ Weights sum to {weight_sum:.3f}")
        
        # AHP matrix input if needed
        pairwise_matrix = None
        if weighting_method == "AHP":
            st.subheader("4️⃣ AHP Pairwise Comparison")
            st.info("Enter how much more important row criterion is compared to column criterion (1-9 scale)")
            
            with st.expander("📖 AHP Scale Reference"):
                st.markdown("""
                - **1**: Equal importance
                - **3**: Moderate importance
                - **5**: Strong importance
                - **7**: Very strong importance
                - **9**: Extreme importance
                - **2, 4, 6, 8**: Intermediate values
                """)
            
            # Simple AHP matrix input
            ahp_data = []
            for i in range(len(numeric_cols)):
                row = []
                for j in range(len(numeric_cols)):
                    if i == j:
                        row.append(1.0)
                    elif i < j:
                        val = st.number_input(
                            f"{numeric_cols[i]} vs {numeric_cols[j]}",
                            1.0, 9.0, 1.0, 0.5,
                            key=f"ahp_{i}_{j}"
                        )
                        row.append(val)
                    else:
                        # Reciprocal
                        row.append(1.0 / ahp_data[j][i])
                ahp_data.append(row)
            
            pairwise_matrix = pd.DataFrame(ahp_data)
        
        # Run analysis button
        st.markdown("---")
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing..."):
                try:
                    # Extract only numeric columns for analysis
                    numeric_data = df[numeric_cols].copy()
                    
                    # For TOPSIS, we need to calculate distances manually to store them
                    if ranking_method == "TOPSIS":
                        # Calculate weights
                        if weighting_method.lower() == "entropy":
                            weights = entropy_weights(numeric_data.values)
                        elif weighting_method.lower() == "equal":
                            weights = np.array([1/len(numeric_cols)] * len(numeric_cols))
                        elif weighting_method.lower() == "manual":
                            weights = np.array(manual_weights)
                            # Normalize if needed
                            if abs(weights.sum() - 1.0) > 0.01:
                                weights = weights / weights.sum()
                        elif weighting_method.lower() == "ahp":
                            weights = ahp(pairwise_matrix, verbose=False)
                        
                        # Manually calculate TOPSIS with distance tracking
                        matrix = numeric_data.values.astype(float)
                        norm_matrix = matrix / np.sqrt((matrix ** 2).sum(axis=0))
                        weighted_matrix = norm_matrix * weights
                        
                        ideal_best = np.zeros(len(numeric_cols))
                        ideal_worst = np.zeros(len(numeric_cols))
                        
                        for i in range(len(numeric_cols)):
                            if impacts[i] == '+':
                                ideal_best[i] = weighted_matrix[:, i].max()
                                ideal_worst[i] = weighted_matrix[:, i].min()
                            else:
                                ideal_best[i] = weighted_matrix[:, i].min()
                                ideal_worst[i] = weighted_matrix[:, i].max()
                        
                        dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
                        dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))
                        scores = dist_worst / (dist_best + dist_worst + 1e-10)
                        
                        # Store analysis data
                        st.session_state.analysis_data = {
                            'dist_best': dist_best,
                            'dist_worst': dist_worst,
                            'ideal_best': ideal_best,
                            'ideal_worst': ideal_worst
                        }
                        
                        # Create result dataframe
                        result = numeric_data.copy()
                        result['Topsis_Score'] = scores
                        scores_series = pd.Series(scores)
                        result['Rank'] = scores_series.rank(ascending=False, method='min').astype(int)
                    else:
                        # Use pipeline for VIKOR
                        pipeline = DecisionPipeline(
                            weights=weighting_method.lower(),
                            method=ranking_method.lower(),
                            verbose=False
                        )
                        
                        result = pipeline.run(
                            numeric_data,
                            impacts=impacts,
                            pairwise_matrix=pairwise_matrix,
                            v=v_param
                        )
                        st.session_state.analysis_data = None
                    
                    # Add back non-numeric columns (IDs, names, etc.) to result
                    for col in non_numeric_cols:
                        result.insert(0, col, df[col].values)
                    
                    # Store results WITHOUT sorting - maintains original order
                    st.session_state.results = result
                    st.success("✅ Analysis completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)

# Display results
if st.session_state.results is not None:
    result = st.session_state.results
    
    st.markdown("---")
    st.header("🏆 Results")
    
    # Success banner with PDF info
    st.success("✅ **Analysis Complete!** Your results are ready for download below.")
    
    # Prominent PDF download banner
    st.info("📄 **Professional PDF Report Available** - Click the button below to download a comprehensive report with charts and analysis.")
    
    # Results table
    st.subheader("📊 Ranking Table")
    st.dataframe(result, use_container_width=True)
    
    # Download buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download Results (CSV)",
            data=result.to_csv(index=False),
            file_name=f"topsisx_results_{ranking_method.lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Generate PDF report
        try:
            from topsisx.reports import generate_report
            import os
            
            # Generate PDF
            pdf_filename = f"topsisx_report_{ranking_method.lower()}.pdf"
            generate_report(result, method=ranking_method, filename=pdf_filename)
            
            # Read PDF file
            with open(pdf_filename, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
            
            # Clean up temporary file
            if os.path.exists(pdf_filename):
                os.remove(pdf_filename)
                
            # Show success banner
            st.success("✅ PDF Report Generated Successfully! Click button above to download.")
            
        except Exception as e:
            st.warning(f"⚠️ PDF generation failed: {e}")
    
    # NEW: Ideal Distance Visualization (only for TOPSIS)
    if ranking_method == "TOPSIS" and st.session_state.analysis_data is not None:
        st.subheader("📈 Distance from Ideal Solutions")
        st.info("💡 Better alternatives are closer to Ideal Best and farther from Ideal Worst")
        
        try:
            fig = plot_ideal_distances(result, st.session_state.analysis_data, ranking_method)
            if fig:
                st.pyplot(fig)
            else:
                st.warning("Could not generate distance visualization")
        except Exception as e:
            st.warning(f"Could not generate visualization: {e}")
    
    # Top alternatives
    st.subheader("🥇 Top 3 Alternatives")
    # Sort ONLY for this display (using a copy), don't modify session state
    top_3 = result.sort_values(by='Rank').head(3)
    
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            medal = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"### {medal} Rank {int(row['Rank'])}")
            
            # Display non-numeric columns (IDs)
            for col in result.columns:
                if col not in ['Rank', 'Topsis_Score', 'Q', 'S', 'R']:
                    st.metric(col, row[col])
    
    # Detailed statistics
    with st.expander("📊 Detailed Statistics"):
        st.write("**Summary Statistics:**")
        
        score_col = 'Topsis_Score' if 'Topsis_Score' in result.columns else 'Q'
        if score_col in result.columns:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Score", f"{result[score_col].mean():.4f}")
            with col2:
                st.metric("Std Dev", f"{result[score_col].std():.4f}")
            with col3:
                st.metric("Min Score", f"{result[score_col].min():.4f}")
            with col4:
                st.metric("Max Score", f"{result[score_col].max():.4f}")

else:
    # Welcome screen
    if st.session_state.data is None:
        st.info("👈 Please upload data or select a sample dataset from the sidebar to begin")
        
        st.markdown("---")
        st.subheader("🚀 Quick Start Guide")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 1️⃣ Input Data")
            st.markdown("""
            - Upload CSV file
            - Use sample data
            - Enter manually
            """)
        
        with col2:
            st.markdown("### 2️⃣ Configure")
            st.markdown("""
            - Select methods
            - Define impacts
            - Set parameters
            """)
        
        with col3:
            st.markdown("### 3️⃣ Analyze")
            st.markdown("""
            - Run analysis
            - View results
            - Download report
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Made with ❤️ using <b>TOPSISX</b> | Version 0.1.4</p>
    <p>For support: <a href='https://github.com/SuvitKumar003/ranklib'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)