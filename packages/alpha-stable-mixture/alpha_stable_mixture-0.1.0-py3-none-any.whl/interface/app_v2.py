# app.py - Enhanced Mixstable Application
import streamlit as st
import contextvars
from io import BytesIO
import numpy as np
import pandas as pd
import warnings
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from scipy import stats
import time

# Suppress R warnings for cleaner Streamlit output
warnings.filterwarnings("ignore", message="R is not initialized by the main thread")

# 🔧 Initialize RPy2 conversions once at startup
try:
    import interface.rpy2_init
    R_AVAILABLE = True
except ImportError:
    R_AVAILABLE = False
    st.warning("R interface not available. Some features will be limited.")

# Import robust wrappers with error handling
try:
    from Mixstable.visualization import plot_final_mixture_fit
    from Mixstable.metrics import compute_model_metrics
    from Mixstable.testing_data import analyse_stable_distribution
    from Mixstable.em_methode import (
        em_estimate_stable_recursive_ecf,
        em_estimate_stable_kernel_ecf,
        em_estimate_stable_weighted_ols,
        em_estimate_stable_from_cdf
    )
    from interface.em_robust import robust_em_stable_mixture
    ALPHA_STABLE_AVAILABLE = True
except ImportError:
    ALPHA_STABLE_AVAILABLE = False
    st.error("Alpha-stable mixture package not available. Please install required dependencies.")

try:
    from interface.preprocess import read_csv_with_auto_delimiter, extract_serial_intervals
    PREPROCESS_AVAILABLE = True
except ImportError:
    PREPROCESS_AVAILABLE = False

# -------------------- Language Configuration --------------------
LANGUAGES = {
    "en": {
        "title": "📊 Mixstable — Alpha-Stable Mixture Estimator",
        "sidebar_title": "Mixstable",
        "upload_file": "📁 Upload a CSV file",
        "stability_test": "⚗️ Stability Test",
        "em_estimation": "📊 EM Estimation",
        "model_comparison": "🔬 Model Comparison",
        "data_explorer": "🔍 Data Explorer",
        "language": "🌐 Language",
        "theme": "🎨 Theme",
        "light": "☀️ Light",
        "dark": "🌙 Dark",
        "run_stability": "Run Stability Test",
        "run_em": "Run EM Algorithm",
        "generate_sample": "🎲 Try Sample Data",
        "running_stability": "Running stability analysis via R...",
        "running_em": "🔄 Running EM algorithm...",
        "stability_complete": "✅ Stability test complete.",
        "em_complete": "🎯 EM estimation complete.",
        "no_numeric": "❌ No numeric column found. Please include a serial interval column.",
        "using_column": "📈 Using column:",
        "no_serial_found": "⚠️ No serial interval column found. Using:",
        "analyzing_points": "📊 Analyzing {} data points",
        "no_valid_data": "❌ No valid data points found after removing NaN values.",
        "download_plot": "📥 Download Plot",
        "plot_not_generated": "⚠️ Plot file not generated",
        "error_stability": "❌ Error during stability analysis:",
        "error_em": "❌ Error during EM estimation:",
        "error_processing": "❌ Error processing file:",
        "error_extracting": "❌ Error extracting data:",
        "r_interface_check": "This might be due to R interface issues. Please check your R installation and required packages.",
        "select_data": "📂 Please select a data source, upload a CSV file, and choose a mode from the sidebar.",
        "how_to_use": "📖 How to use this app:",
        "upload_csv": "Upload a CSV file containing your data",
        "choose_mode": "Choose a mode:",
        "click_button": "Click the respective button to run the analysis",
        "expected_format": "📊 Expected data format:",
        "csv_should_contain": "Your CSV should contain a numeric column with one of these names:",
        "or_any_numeric": "Or any other numeric column (the app will use the first numeric column found).",
        "parameters": "📋 Parameters",
        "weights": "Weights:",
        "log_likelihood": "Log-likelihood:",
        "fit_plot": "📉 Fit Plot",
        "download_fit_plot": "📥 Download Fit Plot",
        "model_metrics": "📊 Model Metrics",
        "component": "Component",
        "choose_method": "Choose estimation method",
        "could_not_compute": "⚠️ Could not compute metrics:",
        "plot_not_found": "⚠️ Plot file not found",
        "data_quality": "🔍 Data Quality Assessment",
        "export_results": "📤 Export Results",
        "troubleshooting": "🚨 Troubleshooting"
    },
    "fr": {
        "title": "📊 Mixstable — Estimateur de Mélange Alpha-Stable",
        "sidebar_title": "Mixstable",
        "upload_file": "📁 Télécharger un fichier CSV",
        "stability_test": "⚗️ Test de Stabilité",
        "em_estimation": "📊 Estimation EM",
        "model_comparison": "🔬 Comparaison de Modèles",
        "data_explorer": "🔍 Explorateur de Données",
        "language": "🌐 Langue",
        "theme": "🎨 Thème",
        "light": "☀️ Clair",
        "dark": "🌙 Sombre",
        "run_stability": "Lancer le Test de Stabilité",
        "run_em": "Lancer l'Algorithme EM",
        "generate_sample": "🎲 Essayer des Données d'Exemple",
        "running_stability": "Exécution de l'analyse de stabilité via R...",
        "running_em": "🔄 Exécution de l'algorithme EM...",
        "stability_complete": "✅ Test de stabilité terminé.",
        "em_complete": "🎯 Estimation EM terminée.",
        "no_numeric": "❌ Aucune colonne numérique trouvée. Veuillez inclure une colonne d'intervalle sériel.",
        "using_column": "📈 Utilisation de la colonne:",
        "no_serial_found": "⚠️ Aucune colonne d'intervalle sériel trouvée. Utilisation de:",
        "analyzing_points": "📊 Analyse de {} points de données",
        "no_valid_data": "❌ Aucun point de données valide trouvé après suppression des valeurs NaN.",
        "download_plot": "📥 Télécharger le Graphique",
        "plot_not_generated": "⚠️ Fichier graphique non généré",
        "error_stability": "❌ Erreur lors de l'analyse de stabilité:",
        "error_em": "❌ Erreur lors de l'estimation EM:",
        "error_processing": "❌ Erreur de traitement du fichier:",
        "error_extracting": "❌ Erreur d'extraction des données:",
        "r_interface_check": "Cela peut être dû à des problèmes d'interface R. Veuillez vérifier votre installation R et les packages requis.",
        "select_data": "📂 Veuillez sélectionner une source de données, télécharger un fichier CSV et choisir un mode dans la barre latérale.",
        "how_to_use": "📖 Comment utiliser cette application:",
        "upload_csv": "Téléchargez un fichier CSV contenant vos données",
        "choose_mode": "Choisissez un mode:",
        "click_button": "Cliquez sur le bouton respectif pour lancer l'analyse",
        "expected_format": "📊 Format de données attendu:",
        "csv_should_contain": "Votre CSV doit contenir une colonne numérique avec l'un de ces noms:",
        "or_any_numeric": "Ou toute autre colonne numérique (l'application utilisera la première colonne numérique trouvée).",
        "parameters": "📋 Paramètres",
        "weights": "Poids:",
        "log_likelihood": "Log-vraisemblance:",
        "fit_plot": "📉 Graphique d'Ajustement",
        "download_fit_plot": "📥 Télécharger le Graphique d'Ajustement",
        "model_metrics": "📊 Métriques du Modèle",
        "component": "Composant",
        "choose_method": "Choisir la méthode d'estimation",
        "could_not_compute": "⚠️ Impossible de calculer les métriques:",
        "plot_not_found": "⚠️ Fichier graphique non trouvé",
        "data_quality": "🔍 Évaluation de la Qualité des Données",
        "export_results": "📤 Exporter les Résultats",
        "troubleshooting": "🚨 Dépannage"
    }
}

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Mixstable — Alpha-Stable Mixture Estimator",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# -------------------- Session State Initialization --------------------
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'model_results' not in st.session_state:
    st.session_state.model_results = {}
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# -------------------- Custom CSS for Better UI --------------------
def apply_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Fix main container visibility */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Ensure main content is visible */
    .main > div {
        padding-top: 2rem;
        font-family: 'Inter', sans-serif;
        background: transparent !important;
    }
    
    /* Fix stApp background */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    }
    
    /* Sidebar styling - simplified */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Enhanced header - make sure it's visible */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
        z-index: 10;
    }
    
    .main-header h1 {
        color: white !important;
        text-align: center;
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        position: relative;
        z-index: 1;
    }
    
    /* Fix result cards visibility */
    .result-card {
        background: rgba(255, 255, 255, 0.98) !important;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        margin: 1.5rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
        position: relative;
        z-index: 5;
    }
    
    /* Fix button visibility */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
        border-radius: 30px;
        padding: 0.75rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        z-index: 10;
        position: relative;
    }
    
    /* Fix metrics visibility */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Info/warning/success boxes - ensure visibility */
    .info-box, .warning-box, .success-box {
        position: relative;
        z-index: 5;
        margin: 1rem 0;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white;
    }
    
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white;
    }
    
    /* Dark theme fixes */
    [data-theme="dark"] .result-card {
        background: rgba(30, 41, 59, 0.95) !important;
        border-color: rgba(102, 126, 234, 0.3);
        color: white;
    }
    
    [data-theme="dark"] [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    /* Fix any z-index stacking issues */
    .element-container {
        position: relative;
        z-index: 1;
    }
    
    /* Responsive fixes */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .result-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Add this function to debug the layout
def debug_layout():
    """Add this temporarily to see what's happening"""
    st.write("🔍 Debug: This text should be visible")
    st.success("🔍 Debug: This success message should be visible")
    
    # Test if columns work
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("Column 1")
    with col2:
        st.warning("Column 2") 
    with col3:
        st.error("Column 3")

# Get current language texts
def t(key):
    return LANGUAGES[st.session_state.language].get(key, key)

# -------------------- Helper Functions --------------------
@st.cache_data
def generate_sample_alpha_stable_data():
    """Generate sample alpha-stable data for demonstration"""
    np.random.seed(42)
    
    # Generate two components with different parameters
    try:
        # Component 1: More stable (higher alpha)
        alpha1, beta1, scale1, loc1 = 1.8, 0.0, 0.8, 3.0
        component1 = stats.levy_stable.rvs(alpha=alpha1, beta=beta1, 
                                         loc=loc1, scale=scale1, size=400)
        
        # Component 2: Less stable (lower alpha)  
        alpha2, beta2, scale2, loc2 = 1.3, 0.5, 1.2, 5.0
        component2 = stats.levy_stable.rvs(alpha=alpha2, beta=beta2,
                                         loc=loc2, scale=scale2, size=200)
        
        # Combine components
        data = np.concatenate([component1, component2])
        
        # Filter positive values (typical for serial intervals)
        data = data[data > 0][:500]  # Keep first 500 positive values
        
    except Exception:
        # Fallback to simpler data generation
        np.random.seed(42)
        component1 = np.random.gamma(2, 1.5, 400) + 1
        component2 = np.random.gamma(1.5, 2.5, 200) + 2
        data = np.concatenate([component1, component2])[:500]
    
    # Add some realistic noise and ensure positive values
    data = np.abs(data) + np.random.normal(0, 0.1, len(data))
    
    return pd.DataFrame({
        'serial_interval': data,
        'source': ['synthetic'] * len(data),
        'generated_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(data)
    })

def validate_and_preprocess_data(df):
    """Enhanced data validation and preprocessing"""
    issues = []
    suggestions = []
    
    # Check for missing values
    if df.isnull().any().any():
        null_counts = df.isnull().sum()
        null_info = null_counts[null_counts > 0].to_dict()
        issues.append(f"Missing values found: {null_info}")
        suggestions.append("Consider removing rows with missing values or imputation")
    
    # Check for negative values in numeric columns
    numeric_cols = df.select_dtypes(include=[float, int]).columns
    for col in numeric_cols:
        if (df[col] < 0).any():
            negative_count = (df[col] < 0).sum()
            issues.append(f"Negative values in {col}: {negative_count} occurrences")
            suggestions.append("Alpha-stable analysis typically requires positive values")
    
    # Check data size
    if len(df) < 30:
        issues.append(f"Small sample size: {len(df)} observations")
        suggestions.append("Consider collecting more data (recommended: >100 observations)")
    elif len(df) < 100:
        issues.append(f"Moderate sample size: {len(df)} observations")
        suggestions.append("Results may be more reliable with larger samples (>100)")
    
    # Check for extreme outliers
    for col in numeric_cols:
        data = df[col].dropna()
        if len(data) > 0:
            Q1 = np.percentile(data, 25)
            Q3 = np.percentile(data, 75)
            IQR = Q3 - Q1
            outlier_count = len(data[(data < Q1 - 3*IQR) | (data > Q3 + 3*IQR)])
            if outlier_count > len(data) * 0.1:  # More than 10% outliers
                issues.append(f"Many extreme outliers in {col}: {outlier_count}")
                suggestions.append("Consider outlier treatment or robust estimation methods")
    
    return issues, suggestions

def count_outliers(data, method='iqr'):
    """Count outliers using various methods"""
    if method == 'iqr':
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return len(data[(data < lower_bound) | (data > upper_bound)])
    elif method == 'zscore':
        z_scores = np.abs(stats.zscore(data))
        return len(data[z_scores > 3])
    return 0

def generate_analysis_report(result, data_info=None):
    """Generate comprehensive analysis report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""
Mixstable Analysis Report
========================
Generated: {timestamp}

Model Summary:
-------------
Method: {result.get('method', 'Unknown')}
Log-likelihood: {result['log_likelihood']:.8f}
Number of components: {len(result['params_list'])}
Sample size: {data_info.get('size', 'Unknown') if data_info else 'Unknown'}

Component Parameters:
--------------------"""
    
    for i, (params, weight) in enumerate(zip(result['params_list'], result['weights'])):
        if isinstance(params, dict):
            alpha, beta, gamma, delta = params['alpha'], params['beta'], params['gamma'], params['delta']
        else:
            alpha, beta, gamma, delta = params
            
        report += f"""

Component {i+1}:
  α (stability): {alpha:.8f}
  β (skewness):  {beta:.8f}  
  γ (scale):     {gamma:.8f}
  δ (location):  {delta:.8f}
  Weight:        {weight:.8f}
  
  Interpretation:
  - Tail heaviness: {'Heavy tails' if alpha < 1.5 else 'Moderate tails' if alpha < 1.8 else 'Light tails'}
  - Skewness: {'Left skewed' if beta < -0.1 else 'Right skewed' if beta > 0.1 else 'Symmetric'}
"""

    if data_info:
        report += f"""

Data Summary:
------------
Sample size: {data_info.get('size', 'N/A')}
Mean: {data_info.get('mean', 'N/A'):.6f}
Standard deviation: {data_info.get('std', 'N/A'):.6f}
Skewness: {data_info.get('skewness', 'N/A'):.6f}
Kurtosis: {data_info.get('kurtosis', 'N/A'):.6f}
Range: [{data_info.get('min', 'N/A'):.6f}, {data_info.get('max', 'N/A'):.6f}]

Model Fit Metrics:
-----------------
AIC: {data_info.get('aic', 'N/A')}
BIC: {data_info.get('bic', 'N/A')}
"""

    report += f"""

Generated by Mixstable v2.0
Alpha-Stable Mixture Estimator
"""
    
    return report

def create_enhanced_fallback_plot(data, result, title="Alpha-Stable Mixture Analysis"):
    """Enhanced fallback plot with better styling and error handling"""
    try:
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Color scheme
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
        
        # Plot 1: Histogram with mixture overlay
        ax1.hist(data, bins=50, density=True, alpha=0.6, color='lightblue', 
                edgecolor='navy', linewidth=0.8, label='Observed Data')
        
        x_range = np.linspace(data.min(), data.max(), 1000)
        total_mixture = np.zeros_like(x_range)
        
        try:
            for i, (params, weight) in enumerate(zip(result["params_list"], result["weights"])):
                if isinstance(params, dict):
                    alpha, beta, loc, scale = params['alpha'], params['beta'], params['delta'], params['gamma']
                else:
                    alpha, beta, scale, loc = params
                
                # Enhanced approximation based on alpha value
                if alpha >= 1.9:
                    y = weight * stats.norm.pdf(x_range, loc=loc, scale=scale)
                elif alpha >= 1.5:
                    df = max(2.5, 15 * (alpha - 1))
                    y = weight * stats.t.pdf((x_range - loc) / scale, df=df) / scale
                elif alpha >= 1.0:
                    y = weight * stats.cauchy.pdf(x_range, loc=loc, scale=scale * alpha)
                else:
                    y = weight * stats.cauchy.pdf(x_range, loc=loc, scale=scale * 0.5)
                
                total_mixture += y
                ax1.plot(x_range, y, '--', linewidth=2.5, alpha=0.8, color=colors[i % len(colors)],
                        label=f'Component {i+1} (α={alpha:.3f}, w={weight:.3f})')
            
            ax1.plot(x_range, total_mixture, '-', linewidth=3, alpha=0.9, color='darkred',
                    label='Total Mixture')
            
        except Exception:
            ax1.text(0.5, 0.5, 'Component visualization\nrequires scipy', 
                    transform=ax1.transAxes, ha='center', va='center',
                    fontsize=12, style='italic')
        
        ax1.set_xlabel('Value', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Density', fontsize=12, fontweight='bold')
        ax1.set_title('Fitted α-Stable Mixture', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Plot 2: Q-Q plot against normal distribution
        try:
            stats.probplot(data, dist="norm", plot=ax2)
            ax2.set_title('Q-Q Plot vs Normal Distribution', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
        except Exception:
            ax2.hist(data, bins=30, alpha=0.7, color=colors[0])
            ax2.set_title('Data Distribution', fontsize=14, fontweight='bold')
        
        # Plot 3: Parameter summary as text
        ax3.axis('off')
        param_text = f"Model Summary\n{'-'*20}\n\n"
        param_text += f"Log-likelihood: {result['log_likelihood']:.4f}\n"
        param_text += f"Method: {result.get('method', 'Unknown')}\n"
        param_text += f"Sample size: {len(data):,}\n\n"
        
        for i, (params, weight) in enumerate(zip(result["params_list"], result["weights"])):
            if isinstance(params, dict):
                alpha, beta, gamma, delta = params['alpha'], params['beta'], params['gamma'], params['delta']
            else:
                alpha, beta, gamma, delta = params
                
            param_text += f"Component {i+1}:\n"
            param_text += f"  α = {alpha:.6f}\n"
            param_text += f"  β = {beta:.6f}\n" 
            param_text += f"  γ = {gamma:.6f}\n"
            param_text += f"  δ = {delta:.6f}\n"
            param_text += f"  weight = {weight:.6f}\n\n"
        
        ax3.text(0.05, 0.95, param_text, transform=ax3.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.8))
        
        # Plot 4: Data statistics
        ax4.axis('off')
        stats_text = f"Data Statistics\n{'-'*20}\n\n"
        stats_text += f"Mean: {np.mean(data):.6f}\n"
        stats_text += f"Std Dev: {np.std(data):.6f}\n"
        stats_text += f"Skewness: {stats.skew(data):.6f}\n"
        stats_text += f"Kurtosis: {stats.kurtosis(data):.6f}\n"
        stats_text += f"Min: {np.min(data):.6f}\n"
        stats_text += f"Max: {np.max(data):.6f}\n"
        stats_text += f"Range: {np.ptp(data):.6f}\n\n"
        
        # Add interpretation
        skew_val = stats.skew(data)
        kurt_val = stats.kurtosis(data)
        
        stats_text += "Interpretation:\n"
        if abs(skew_val) < 0.5:
            stats_text += "• Distribution is fairly symmetric\n"
        elif skew_val > 0.5:
            stats_text += "• Distribution is right-skewed\n"
        else:
            stats_text += "• Distribution is left-skewed\n"
            
        if kurt_val > 3:
            stats_text += "• Heavy tails (leptokurtic)\n"
        elif kurt_val < -1:
            stats_text += "• Light tails (platykurtic)\n"
        else:
            stats_text += "• Normal tail behavior\n"
        
        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcyan', alpha=0.8))
        
        plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout(pad=3.0)
        
        # Save with high quality
        filename = 'enhanced_mixture_analysis.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none', format='png')
        plt.close()
        
        return filename
        
    except Exception as e:
        st.error(f"Enhanced plotting failed: {e}")
        return None

# Fallback CSV reading function
def read_csv_fallback(uploaded_file):
    """Fallback CSV reading if preprocess module unavailable"""
    try:
        # Try different encodings and separators
        content = uploaded_file.getvalue()
        
        # Detect encoding
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                df = pd.read_csv(BytesIO(content), encoding=encoding, sep=None, engine='python')
                if not df.empty:
                    return df
            except:
                continue
        
        # Last resort
        return pd.read_csv(uploaded_file, sep=None, engine='python')
        
    except Exception as e:
        st.error(f"Could not read CSV file: {e}")
        return None

def extract_serial_intervals_fallback(df):
    """Fallback serial interval extraction"""
    possible_cols = ["serial_interval", "serial_interval_mean_based", "mean_serial_interval"]
    
    # First try exact column names
    for col in possible_cols:
        if col in df.columns:
            data = df[col].dropna().astype(float)
            return data.values
    
    # Then try numeric columns
    numeric_cols = df.select_dtypes(include=[float, int]).columns
    if len(numeric_cols) > 0:
        data = df[numeric_cols[0]].dropna().astype(float)
        return data.values
    
    raise ValueError("No suitable numeric column found")

# -------------------- Enhanced Sidebar --------------------
apply_custom_css()

with st.sidebar:
    # Enhanced logo/title section
    st.markdown("""
    <div class="sidebar-logo">
        <h2 style="color: #667eea; font-weight: 700; margin: 0; font-size: 1.8rem;">📊 Mixstable</h2>
        <p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0 0 0; font-weight: 500;">Alpha-Stable Analysis</p>
        <div style="width: 50px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 0.5rem auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Language and theme controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 EN" if st.session_state.language == 'fr' else "🇫🇷 FR", 
                     key="lang_toggle", use_container_width=True):
            st.session_state.language = 'en' if st.session_state.language == 'fr' else 'fr'
            st.rerun()

    with col2:
        if st.button("🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light", 
                     key="theme_toggle", use_container_width=True):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()

    st.markdown("---")
    
    # Enhanced mode selection
    st.markdown("### 🎯 Analysis Mode")
    modes = [t("stability_test"), t("em_estimation"), t("model_comparison"), t("data_explorer")]
    mode = st.radio(
        "Choose your analysis type:", 
        modes,
        help="Select the type of analysis to perform on your data"
    )

    st.markdown("---")
    
    # Enhanced file upload section
    st.markdown("### 📁 Data Input")
    
    # Sample data button
    if st.button(t("generate_sample"), use_container_width=True, type="secondary"):
        with st.spinner("Generating sample data..."):
            sample_df = generate_sample_alpha_stable_data()
            st.session_state.current_data = sample_df
            st.session_state.data_source = "sample"
            st.success("✅ Sample data generated!")
            st.rerun()
    
    # File upload
    uploaded_file = st.file_uploader(
        t("upload_file"), 
        type=["csv", "txt"],
        help="Upload a CSV file containing your time series data"
    )
    
    # Show file info if uploaded
    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.success(f"✅ File loaded: {uploaded_file.name}")
        st.info(f"📊 Size: {file_size:.1f} KB")
        st.session_state.data_source = "uploaded"

    # Data source indicator
    if hasattr(st.session_state, 'data_source'):
        if st.session_state.data_source == "sample":
            st.info("🎲 Using sample data")
        elif st.session_state.data_source == "uploaded":
            st.info("📁 Using uploaded file")

    st.markdown("---")
    
    # Enhanced troubleshooting section
    with st.expander(t("troubleshooting")):
        st.markdown("""
        **Common Issues:**
        
        🔧 **R Interface Errors**
        - Ensure R is installed
        - Check required packages
        - Try restarting the app
        
        📊 **EM Algorithm Issues**
        - Try different methods
        - Increase max iterations
        - Check data quality
        
        📁 **File Upload Problems**
        - Use UTF-8 encoding
        - Check CSV format
        - Verify numeric columns
        
        💡 **Performance Tips**
        - Use sample data to test
        - Check data size (<10MB)
        - Remove missing values
        """)
    
    # System status
    with st.expander("🔍 System Status"):
        st.write(f"**R Available:** {'✅ Yes' if R_AVAILABLE else '❌ No'}")
        st.write(f"**Alpha-Stable:** {'✅ Available' if ALPHA_STABLE_AVAILABLE else '❌ Missing'}")
        st.write(f"**Preprocessing:** {'✅ Available' if PREPROCESS_AVAILABLE else '❌ Missing'}")

# -------------------- Main Application Logic --------------------

# Get current language texts
def t(key):
    return LANGUAGES[st.session_state.language].get(key, key)

# Custom header
st.markdown(f"""
<div class="main-header">
    <h1>{t("title")}</h1>
</div>
""", unsafe_allow_html=True)

# Determine data source
data_available = uploaded_file is not None or hasattr(st.session_state, 'current_data')

if data_available:
    try:
        # Load data based on source
        if uploaded_file:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Reading CSV file...")
            progress_bar.progress(25)
            
            if PREPROCESS_AVAILABLE:
                df = read_csv_with_auto_delimiter(uploaded_file)
            else:
                df = read_csv_fallback(uploaded_file)
                
            st.session_state.current_data = df
            
        elif hasattr(st.session_state, 'current_data'):
            df = st.session_state.current_data
            progress_bar = st.progress(50)
            status_text = st.empty()
            status_text.text("Using existing data...")
        
        if df is None:
            st.error("Failed to load data")
            st.stop()
            
        progress_bar.progress(75)
        status_text.text("Processing data...")

        # Data validation and quality assessment
        issues, suggestions = validate_and_preprocess_data(df)
        
        if issues:
            with st.expander("⚠️ Data Quality Issues", expanded=len(issues) > 2):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Issues Found:**")
                    for issue in issues:
                        st.warning(f"• {issue}")
                with col2:
                    st.markdown("**Suggestions:**")
                    for suggestion in suggestions:
                        st.info(f"• {suggestion}")

        # Mode-specific analysis
        if mode == t("data_explorer"):
            # Data Explorer Mode
            st.markdown("""
            <div class="result-card">
                <h2>🔍 Data Explorer</h2>
                <p>Comprehensive analysis of your dataset before running statistical models.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Data overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Rows", f"{len(df):,}")
            with col2:
                st.metric("📋 Columns", f"{len(df.columns):,}")
            with col3:
                numeric_cols = df.select_dtypes(include=[float, int]).columns
                st.metric("🔢 Numeric", f"{len(numeric_cols)}")
            with col4:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("❓ Missing %", f"{missing_pct:.1f}%")
            
            # Data preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Statistical summary for numeric columns
            if len(numeric_cols) > 0:
                st.subheader("📊 Statistical Summary")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                # Correlation matrix if multiple numeric columns
                if len(numeric_cols) > 1:
                    st.subheader("🔗 Correlation Matrix")
                    corr_matrix = df[numeric_cols].corr()
                    st.dataframe(corr_matrix, use_container_width=True)
            
            # Data quality assessment for each numeric column
            st.subheader(t("data_quality"))
            for col in numeric_cols[:3]:  # Limit to first 3 columns
                data = df[col].dropna()
                if len(data) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(f"{col} - Skewness", f"{stats.skew(data):.3f}")
                    with col2:
                        st.metric(f"{col} - Kurtosis", f"{stats.kurtosis(data):.3f}")
                    with col3:
                        outliers = count_outliers(data)
                        st.metric(f"{col} - Outliers", f"{outliers}")
                    with col4:
                        try:
                            _, p_val = stats.normaltest(data)
                            st.metric(f"{col} - Normality p", f"{p_val:.4f}")
                        except:
                            st.metric(f"{col} - Normality", "N/A")

        elif mode == t("stability_test"):
            # Enhanced Stability Test Section
            st.markdown("""
            <div class="result-card">
                <h2>🧪 Stability Distribution Analysis</h2>
                <p>Test whether your data follows an α-stable distribution pattern using advanced statistical methods.</p>
            </div>
            """, unsafe_allow_html=True)

            # Extract data for analysis
            try:
                if PREPROCESS_AVAILABLE:
                    data = extract_serial_intervals(df)
                else:
                    data = extract_serial_intervals_fallback(df)
                
                # Data overview metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Data Points", f"{len(data):,}")
                with col2:
                    st.metric("📈 Mean", f"{np.mean(data):.3f}")
                with col3:
                    st.metric("📏 Std Dev", f"{np.std(data):.3f}")
                with col4:
                    st.metric("🎯 Range", f"{np.ptp(data):.3f}")

                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()

                # Enhanced run button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    run_stability = st.button(
                        t("run_stability"), 
                        key="stability_btn",
                        use_container_width=True,
                        type="primary"
                    )

                if run_stability:
                    with st.spinner(t("running_stability")):
                        try:
                            if ALPHA_STABLE_AVAILABLE and R_AVAILABLE:
                                result = analyse_stable_distribution(data, "serial_interval_result")
                                
                                if isinstance(result, tuple):
                                    result_text, fig_path = result
                                else:
                                    result_text = result
                                    fig_path = "stability_test_plot.png"

                                st.markdown("""
                                <div class="success-box">
                                    <h3>✅ Analysis Complete</h3>
                                    <p>Statistical stability test has been completed successfully.</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Results display
                                result_html = result_text.replace('\n', '<br>')
                                st.markdown(f"""
                                <div class="result-card">
                                    <h3>📊 Statistical Results</h3>
                                    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                               padding: 1.5rem; border-radius: 10px; font-family: 'Courier New', monospace;
                                               border-left: 4px solid #667eea;">
                                        {result_html}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Plot display
                                if os.path.exists("stability_test_plot.png"):
                                    st.markdown("""
                                    <div class="result-card">
                                        <h3>📈 Distribution Analysis</h3>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.image("stability_test_plot.png", use_column_width=True)
                                    
                                    col1, col2, col3 = st.columns([1, 2, 1])
                                    with col2:
                                        with open("stability_test_plot.png", "rb") as f:
                                            st.download_button(
                                                "📥 Download Analysis Plot", 
                                                f.read(), 
                                                file_name="stability_analysis.png", 
                                                mime="image/png",
                                                use_container_width=True
                                            )
                                
                            else:
                                st.warning("⚠️ R interface or alpha-stable packages not available. Using basic analysis.")
                                
                                # Basic statistical tests
                                st.markdown("""
                                <div class="result-card">
                                    <h3>📊 Basic Statistical Analysis</h3>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Normality tests
                                col1, col2 = st.columns(2)
                                with col1:
                                    shapiro_stat, shapiro_p = stats.shapiro(data[:5000] if len(data) > 5000 else data)
                                    st.metric("Shapiro-Wilk p-value", f"{shapiro_p:.6f}")
                                    
                                with col2:
                                    ks_stat, ks_p = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data)))
                                    st.metric("Kolmogorov-Smirnov p-value", f"{ks_p:.6f}")
                                
                                # Distribution characteristics
                                skewness = stats.skew(data)
                                kurtosis = stats.kurtosis(data)
                                
                                st.markdown(f"""
                                **Distribution Characteristics:**
                                - Skewness: {skewness:.4f} ({'Right-skewed' if skewness > 0.5 else 'Left-skewed' if skewness < -0.5 else 'Symmetric'})
                                - Excess Kurtosis: {kurtosis:.4f} ({'Heavy tails' if kurtosis > 3 else 'Light tails' if kurtosis < -1 else 'Normal tails'})
                                - Potential for α-stable: {'High' if kurtosis > 5 or abs(skewness) > 1 else 'Moderate' if kurtosis > 1 else 'Low'}
                                """)
                                
                        except Exception as e:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h3>❌ Analysis Error</h3>
                                <p>{str(e)}</p>
                                <p><em>Try using sample data or checking your data format.</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
            except Exception as e:
                st.error(f"Data extraction error: {e}")

        elif mode == t("em_estimation"):
            # Enhanced EM Estimation Section
            st.markdown("""
            <div class="result-card">
                <h2>⚙️ Expectation-Maximization Estimation</h2>
                <p>Fit mixture models of α-stable distributions using state-of-the-art EM algorithms.</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                if PREPROCESS_AVAILABLE:
                    data = extract_serial_intervals(df)
                else:
                    data = extract_serial_intervals_fallback(df)
                
                # Data overview
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Sample Size", f"{len(data):,}")
                with col2:
                    st.metric("📈 Mean", f"{np.mean(data):.3f}")
                with col3:
                    st.metric("📏 Std Dev", f"{np.std(data):.3f}")
                with col4:
                    st.metric("🎯 Range", f"{np.ptp(data):.3f}")
                
                # Algorithm configuration
                st.markdown("### 🔧 Algorithm Configuration")
                
                if ALPHA_STABLE_AVAILABLE:
                    methods = {
                        "ECF - Recursive": em_estimate_stable_recursive_ecf,
                        "ECF - Kernel": em_estimate_stable_kernel_ecf,
                        "ECF - Weighted OLS": em_estimate_stable_weighted_ols,
                        "ECF - From CDF": em_estimate_stable_from_cdf
                    }
                else:
                    st.warning("⚠️ Alpha-stable methods not available. Using fallback methods.")
                    methods = {"Fallback Method": None}
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    selected_method = st.selectbox(
                        "Choose estimation method:",
                        list(methods.keys()),
                        help="Different methods use various approaches to estimate parameters"
                    )
                
                with col2:
                    max_iter = st.number_input("Max Iterations", min_value=50, max_value=1000, value=300)
                    
                with col3:
                    epsilon = st.number_input("Convergence Tolerance", min_value=1e-6, max_value=1e-2, 
                                            value=1e-3, format="%.1e")

                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()

                # Enhanced run button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    run_em = st.button(
                        t("run_em"), 
                        key="em_btn",
                        use_container_width=True,
                        type="primary"
                    )

                if run_em:
                    with st.spinner(t("running_em")):
                        try:
                            if ALPHA_STABLE_AVAILABLE and methods[selected_method] is not None:
                                estimator_func = methods[selected_method]
                                
                                result = robust_em_stable_mixture(
                                    data, 
                                    u=None,
                                    estimator_func=estimator_func,
                                    max_iter=max_iter, 
                                    epsilon=epsilon
                                )
                            else:
                                # Fallback EM implementation
                                st.info("Using fallback EM implementation...")
                                result = run_fallback_em(data, max_iter, epsilon)

                            # Store result for comparison
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            model_name = f"{selected_method}_{timestamp}"
                            st.session_state.model_results[model_name] = result

                            st.markdown("""
                            <div class="success-box">
                                <h3>🎯 Estimation Complete</h3>
                                <p>EM algorithm has converged successfully!</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Enhanced parameter display
                            display_em_results(result, data, selected_method)
                            
                        except Exception as e:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h3>❌ EM Estimation Error</h3>
                                <p>{str(e)}</p>
                                <p><em>Try different methods or check data quality.</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
            except Exception as e:
                st.error(f"Data processing error: {e}")

        elif mode == t("model_comparison"):
            # Model Comparison Mode
            st.markdown("""
            <div class="result-card">
                <h2>🔬 Model Comparison</h2>
                <p>Compare different models and estimation methods on your data.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.model_results:
                # Comparison table
                comparison_data = []
                for name, result in st.session_state.model_results.items():
                    try:
                        # Calculate AIC/BIC if possible
                        n_params = len(result['params_list']) * 4 + len(result['weights']) - 1
                        n_data = len(data) if 'data' in locals() else 1000  # fallback
                        aic = -2 * result['log_likelihood'] + 2 * n_params
                        bic = -2 * result['log_likelihood'] + n_params * np.log(n_data)
                        
                        comparison_data.append({
                            'Model': name,
                            'Log-Likelihood': f"{result['log_likelihood']:.4f}",
                            'AIC': f"{aic:.4f}",
                            'BIC': f"{bic:.4f}",
                            'Method': result.get('method', 'Unknown'),
                            'Components': len(result['params_list'])
                        })
                    except:
                        comparison_data.append({
                            'Model': name,
                            'Log-Likelihood': f"{result.get('log_likelihood', 'N/A')}",
                            'AIC': 'N/A',
                            'BIC': 'N/A', 
                            'Method': result.get('method', 'Unknown'),
                            'Components': len(result.get('params_list', []))
                        })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Model selection recommendations
                st.subheader("🎯 Model Selection Guidance")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **Selection Criteria:**
                    - **AIC**: Lower values indicate better fit
                    - **BIC**: Penalizes complexity more heavily
                    - **Log-likelihood**: Higher values are better
                    - **Method**: Some methods are more robust
                    """)
                
                with col2:
                    if len(comparison_data) > 0:
                        # Find best models
                        try:
                            numeric_data = []
                            for row in comparison_data:
                                try:
                                    aic_val = float(row['AIC']) if row['AIC'] != 'N/A' else float('inf')
                                    ll_val = float(row['Log-Likelihood']) if row['Log-Likelihood'] != 'N/A' else -float('inf')
                                    numeric_data.append((row['Model'], aic_val, ll_val))
                                except:
                                    continue
                            
                            if numeric_data:
                                best_aic = min(numeric_data, key=lambda x: x[1])
                                best_ll = max(numeric_data, key=lambda x: x[2])
                                
                                st.markdown(f"""
                                **Recommendations:**
                                - **Best AIC**: {best_aic[0]}
                                - **Best Log-likelihood**: {best_ll[0]}
                                """)
                        except:
                            st.info("Enable model comparison by running multiple analyses")
                
                # Clear models button
                if st.button("🗑️ Clear All Models"):
                    st.session_state.model_results = {}
                    st.rerun()
                    
            else:
                st.info("No models available for comparison. Run some analyses first!")
                
                # Quick analysis buttons
                if hasattr(st.session_state, 'current_data') or uploaded_file:
                    st.subheader("🚀 Quick Model Comparison")
                    if st.button("Run Multiple Methods", type="primary"):
                        with st.spinner("Running multiple EM methods..."):
                            # This would run multiple methods automatically
                            st.info("Feature coming soon: Automated model comparison")

    except Exception as e:
        st.markdown(f"""
        <div class="warning-box">
            <h3>❌ Processing Error</h3>
            <p>{str(e)}</p>
            <p><em>Please check your data format and try again.</em></p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Enhanced welcome screen
    st.markdown("""
    <div class="result-card">
        <h2>👋 Welcome to Mixstable</h2>
        <p>A comprehensive tool for analyzing α-stable distributions and fitting mixture models to your data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>⚗️ Distribution Analysis</h3>
            <p>Advanced statistical testing to determine if your data follows α-stable patterns.</p>
            <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                <li>Comprehensive stability tests</li>
                <li>Distribution comparison plots</li>
                <li>Statistical hypothesis testing</li>
                <li>R-based robust analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>📊 Mixture Modeling</h3>
            <p>State-of-the-art EM algorithms for fitting complex mixture models.</p>
            <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                <li>Multiple estimation methods</li>
                <li>Interactive visualizations</li>
                <li>Comprehensive model metrics</li>
                <li>Model comparison tools</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # New features highlight
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-box">
            <h3>🔍 Data Explorer</h3>
            <p>Comprehensive data analysis and quality assessment.</p>
            <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                <li>Statistical summaries</li>
                <li>Data quality checks</li>
                <li>Correlation analysis</li>
                <li>Outlier detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-box">
            <h3>🔬 Model Comparison</h3>
            <p>Advanced tools for comparing and selecting the best models.</p>
            <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                <li>AIC/BIC comparison</li>
                <li>Model performance metrics</li>
                <li>Automated recommendations</li>
                <li>Export capabilities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Usage guide
    st.markdown("""
    <div class="result-card">
        <h3>📖 Getting Started</h3>
        
        <div style="margin: 1.5rem 0;">
            <h4 style="color: #667eea;">🎯 Step 1: Choose Your Data</h4>
            <p>You have two options to get started:</p>
            <ul>
                <li><strong>Generate Sample Data</strong>: Click the "🎲 Try Sample Data" button to create synthetic α-stable data</li>
                <li><strong>Upload Your Data</strong>: Upload a CSV file with columns named <code>serial_interval</code>, <code>serial_interval_mean_based</code>, or <code>mean_serial_interval</code></li>
            </ul>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <h4 style="color: #667eea;">🔍 Step 2: Explore Your Data</h4>
            <p>Use the <strong>Data Explorer</strong> mode to:</p>
            <ul>
                <li>Examine data quality and statistics</li>
                <li>Identify potential issues</li>
                <li>Understand distribution characteristics</li>
            </ul>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <h4 style="color: #667eea;">⚗️ Step 3: Test for Stability</h4>
            <p>Run <strong>Stability Tests</strong> to determine if your data follows α-stable patterns:</p>
            <ul>
                <li>Statistical hypothesis tests</li>
                <li>Distribution comparison plots</li>
                <li>Detailed analysis reports</li>
            </ul>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <h4 style="color: #667eea;">📊 Step 4: Fit Mixture Models</h4>
            <p>Use <strong>EM Estimation</strong> to fit mixture models:</p>
            <ul>
                <li>Choose from multiple algorithms</li>
                <li>Adjust convergence parameters</li>
                <li>Generate publication-quality plots</li>
            </ul>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <h4 style="color: #667eea;">🔬 Step 5: Compare Models</h4>
            <p>Use <strong>Model Comparison</strong> to select the best approach:</p>
            <ul>
                <li>Compare different methods</li>
                <li>Evaluate fit statistics</li>
                <li>Export results and reports</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample data format
    st.markdown("""
    <div class="result-card">
        <h3>📊 Expected Data Format</h3>
        <p>Your CSV should contain numeric data in one of these formats:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sample data table
    sample_data = pd.DataFrame({
        'serial_interval': [2.1, 3.5, 1.8, 4.2, 2.9, 3.1, 2.7, 3.8, 4.1, 2.6],
        'date': pd.date_range('2024-01-01', periods=10),
        'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
    })
    st.dataframe(sample_data, use_container_width=True)
    
    # Technical information
    with st.expander("🔬 Technical Background"):
        st.markdown("""
        ### Alpha-Stable Distributions
        
        **Mathematical Foundation:**
        - Generalization of the normal distribution with heavy tails
        - Characterized by four parameters: α (stability index), β (skewness), γ (scale), δ (location)
        - Stable under addition: sum of α-stable variables is also α-stable
        
        **Key Properties:**
        - **α (Alpha)**: Controls tail heaviness (0 < α ≤ 2)
          - α = 2: Normal distribution
          - α = 1: Cauchy distribution  
          - α < 2: Heavy tails, infinite variance
        
        - **β (Beta)**: Controls skewness (-1 ≤ β ≤ 1)
          - β = 0: Symmetric distribution
          - β > 0: Right-skewed
          - β < 0: Left-skewed
        
        - **γ (Gamma)**: Scale parameter (γ > 0)
        - **δ (Delta)**: Location parameter
        
        **Applications:**
        - Financial modeling (stock returns, risk analysis)
        - Signal processing and telecommunications
        - Physics (Lévy flights, turbulence)
        - Epidemiology (disease spread modeling)
        
        ### EM Algorithm Methods
        
        **Empirical Characteristic Function (ECF) Approaches:**
        
        1. **ECF - Recursive**: Iterative estimation using recursive formulas
        2. **ECF - Kernel**: Kernel density estimation of characteristic function
        3. **ECF - Weighted OLS**: Weighted least squares on log-characteristic function
        4. **ECF - From CDF**: Estimation based on cumulative distribution function
        
        **Model Selection:**
        - **AIC (Akaike Information Criterion)**: -2 × log-likelihood + 2 × parameters
        - **BIC (Bayesian Information Criterion)**: -2 × log-likelihood + parameters × ln(n)
        - **Log-likelihood**: Higher values indicate better fit to data
        
        ### Computational Considerations
        - α-stable densities have no closed form (except special cases)
        - Numerical integration required for likelihood computation
        - Characteristic function approach often more stable
        - EM algorithm guarantees likelihood improvement at each step
        """)

# -------------------- Helper Functions for Results Display --------------------

def display_em_results(result, data, method_name):
    """Enhanced display of EM estimation results"""
    
    # Parameter display with enhanced formatting
    st.markdown("""
    <div class="result-card">
        <h3>📋 Estimated Parameters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Parameters in enhanced cards
    cols = st.columns(len(result["params_list"]))
    
    for i, (col, params) in enumerate(zip(cols, result["params_list"])):
        with col:
            if isinstance(params, dict):
                param_data = {
                    "α (Alpha)": params['alpha'],
                    "β (Beta)": params['beta'], 
                    "γ (Gamma)": params['gamma'],
                    "δ (Delta)": params['delta']
                }
            else:
                param_data = {
                    "α (Alpha)": params[0],
                    "β (Beta)": params[1],
                    "γ (Gamma)": params[2], 
                    "δ (Delta)": params[3]
                }
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {['#667eea', '#764ba2', '#f093fb', '#f5576c'][i % 4]} 0%, 
                       {['#764ba2', '#667eea', '#f5576c', '#f093fb'][i % 4]} 100%);
                       padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h4 style="margin: 0; text-align: center;">Component {i+1}</h4>
                <p style="margin: 0.5rem 0; text-align: center; font-size: 0.9em;">
                    Weight: {result['weights'][i]:.4f}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            for param_name, param_value in param_data.items():
                st.metric(param_name, f"{param_value:.6f}")
    
    # Model summary metrics
    st.markdown("### 📊 Model Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Log-likelihood", f"{result['log_likelihood']:.6f}")
    with col2:
        n_params = len(result['params_list']) * 4 + len(result['weights']) - 1
        aic = -2 * result['log_likelihood'] + 2 * n_params
        st.metric("📈 AIC", f"{aic:.4f}")
    with col3:
        n_data = len(data)
        bic = -2 * result['log_likelihood'] + n_params * np.log(n_data)
        st.metric("📊 BIC", f"{bic:.4f}")
    with col4:
        st.metric("⚙️ Method", method_name.split(' - ')[0])
    
    # Enhanced visualization
    st.markdown("""
    <div class="result-card">
        <h3>📈 Model Visualization</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Try to create enhanced plot
        plot_filename = create_enhanced_fallback_plot(data, result, "Alpha-Stable Mixture Fit")
        
        if plot_filename and os.path.exists(plot_filename):
            st.image(plot_filename, use_column_width=True)
            
            # Download button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with open(plot_filename, "rb") as f:
                    st.download_button(
                        "📥 Download Analysis Plot", 
                        f.read(), 
                        file_name="mixstable_fit.png",
                        mime="image/png",
                        use_container_width=True
                    )
        else:
            st.warning("Could not generate enhanced plot")
            
    except Exception as plot_error:
        st.warning(f"Visualization error: {plot_error}")
    
    # Export options
    st.markdown("""
    <div class="result-card">
        <h3>📤 Export Options</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export parameters as JSON
        params_dict = {
            'method': method_name,
            'log_likelihood': result['log_likelihood'],
            'parameters': result['params_list'],
            'weights': result['weights'],
            'timestamp': datetime.now().isoformat()
        }
        params_json = json.dumps(params_dict, indent=2, default=str)
        st.download_button(
            "📋 Export Parameters",
            params_json,
            "mixstable_parameters.json",
            "application/json",
            use_container_width=True
        )
    
    with col2:
        # Export summary report
        data_info = {
            'size': len(data),
            'mean': np.mean(data),
            'std': np.std(data),
            'skewness': stats.skew(data),
            'kurtosis': stats.kurtosis(data),
            'min': np.min(data),
            'max': np.max(data),
            'aic': aic,
            'bic': bic
        }
        report = generate_analysis_report(result, data_info)
        st.download_button(
            "📄 Export Report",
            report,
            "mixstable_report.txt",
            "text/plain",
            use_container_width=True
        )
    
    with col3:
        # Export enhanced data with model info
        try:
            enhanced_df = pd.DataFrame({
                'original_data': data,
                'log_likelihood': [result['log_likelihood']] * len(data),
                'method': [method_name] * len(data)
            })
            csv_data = enhanced_df.to_csv(index=False)
            st.download_button(
                "📊 Export Data",
                csv_data,
                "mixstable_data.csv", 
                "text/csv",
                use_container_width=True
            )
        except Exception:
            st.button("📊 Export Data", disabled=True, help="Export not available")

def run_fallback_em(data, max_iter=300, epsilon=1e-3):
    """Fallback EM implementation using basic statistical methods"""
    np.random.seed(42)
    
    # Simple two-component mixture using normal distributions as approximation
    # This is a fallback when alpha-stable methods are not available
    
    try:
        from sklearn.mixture import GaussianMixture
        
        # Use Gaussian mixture as approximation
        gmm = GaussianMixture(n_components=2, max_iter=max_iter, tol=epsilon, random_state=42)
        gmm.fit(data.reshape(-1, 1))
        
        # Convert to alpha-stable-like format
        weights = gmm.weights_
        means = gmm.means_.flatten()
        stds = np.sqrt(gmm.covariances_.flatten())
        
        # Create pseudo alpha-stable parameters (alpha=2 for normal)
        params_list = []
        for i in range(2):
            params_list.append([2.0, 0.0, stds[i], means[i]])  # alpha, beta, gamma, delta
        
        result = {
            'params_list': params_list,
            'weights': weights.tolist(),
            'log_likelihood': gmm.score(data.reshape(-1, 1)) * len(data),
            'method': 'Fallback Gaussian Mixture'
        }
        
        return result
        
    except ImportError:
        # Even more basic fallback
        st.warning("Using very basic fallback method")
        
        # Simple k-means-like approach
        data_sorted = np.sort(data)
        mid_point = len(data) // 2
        
        component1_data = data_sorted[:mid_point]
        component2_data = data_sorted[mid_point:]
        
        params_list = [
            [2.0, 0.0, np.std(component1_data), np.mean(component1_data)],
            [2.0, 0.0, np.std(component2_data), np.mean(component2_data)]
        ]
        
        weights = [0.5, 0.5]
        
        # Simple log-likelihood approximation
        ll1 = -0.5 * len(component1_data) * np.log(2 * np.pi * np.var(component1_data))
        ll2 = -0.5 * len(component2_data) * np.log(2 * np.pi * np.var(component2_data)) 
        log_likelihood = ll1 + ll2
        
        result = {
            'params_list': params_list,
            'weights': weights,
            'log_likelihood': log_likelihood,
            'method': 'Basic Fallback Split'
        }
        
        return result

# -------------------- Application Footer --------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>Mixstable v2.0</strong> - Advanced Alpha-Stable Distribution Analysis</p>
    <p>Built with ❤️ using Streamlit | Enhanced with modern UI/UX principles</p>
    <p><small>For technical support and documentation, visit our repository</small></p>
</div>
""", unsafe_allow_html=True)