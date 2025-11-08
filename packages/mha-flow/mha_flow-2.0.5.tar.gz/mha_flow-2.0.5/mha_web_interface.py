"""
MHA Analysis Dashboard - Redesigned Interface
=============================================

A guided, intuitive interface for analyzing metaheuristic algorithms.

Features:
- Multi-page navigation (Dashboard Home, New Experiment, Results History)
- Guided 3-step workflow for new experiments
- Live progress with algorithm cards
- Browser-based session persistence
- Clean, professional design with progressive disclosure
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import time
import contextlib  # <-- ADD THIS IMPORT

# Your wakepy import remains the same
try:
    from wakepy import keep
    WAKEPY_AVAILABLE = True
except ImportError:
    WAKEPY_AVAILABLE = False
    print("⚠️ wakepy not installed. Sleep prevention disabled.")
    
# Import helper modules
from mha_comparison_toolbox import MHAComparisonToolbox
from mha_toolbox.enhanced_runner import run_comparison_with_live_progress
from mha_toolbox.persistent_state import PersistentStateManager
from mha_toolbox.enhanced_session_manager import EnhancedSessionManager
from mha_toolbox.results_manager import ResultsManager

def toggle_algorithm_selection(algorithm_name):
    """Callback to toggle algorithm selection."""
    if algorithm_name in st.session_state.selected_algorithms:
        st.session_state.selected_algorithms.remove(algorithm_name)
    else:
        st.session_state.selected_algorithms.append(algorithm_name)
    # FIXED: Remove st.rerun() - Streamlit auto-reruns after callback

# Page configuration
st.set_page_config(
    page_title="MHA Analysis Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, professional design
st.markdown("""
<style>
    /* ============================================= */
    /* 1. GLOBAL STYLES & ANIMATIONS                */
    /* ============================================= */
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Smooth fade-in animation */
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(20px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes slideIn {
        from { 
            transform: translateX(-20px); 
            opacity: 0; 
        }
        to { 
            transform: translateX(0); 
            opacity: 1; 
        }
    }
    
    @keyframes pulse {
        0%, 100% { 
            opacity: 1; 
        }
        50% { 
            opacity: 0.6; 
        }
    }
    
    @keyframes spin {
        0% { 
            transform: rotate(0deg); 
        }
        100% { 
            transform: rotate(360deg); 
        }
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Main container styling */
    .main {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* ============================================= */
    /* 2. HEADER & BRANDING                         */
    /* ============================================= */
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: fadeIn 0.8s ease-in;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 3s ease-in-out infinite;
    }
    
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    /* ============================================= */
    /* 3. INFO CARDS (GUIDE & ACTIVITY)             */
    /* ============================================= */
    
    .info-card {
        background: linear-gradient(135deg, #2d2d3a 0%, #1e1e28 100%);
        border: 1px solid #444;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        animation: slideIn 0.6s ease-out;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .info-card h4 {
        color: #FAFAFA;
        margin-bottom: 1.2rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .info-card ol, .info-card ul {
        padding-left: 20px;
        color: #ccc;
        line-height: 1.8;
    }
    
    .info-card li {
        margin-bottom: 0.8rem;
        transition: color 0.2s;
    }
    
    .info-card li:hover {
        color: #fff;
    }
    
    .recent-activity-item {
        font-size: 0.95rem;
        color: #ccc;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        border-radius: 5px;
        transition: all 0.2s;
    }
    
    .recent-activity-item:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #fff;
        transform: translateX(5px);
    }
        .step-box {
        display: flex;
        align-items: center;
        background: rgba(102, 126, 234, 0.1);
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 3px solid #667eea;
        transition: background-color 0.3s;
    }
    
    .step-box:hover {
        background: rgba(102, 126, 234, 0.2);
    }
    
    .step-box-number {
        font-size: 1.2rem;
        font-weight: 700;
        color: #667eea;
        margin-right: 1rem;
        min-width: 20px; /* Aligns the text nicely */
        text-align: center;
    }
    
    .step-box-text {
        color: #ccc;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    /* ============================================= */
    /* 4. STATISTICS CARDS                          */
    /* ============================================= */
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        animation: fadeIn 0.8s ease-in;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stat-card:hover::before {
        left: 100%;
    }
    
    .stat-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    .stat-card-icon {
        font-size: 2.8em;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    
    .stat-card-value {
        font-size: 2.2em;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }
    
    .stat-card-label {
        color: #f0f0f0;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* ============================================= */
    /* 5. ALGORITHM CARDS                           */
    /* ============================================= */
    
    .algorithm-card {
        background: linear-gradient(135deg, #2d2d3a 0%, #1e1e28 100%);
        border-left: 4px solid #667eea;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        animation: slideIn 0.5s ease-out;
    }
    
    .algorithm-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .algorithm-card-pending {
        border-left-color: #888;
        opacity: 0.7;
    }
    
    .algorithm-card-running {
        border-left-color: #ffa500;
        background: linear-gradient(135deg, #2d2d3a 0%, #3a2d1e 100%);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .algorithm-card-completed {
        border-left-color: #43e97b;
        background: linear-gradient(135deg, #2d2d3a 0%, #1e3a2d 100%);
    }
    
    .algorithm-card-failed {
        border-left-color: #dc3545;
        background: linear-gradient(135deg, #2d2d3a 0%, #3a1e1e 100%);
    }
    
    /* Spinner animation for running algorithms */
    .spinner-emoji {
        display: inline-block;
        animation: spin 2s linear infinite;
    }
    
    /* ============================================= */
    /* 6. BUTTONS (ENHANCED STYLING)                */
    /* ============================================= */
    
    /* All buttons base styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    /* Hover effect with ripple */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        transform: translate(-50%, -50%);
        transition: width 0.5s, height 0.5s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Primary button (RED) - type="primary" */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        color: white;
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #e04555 0%, #d875e3 100%);
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
    }
    
    /* Secondary button (DEFAULT) */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8f 100%);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Custom blue button wrapper */
    .custom-blue-button-wrapper .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
    }
    
    .custom-blue-button-wrapper .stButton > button:hover {
        background: linear-gradient(135deg, #3a8fd9 0%, #00d4e6 100%);
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4);
    }
    
    /* ============================================= */
    /* 7. TABS STYLING                              */
    /* ============================================= */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(102, 126, 234, 0.1);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
        color: white;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    
    /* ============================================= */
    /* 8. EXPANDER STYLING                          */
    /* ============================================= */
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 8px;
        font-weight: 600;
        padding: 1rem;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border-color: #667eea;
        transform: translateX(5px);
    }
    
    .streamlit-expanderContent {
        background-color: rgba(0,0,0,0.1);
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        border: 1px solid #333;
        border-top: none;
    }
    
    /* ============================================= */
    /* 9. DATAFRAME STYLING                         */
    /* ============================================= */
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: 10px;
    }
    
    /* ============================================= */
    /* 10. METRIC CARDS                             */
    /* ============================================= */
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid #444;
        border-radius: 10px;
        padding: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    div[data-testid="metric-container"] label {
        font-weight: 600;
        color: #ccc;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #fff;
    }
    
    /* ============================================= */
    /* 11. PROGRESS BAR                             */
    /* ============================================= */
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .stProgress > div > div {
        background-color: rgba(102, 126, 234, 0.2);
        border-radius: 10px;
    }
    
    /* ============================================= */
    /* 12. SELECTBOX & INPUT FIELDS                 */
    /* ============================================= */
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div {
        border-radius: 8px;
        border: 1px solid #444;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover,
    .stTextInput > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within,
    .stTextInput > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
    }
    
    /* ============================================= */
    /* 13. CHECKBOX & RADIO STYLING                 */
    /* ============================================= */
    
    .stCheckbox {
        transition: all 0.2s ease;
    }
    
    .stCheckbox:hover {
        transform: scale(1.05);
    }
    
    .stRadio > div {
        gap: 1rem;
    }
    
    .stRadio > div > label {
        background: rgba(102, 126, 234, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .stRadio > div > label:hover {
        background: rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    /* ============================================= */
    /* 14. SLIDER STYLING                           */
    /* ============================================= */
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSlider > div > div > div {
        background-color: rgba(102, 126, 234, 0.2);
    }
    
    /* ============================================= */
    /* 15. FILE UPLOADER                            */
    /* ============================================= */
    
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        transition: all 0.3s ease;
        background: rgba(102, 126, 234, 0.05);
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.1);
        transform: scale(1.02);
    }
    
    /* ============================================= */
    /* 16. ALERTS & MESSAGES                        */
    /* ============================================= */
    
    .stAlert {
        border-radius: 10px;
        border-left-width: 4px;
        animation: slideIn 0.5s ease-out;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Success */
    .stSuccess {
        background: linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.1) 100%);
        border-left-color: #43e97b;
    }
    
    /* Info */
    .stInfo {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%);
        border-left-color: #4facfe;
    }
    
    /* Warning */
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1) 0%, rgba(255, 200, 0, 0.1) 100%);
        border-left-color: #ffa500;
    }
    
    /* Error */
    .stError {
        background: linear-gradient(135deg, rgba(245, 87, 108, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
        border-left-color: #f5576c;
    }
    
    /* ============================================= */
    /* 17. SIDEBAR STYLING                          */
    /* ============================================= */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e28 0%, #2d2d3a 100%);
        border-right: 1px solid #444;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #667eea;
        font-weight: 700;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* ============================================= */
    /* 18. PLOTLY CHART CONTAINER                   */
    /* ============================================= */
    
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .js-plotly-plot:hover {
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    /* ============================================= */
    /* 19. CATEGORY CARDS (ALGORITHM SHOWCASE)      */
    /* ============================================= */
    
    .category-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid;
        transition: all 0.3s ease;
        cursor: pointer;
        animation: fadeIn 0.8s ease-in;
    }
    
    .category-card:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* ============================================= */
    /* 20. SCROLLBAR STYLING                        */
    /* ============================================= */
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e1e28;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8f 100%);
    }
    
    /* ============================================= */
    /* 21. LOADING SPINNER                          */
    /* ============================================= */
    
    .stSpinner > div {
        border-top-color: #667eea;
        animation: spin 1s linear infinite;
    }
    
    /* ============================================= */
    /* 22. CONTAINER BORDERS                        */
    /* ============================================= */
    
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border-radius: 10px;
    }
    
    /* ============================================= */
    /* 23. DOWNLOAD BUTTON                          */
    /* ============================================= */
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #32d46b 0%, #28e4c2 100%);
        box-shadow: 0 6px 20px rgba(67, 233, 123, 0.4);
        transform: translateY(-2px);
    }
    
    /* ============================================= */
    /* 24. RESPONSIVE ADJUSTMENTS                   */
    /* ============================================= */
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 0.95rem;
        }
        
        .stat-card-value {
            font-size: 1.8em;
        }
        
        .stButton > button {
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
        }
    }
    
    /* ============================================= */
    /* 25. STEP INDICATOR                           */
    /* ============================================= */
    
    .step-indicator {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        text-align: center;
        line-height: 35px;
        font-weight: 700;
        margin-right: 10px;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.4);
    }
    
    /* ============================================= */
    /* 26. LINK STYLING                             */
    /* ============================================= */
    
    a {
        color: #667eea;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    /* ============================================= */
    /* 27. CODE BLOCK STYLING                       */
    /* ============================================= */
    
    code {
        background: rgba(102, 126, 234, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
        color: #667eea;
        font-family: 'Courier New', monospace;
    }
    
    pre {
        background: rgba(0,0,0,0.2);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #444;
    }
    
    /* ============================================= */
    /* 28. FOOTER                                   */
    /* ============================================= */
    
    footer {
        text-align: center;
        padding: 2rem;
        color: #888;
        border-top: 1px solid #444;
        margin-top: 3rem;
    }
    
    footer a {
        color: #667eea;
    }
    
    /* ============================================= */
    /* 29. TOOLTIP STYLING                          */
    /* ============================================= */
    
    [data-testid="stTooltipIcon"] {
        color: #667eea;
    }
    
    /* ============================================= */
    /* 30. CONTAINER WITH BORDER                    */
    /* ============================================= */
    
    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    [data-testid="column"] {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize managers
@st.cache_resource
def get_safe_managers():
    """Initialize manager instances that don't use widgets and are safe to cache."""
    return {
        'session': EnhancedSessionManager(),
        'results': ResultsManager()
    }

# Initialize the persistent state manager (with cookies) separately.
# This ensures it's created only once per session but NOT inside a cached function.
if 'persistent_manager' not in st.session_state:
    st.session_state.persistent_manager = PersistentStateManager()

# Get the cached managers
safe_managers = get_safe_managers()

# Combine all managers into a single dictionary for easy access throughout the app
managers = {
    'persistent': st.session_state.persistent_manager,
    'session': safe_managers['session'],
    'results': safe_managers['results']
}

# Initialize session state
# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard_home'
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'selected_algorithms' not in st.session_state:
    st.session_state.selected_algorithms = []
if 'experiment_results' not in st.session_state:
    st.session_state.experiment_results = {}
if 'selected_for_deletion' not in st.session_state: # <-- ADD THIS NEW LINE
    st.session_state.selected_for_deletion = []      # <-- AND THIS ONE

def main():
    """Main application entry point"""
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(" 📍 Navigation")
        
        # Navigation buttons
        if st.button("🏠 Dashboard Home", use_container_width=True, 
                    type="primary" if st.session_state.current_page == 'dashboard_home' else "secondary"):
            st.session_state.current_page = 'dashboard_home'
            st.rerun()
        
        if st.button("🔬 New Experiment", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'new_experiment' else "secondary"):
            st.session_state.current_page = 'new_experiment'
            st.rerun()
        
        if st.button("📚 Results History", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'results_history' else "secondary"):
            st.session_state.current_page = 'results_history'
            st.rerun()
        if st.button("ℹ️ About", use_container_width=True, type="primary" if st.session_state.current_page == 'about' else "secondary"):
            st.session_state.current_page = 'about'
            st.rerun()

        st.markdown("---")
        st.markdown("### Information")
        st.info("""
        **MHA Toolbox**
        
        Analyze and compare 37+ metaheuristic algorithms with intuitive workflows and real-time progress tracking.
        """)
    
    # Route to appropriate page
    if st.session_state.current_page == 'dashboard_home':
        show_dashboard_home()
    elif st.session_state.current_page == 'new_experiment':
        show_new_experiment()
    elif st.session_state.current_page == 'results_history':
        show_results_history()
    elif st.session_state.current_page == 'about':
        show_about_page()

    
def show_dashboard_home():
    """
    ## MODIFIED ## - The "How to Get Started" section now uses styled "step boxes" instead of a numbered list.
    ## UPDATED ## - The "Quick Actions" button section at the bottom has been removed to reduce redundancy.
    """
    # Main Header with Gradient
    st.markdown("""
    <div class="main-header">
        <h1>🧬 MHA Analysis Dashboard</h1>
        <p>Professional Platform for Metaheuristic Algorithm Comparison and Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # === STATISTICS OVERVIEW SECTION ===
    st.markdown("### 📊 Quick Statistics")
    
    all_experiments = managers['results'].list_all_experiments()
    total_experiments = len(all_experiments)
    
    total_algorithms_run = 0
    datasets_used = set()
    for exp in all_experiments:
        results = managers['results'].load_experiment_results(exp['dataset_name'], exp['session_id'])
        if results:
            total_algorithms_run += len(results)
            datasets_used.add(exp['dataset_name'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-icon">🧪</div>
            <div class="stat-card-value">{total_experiments}</div>
            <div class="stat-card-label">Total Experiments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-icon">🔬</div>
            <div class="stat-card-value">{total_algorithms_run}</div>
            <div class="stat-card-label">Algorithms Run</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-icon">📁</div>
            <div class="stat-card-value">{len(datasets_used)}</div>
            <div class="stat-card-label">Datasets Used</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-icon">🧬</div>
            <div class="stat-card-value">37+</div>
            <div class="stat-card-label">Available Algorithms</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # === INTERACTIVE GUIDE & ACTIVITY SECTION ===
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>📋 How to Get Started</h4>
            <div class="step-box">
                <div class="step-box-number">1.</div>
                <div class="step-box-text">Navigate to the <b>New Experiment</b> page from the sidebar.</div>
            </div>
            <div class="step-box">
                <div class="step-box-number">2.</div>
                <div class="step-box-text">Select a sample dataset or upload your own CSV file.</div>
            </div>
            <div class="step-box">
                <div class="step-box-number">3.</div>
                <div class="step-box-text">Choose the algorithms you wish to compare.</div>
            </div>
            <div class="step-box">
                <div class="step-box-number">4.</div>
                <div class="step-box-text">Configure parameters and click "Start Comparison" to run!</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="info-card"><h4>🕒 Recent Activity</h4>', unsafe_allow_html=True)
        
        recent_experiments = managers['results'].list_all_experiments()[:4]
        
        if not recent_experiments:
            st.info("No recent activity found. Run an experiment to get started!")
        else:
            for exp in recent_experiments:
                date = datetime.fromisoformat(exp['modified_at']).strftime('%Y-%m-%d %H:%M')
                st.markdown(f"""
                <div class="recent-activity-item">
                    <div>📊 <strong>{exp['dataset_name']}</strong></div>
                    <div style='font-size: 0.85em; color: #999;'>{date}</div>
                </div>
                """, unsafe_allow_html=True)
        
def show_new_experiment():
    """
    Displays the guided 3-step workflow for setting up a new experiment.
    """
    st.markdown("""
    <div class="main-header">
        <h1>🔬 New Experiment</h1>
        <p>Follow the steps below to configure and run your analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    # Create the tabbed interface for the 3 steps
    tab1, tab2, tab3 = st.tabs([
        "**Step 1: Select Dataset**", 
        "**Step 2: Choose Algorithms**", 
        "**Step 3: Configure & Run**"
    ])

    # Populate each tab with its corresponding function
    with tab1:
        show_dataset_selection_tab()
    
    with tab2:
        show_algorithm_selection_tab()
        
    with tab3:
        show_configuration_and_run_tab()

def show_dataset_selection_tab():
    """
    ## MODIFIED ## - Highlights the button of the selected dataset.
    """
    
    st.markdown("### <span class='step-indicator'>1</span> Select Your Dataset", unsafe_allow_html=True)
    
    # Radio button to choose between the two workflows
    data_source = st.radio(
        "Choose your data source:",
        ["📦 Sample Datasets", "📤 Upload Custom CSV"],
        horizontal=True,
        label_visibility="collapsed" # Hides the label to save space
    )
    
    # --- Workflow 1: Sample Datasets ---
    if data_source == "📦 Sample Datasets":
        st.markdown("#### Available Sample Datasets")
        
        # Define the sample datasets with their properties
        datasets = [
            {"name": "Breast Cancer", "samples": 569, "features": 30, "type": "Classification"},
            {"name": "Wine", "samples": 178, "features": 13, "type": "Classification"},
            {"name": "Iris", "samples": 150, "features": 4, "type": "Classification"},
            {"name": "Digits", "samples": 1797, "features": 64, "type": "Classification"},
            {"name": "California Housing", "samples": 20640, "features": 8, "type": "Regression"},
            {"name": "Diabetes", "samples": 442, "features": 10, "type": "Regression"}
        ]
        
        # Create a 3-column grid for the cards
        cols = st.columns(3)
        
        for i, dataset in enumerate(datasets):
            with cols[i % 3]:
                # Use a container to group the card and button
                with st.container(border=True):
                    # Display dataset info in a card format
                    st.markdown(f"""
                        <h4>{dataset['name']}</h4>
                        <p><strong>Samples:</strong> {dataset['samples']} | <strong>Features:</strong> {dataset['features']}<br>
                        <strong>Type:</strong> {dataset['type']}</p>
                    """, unsafe_allow_html=True)
                    
                    # --- THIS IS THE CHANGED LOGIC ---
                    
                    # 1. Check if this card's dataset is the selected one
                    is_selected = (st.session_state.selected_dataset == dataset['name'])
                    
                    # 2. Set the button type based on selection
                    button_type = "primary" if is_selected else "secondary"
                    
                    # 3. Use the 'type' parameter in the st.button
                    if st.button(f"Select {dataset['name']}", 
                                 key=f"select_{dataset['name']}", 
                                 use_container_width=True, 
                                 type=button_type): # <-- THIS IS THE FIX
                        
                        st.session_state.selected_dataset = dataset['name']
                        st.session_state.dataset_type = 'sample'
                        st.rerun() # Rerun to update the UI state immediately

    # --- Workflow 2: Custom CSV Upload ---
    else:
        # (Your existing code for this section is fine)
        st.markdown("#### Upload Your Dataset")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                with st.expander("📋 Dataset Preview"):
                    st.dataframe(df.head(10))
                    st.info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                
                target_col = st.selectbox("Select the target (output) column:", df.columns)
                
                if st.button("Confirm Dataset", type="primary"):
                    st.session_state.selected_dataset = uploaded_file.name
                    st.session_state.dataset_type = 'uploaded'
                    st.session_state.uploaded_data = df
                    st.session_state.target_column = target_col
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading or processing the CSV file: {e}")
    
    # --- Persistent Summary at the bottom of the tab ---
    if st.session_state.selected_dataset:
        st.markdown("---")
        st.success(f"✅ **Currently Selected**: {st.session_state.selected_dataset}")


import streamlit as st

def show_algorithm_selection_tab():
    """Tab 2: Algorithm Selection with Custom Interface"""

    # -------------------------------------------------
    # 2. STEP TITLE
    # -------------------------------------------------
    st.markdown("### <span class='step-indicator'>2</span> Choose Algorithms to Compare", unsafe_allow_html=True)

    # -------------------------------------------------
    # 3. SELECTION SUMMARY (GREEN) - MOVED TO TOP
    # -------------------------------------------------
    if st.session_state.selected_algorithms:
        st.success(f"**{len(st.session_state.selected_algorithms)} algorithms selected**")

    # -------------------------------------------------
    # 4. DATASET GUARD
    # -------------------------------------------------
    if not st.session_state.selected_dataset:
        st.warning("Please select a dataset first in **Step 1**")
        return

    # -------------------------------------------------
    # 5. ALGORITHM CATALOGUE
    # -------------------------------------------------
    algorithm_groups = {
        "Swarm Intelligence": ["pso", "alo", "woa", "gwo", "ssa", "mrfo", "spider"],
        "Evolutionary": ["ga", "de", "eo", "innov"],
        "Physics-Based": ["sca", "sa", "hgso", "wca", "wdo"],
        "Bio-Inspired": ["ba", "fa", "csa", "coa", "msa"],
        "Novel": ["ao", "aoa", "cgo", "fbi", "gbo", "ica", "pfa", "qsa", "sma", "spbo", "tso", "vcs", "vns"]
    }

    # -------------------------------------------------
    # 6. SEARCH + MASTER BUTTONS (YOUR LOGIC - UNCHANGED)
    # -------------------------------------------------
    search = st.text_input("Search algorithms", placeholder="Type to filter...")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Select All", use_container_width=True, key="select_all_btn"):
            all_algs = [alg for group in algorithm_groups.values() for alg in group]
            st.session_state.selected_algorithms = all_algs.copy()
            st.rerun()

    with col2:
        if st.button("Select Recommended (Top 10)", use_container_width=True, key="select_recommended_btn"):
            st.session_state.selected_algorithms = ["pso", "gwo", "sca", "woa", "alo", "ga", "de", "ssa", "fa", "ba"]
            st.rerun()

    with col3:
        if st.button("Clear Selection", use_container_width=True, key="clear_selection_btn"):
            st.session_state.selected_algorithms = []
            st.rerun()

    st.markdown("---")

    # -------------------------------------------------
    # 7. EXPANDABLE GROUPS WITH CHECKBOXES
    # -------------------------------------------------
    for group_name, algorithms in algorithm_groups.items():
        filtered = [alg for alg in algorithms if not search or search.lower() in alg.lower()]
        if not filtered:
            continue

        # --- THIS IS THE ONLY CHANGE ---
        # I removed `expanded=False` from this line.
        # This lets Streamlit remember if it was open or closed.
        with st.expander(f"{group_name} ({len(algorithms)} algorithms)"):
        # ---------------------------------
            cols = st.columns(4)
            for i, alg in enumerate(filtered):
                with cols[i % 4]:
                    is_selected = alg in st.session_state.selected_algorithms
                    
                    # --- YOUR LOGIC - UNCHANGED ---
                    # Using a dynamic key is important for your logic
                    key = f"alg_checkbox_{alg}_{is_selected}" 

                    checked = st.checkbox(
                        alg.upper(),
                        value=is_selected,
                        key=key
                    )

                    # --- YOUR LOGIC - UNCHANGED ---
                    if checked and alg not in st.session_state.selected_algorithms:
                        st.session_state.selected_algorithms.append(alg)
                        st.rerun()
                    elif not checked and alg in st.session_state.selected_algorithms:
                        st.session_state.selected_algorithms.remove(alg)
                        st.rerun()

    # -------------------------------------------------
    # 8. BOTTOM: PROCEED MESSAGE (ONLY IF ALGORITHMS SELECTED)
    # -------------------------------------------------
    st.markdown("---")
    if st.session_state.selected_algorithms:
        st.info("Proceed to **Step 3: Configure & Run**")
    else:
        st.warning("No algorithms selected. Please select at least one algorithm.")


def show_configuration_and_run_tab():
    """
    Shows the configuration and run tab for a new experiment.
    """
    
    # This block for showing completed results remains the same
    if 'experiment_results' in st.session_state and st.session_state.experiment_results:
        st.success("✅ Experiment completed! View results below.")
        col_back, col_clear = st.columns([3, 1])
        with col_back:
            if st.button("🔄 New Run", use_container_width=True):
                if 'experiment_results' in st.session_state: del st.session_state.experiment_results
                st.rerun()
        with col_clear:
            if st.button("🗑️ Clear Results", use_container_width=True):
                if 'experiment_results' in st.session_state: del st.session_state.experiment_results
                st.rerun()
        show_results_dashboard(st.session_state.experiment_results)
        return

    st.markdown("### <span class='step-indicator'>3</span> Configure & Run Experiment", unsafe_allow_html=True)
    
    # Validation checks remain the same
    if not st.session_state.get('selected_dataset', False):
        st.warning("⚠️ Please select a dataset in **Step 1**")
        return
    if not st.session_state.get('selected_algorithms', []):
        st.warning("⚠️ Please select algorithms in **Step 2**")
        return
    
    # Experiment summary remains the same
    st.markdown("#### 📋 Experiment Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Dataset**: {st.session_state.selected_dataset}")
    with col2:
        st.info(f"**Algorithms**: {len(st.session_state.selected_algorithms)} selected")
    
    st.markdown("---")
    st.markdown("#### ⚙️ Parameters")
    
    preset = st.selectbox(
        "Parameter preset:",
        ["Demo (Fast)", "Standard", "Thorough", "Custom"],
        help="Pre-configured parameter sets for different needs"
    )
    
    if preset == "Demo (Fast)":
        max_iter, pop_size, n_runs = 20, 15, 2
        st.info("⚡ Fast demo settings for quick results")
    elif preset == "Standard":
        max_iter, pop_size, n_runs = 50, 25, 3
        st.info("⚖️ Balanced settings for good results")
    elif preset == "Thorough":
        max_iter, pop_size, n_runs = 100, 40, 5
        st.info("🎯 Comprehensive settings for best results")
    else: # Custom
        st.write("Custom Parameters:")
        col_ps, col_nr = st.columns(2)
        with col_ps:
            pop_size = st.slider("Population Size", 10, 100, 25, key="pop_size_slider")
        with col_nr:
            n_runs = st.slider("Number of Runs", 1, 10, 3, key="n_runs_slider")
        max_iter = st.slider("Max Iterations (full width)", 10, 200, 50, key="max_iter_slider")

    with st.expander("⚙️ Advanced Options"):
        task_type = st.selectbox(
            "Task Type:",
            ["feature_selection", "feature_optimization", "hyperparameter_tuning"],
            format_func=lambda x: {"feature_selection": "🔍 Feature Selection", "feature_optimization": "🎯 Feature Optimization", "hyperparameter_tuning": "⚙️ Hyperparameter Tuning"}[x]
        )
        save_results = st.checkbox("Auto-save results to history", value=True)
    
    st.markdown("---")
    
    if st.button("🚀 Start Comparison", type="primary", use_container_width=True):
        # Initialize all_results to None before calling the function
        all_results = None
        
        try:
            all_results = run_experiment_with_live_progress(
                max_iterations=max_iter,
                population_size=pop_size,
                n_runs=n_runs,
                task_type=task_type if 'task_type' in locals() else 'feature_selection',
            )
        except Exception as e:
            st.error(f"❌ An error occurred during the experiment: {str(e)}")
            st.exception(e)
            return
        
        # Only proceed if we got valid results
        if all_results and len(all_results) > 0:
            st.success("✅ Experiment completed successfully!")
            st.rerun()
        else:
            st.error("❌ Experiment failed to produce results. Please check the logs above.")


def run_experiment_with_live_progress(max_iterations, population_size, n_runs, 
                                     task_type='feature_selection'):
    """Run experiment with live progress and save results to history."""
    
    st.markdown("---")
    st.markdown("## 🚀 Running Experiment")
    
    X, y, dataset_name = load_dataset(
        st.session_state.selected_dataset,
        st.session_state.get('dataset_type', 'sample')
    )
    if X is None:
        st.error("Failed to load dataset")
        return None

    use_wakepy = st.session_state.get('keep_awake', True)
    if WAKEPY_AVAILABLE and use_wakepy:
        st.info("☕ **Keep-awake mode enabled** - Your system will stay active.")
        keep_awake_context = keep.running()
    else:
        keep_awake_context = contextlib.nullcontext()

    all_results = {}

    with keep_awake_context:
        # --- Simplified UI Placeholders ---
        completed_count = 0
        total_algorithms = len(st.session_state.selected_algorithms)
        progress_bar = st.progress(0, text="Starting experiment...")
        status_text = st.empty() # A single placeholder for status updates
        status_text.text("Queuing up algorithms...")

        cards_placeholder = st.empty()
        algorithm_states = {alg: {'status': 'pending'} for alg in st.session_state.selected_algorithms}
        
        with cards_placeholder.container():
            for alg_name, state in algorithm_states.items():
                show_algorithm_card(alg_name, state['status'])

        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        from mha_toolbox.enhanced_runner import run_comparison_with_live_progress as run_toolbox_comparison
        
        for update in run_toolbox_comparison(
            X, y, dataset_name, task_type,
            st.session_state.selected_algorithms,
            max_iterations, population_size, n_runs
        ):
            algorithm = update['algorithm']
            status = update['status']
            progress = update.get('progress', 0)
            
            # Update progress bar with descriptive text
            progress_text = f"Overall Progress ({completed_count + 1}/{total_algorithms})"
            progress_bar.progress(progress, text=progress_text)
            
            if algorithm in algorithm_states:
                if status == 'running':
                    status_text.text(f"🔄 Running {algorithm.upper()} [{update.get('iteration', '')}]...")
                    algorithm_states[algorithm]['status'] = 'running'
                
                elif status == 'completed' and 'result_data' in update:
                    status_text.text(f"✅ {algorithm.upper()} completed!")
                    all_results[algorithm] = update['result_data']
                    algorithm_states[algorithm]['status'] = 'completed'
                    algorithm_states[algorithm]['data'] = update['result_data']
                    completed_count += 1

                elif status == 'failed':
                    status_text.text(f"❌ {algorithm.upper()} failed: {update.get('error', 'Unknown error')}")
                    algorithm_states[algorithm]['status'] = 'failed'
                    algorithm_states[algorithm]['error'] = update.get('error')
                    completed_count += 1

            with cards_placeholder.container():
                for alg_name, state in algorithm_states.items():
                    show_algorithm_card(
                        alg_name, 
                        state['status'], 
                        result_data=state.get('data'), 
                        error=state.get('error')
                    )
            time.sleep(0.1)

    # Experiment completed
    progress_bar.progress(1.0, text="✅ Experiment Finished!")
    status_text.success("✅ All algorithms completed!")
    
    # Save results to history
    if all_results:
        with st.spinner("💾 Saving experiment results to history..."):
            save_path = managers['results'].save_experiment_results(
                results=all_results,
                dataset_name=dataset_name,
                session_id=session_id
            )
            if save_path:
                st.success(f"Results for session `{session_id}` saved to history.")
            else:
                st.error("Failed to save results to history.")
    
    # Store results in session state
    st.session_state.experiment_results = all_results
    
    return all_results


def show_algorithm_card(algorithm, status, result_data=None, error=None):
    """Display an algorithm card with status, including an animated emoji for 'running'."""
    
    card_class = f"algorithm-card algorithm-card-{status}"
    alg_display = algorithm.upper()
    
    with st.container():
        if status == 'pending':
            st.markdown(f"""
            <div class="{card_class}" style="border-left-color: #888;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style='font-size: 2.5em;'>⏳</div>
                    <div>
                        <h4>{alg_display}</h4>
                        <p style="color: #888; margin: 0;"><strong>Queued...</strong></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif status == 'running':
            # --- THIS IS THE CHANGE ---
            # Using the emoji with the spinner class instead of the GIF
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style='font-size: 2.5em;'>
                        <span class="spinner-emoji">⏳</span>
                    </div>
                    <div>
                        <h4>{alg_display}</h4>
                        <p style="color: #ffa500; margin: 0;"><strong>Running...</strong></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif status == 'completed' and result_data:
            stats = result_data.get('statistics', {})
            cols = st.columns([1, 2, 2, 2])
            with cols[0]:
                st.markdown(f"<div style='text-align: center; font-size: 2em; padding-top: 10px;'>✅</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{alg_display}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.metric("Best Fitness", f"{stats.get('best_fitness', 0):.6f}")
            with cols[2]:
                st.metric("Mean Fitness", f"{stats.get('mean_fitness', 0):.6f}")
            with cols[3]:
                st.metric("Execution Time", f"{stats.get('mean_time', 0):.2f}s")
        
        elif status == 'failed':
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style='font-size: 2.5em;'>❌</div>
                    <div>
                        <h4>{alg_display} - Failed</h4>
                        <p style="color: #dc3545; margin: 0;"><strong>Error:</strong> {error or 'Unknown error'}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def show_results_dashboard(results):
    """Display comprehensive results dashboard with icons and better styling."""
    
    st.markdown("## 🎯 Results Dashboard")
    
    # Summary metrics with icons
    col1, col2, col3, col4 = st.columns(4)
    
    best_alg = min(results.items(), key=lambda x: x[1]['statistics']['best_fitness'])
    fastest_alg = min(results.items(), key=lambda x: x[1]['statistics']['mean_time'])
    
    with col1:
        st.metric("🧬 Algorithms Tested", len(results))
    
    with col2:
        st.metric("🏆 Best Performer",  # <-- ADDED EMOJI
                 best_alg[0].upper(),
                 f"{best_alg[1]['statistics']['best_fitness']:.6f}")
    
    with col3:
        st.metric("⚡ Fastest",  # <-- ADDED EMOJI
                 fastest_alg[0].upper(),
                 f"{fastest_alg[1]['statistics']['mean_time']:.2f}s")
    
    with col4:
        avg_time = np.mean([r['statistics']['mean_time'] for r in results.values()])
        st.metric("⏱️ Avg Time", f"{avg_time:.2f}s") # <-- ADDED EMOJI
    
    # Tabbed results (This part is now handled by the new tab structure)
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Summary", "⚖️ Comparative Analysis", "🔄 Convergence Analysis", "💾 Export"])

    with tab1:
        show_results_summary(results)
    with tab2:
        show_comparative_analysis(results)
    with tab3:
        show_convergence_analysis(results)
    with tab4:
        show_export_options(results)


def show_results_summary(results):
    """Enhanced results summary with interactive visualizations"""
    
    st.markdown("### 📊 Performance Summary")
    
    # Create summary DataFrame
    summary_data = []
    for alg_name, result in results.items():
        stats = result['statistics']
        summary_data.append({
            'Algorithm': alg_name.upper(),
            'Best Fitness': stats['best_fitness'],
            'Mean Fitness': stats['mean_fitness'],
            'Std Dev': stats['std_fitness'],
            'Mean Time (s)': stats['mean_time'],
            'Runs': stats['total_runs']
        })
    df = pd.DataFrame(summary_data)
    
    # Highlight best performers
    def highlight_best(s):
        if s.name == 'Best Fitness':
            is_min = s == s.min()
            return ['background-color: #43e97b; color: white; font-weight: bold' if v else '' for v in is_min]
        elif s.name == 'Mean Time (s)':
            is_min = s == s.min()
            return ['background-color: #4facfe; color: white; font-weight: bold' if v else '' for v in is_min]
        return ['' for _ in s]
    
    styled_df = df.style.format({
        'Best Fitness': '{:.6f}',
        'Mean Fitness': '{:.6f}',
        'Std Dev': '{:.6f}',
        'Mean Time (s)': '{:.2f}'
    }).apply(highlight_best)
    
    st.dataframe(styled_df, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === INTERACTIVE CHARTS ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Performance Ranking")
        
        # Sort by mean fitness and create bar chart
        df_sorted = df.sort_values('Mean Fitness')
        
        fig_bar = px.bar(
            df_sorted,
            x='Mean Fitness',
            y='Algorithm',
            orientation='h',
            color='Mean Fitness',
            color_continuous_scale='RdYlGn_r',
            text='Mean Fitness',
            title="Algorithm Performance (Lower is Better)"
        )
        fig_bar.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig_bar.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True, theme=None)
    
    with col2:
        st.markdown("#### ⚡ Execution Time")
        
        # Sort by time and create bar chart
        df_time_sorted = df.sort_values('Mean Time (s)')
        
        fig_time = px.bar(
            df_time_sorted,
            x='Mean Time (s)',
            y='Algorithm',
            orientation='h',
            color='Mean Time (s)',
            color_continuous_scale='Blues',
            text='Mean Time (s)',
            title="Execution Time (Lower is Better)"
        )
        fig_time.update_traces(texttemplate='%{text:.2f}s', textposition='outside')
        fig_time.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_time, use_container_width=True, theme=None)
    
    # === PERFORMANCE DISTRIBUTION (MODIFIED TO BUBBLE/STRIP PLOT) ===
    st.markdown("#### 📊 Fitness Distribution Across Runs")

    # Prepare data in a long format for Plotly Express
    plot_data = []
    for alg_name, result in results.items():
        for run in result['runs']:
            plot_data.append({
                'Algorithm': alg_name.upper(),
                'Fitness': run['best_fitness']
            })

    # Create a strip plot, which is a scatter plot for distributions
    if plot_data:
        df_plot = pd.DataFrame(plot_data)
        fig_strip = px.strip(
            df_plot,
            x='Algorithm',
            y='Fitness',
            color='Algorithm',
            title="Fitness Distribution Across All Runs"
        )
        
        # Make the markers larger to look like bubbles
        fig_strip.update_traces(
            marker=dict(
                size=20,
                line=dict(width=1, color='DarkSlateGrey')
            )
        )

        fig_strip.update_layout(
            height=500,
            showlegend=False, # Legend is redundant since colors are tied to the x-axis
            yaxis_title="Best Fitness Value"
        )
        
        st.plotly_chart(fig_strip, use_container_width=True, theme=None)

def show_comparative_analysis(results):
    """
    ## MODIFIED ## - Added user-selectable chart types (Vertical Bar, Horizontal Bar, Scatter).
    - The user can now choose both the metric and the visualization style.
    """
    
    st.markdown("### ⚖️ Comparative Analysis")

    # --- Data Preparation (Unchanged) ---
    summary_data = []
    for alg_name, result in results.items():
        stats = result['statistics']
        summary_data.append({
            'Algorithm': alg_name.upper(),
            'Mean Fitness': stats['mean_fitness'],
            'Best Fitness': stats['best_fitness'], # Added for the new plotting option
            'Std Dev': stats['std_fitness'],
            'Mean Time (s)': stats['mean_time'],
            'Runs': stats['total_runs']
        })
    df = pd.DataFrame(summary_data)

    # --- NEW: Interactive Controls for Metric and Chart Type ---
    st.markdown("#### 📈 Interactive Performance Comparison")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        metric_to_plot = st.selectbox(
            "**Choose a metric to compare:**",
            ['Mean Fitness', 'Best Fitness', 'Mean Time (s)', 'Std Dev']
        )
    
    with col2:
        chart_type = st.radio(
            "**Select visualization type:**",
            ["Vertical Bar", "Horizontal Bar", "Scatter Plot"],
            horizontal=True
        )

    # --- Dynamic Plotting Logic ---
    is_lower_better = "Time" in metric_to_plot or "Fitness" in metric_to_plot
    
    # --- Chart Type 1: Vertical Bar Chart ---
    if chart_type == "Vertical Bar":
        chart_title = f"Algorithm Performance: {metric_to_plot}"
        fig = px.bar(
            df.sort_values(metric_to_plot, ascending=is_lower_better),
            x='Algorithm',
            y=metric_to_plot,
            color=metric_to_plot,
            color_continuous_scale='RdYlGn_r' if is_lower_better else 'RdYlGn',
            title=chart_title,
            text=metric_to_plot
        )
        fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')

    # --- Chart Type 2: Horizontal Bar Chart ---
    elif chart_type == "Horizontal Bar":
        chart_title = f"Algorithm Performance: {metric_to_plot}"
        fig = px.bar(
            df.sort_values(metric_to_plot, ascending=True), # Horizontal bars look better sorted ascending
            x=metric_to_plot,
            y='Algorithm',
            orientation='h',
            color=metric_to_plot,
            color_continuous_scale='RdYlGn_r' if is_lower_better else 'RdYlGn',
            title=chart_title,
            text=metric_to_plot
        )
        fig.update_traces(texttemplate='%{text:.4f}', textposition='inside')

    # --- Chart Type 3: Scatter Plot ---
    else: # Scatter Plot
        chart_title = f"{metric_to_plot} vs. Execution Time"
        fig = px.scatter(
            df,
            x='Mean Time (s)',
            y=metric_to_plot,
            size='Runs',
            color='Algorithm',
            hover_name='Algorithm',
            title=chart_title,
            text='Algorithm' # Display algorithm names on the plot
        )
        fig.update_traces(textposition='top center')

    # --- Display the selected chart ---
    fig.update_layout(height=500, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True, theme=None)

def show_convergence_analysis(results):
    """Show detailed analysis with convergence curves"""
    
    st.markdown("### 🔄 Convergence Analysis")
    
    # Convergence curves
    fig = go.Figure()
    
    for alg_name, result in results.items():
        # Get best run's convergence
        best_run = min(result['runs'], key=lambda x: x['best_fitness'])
        convergence = best_run['convergence_curve']
        
        fig.add_trace(go.Scatter(
            x=list(range(len(convergence))),
            y=convergence,
            mode='lines+markers',
            name=alg_name.upper(),
            line=dict(width=2),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title="Convergence Curves (Best Runs)",
        xaxis_title="Iteration",
        yaxis_title="Fitness Value",
        height=600,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_export_options(results):
    """Show export and download options"""
    
    st.markdown("### 💾 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        summary_data = []
        for alg_name, result in results.items():
            stats = result['statistics']
            summary_data.append({
                'Algorithm': alg_name.upper(),
                'Best_Fitness': stats['best_fitness'],
                'Mean_Fitness': stats['mean_fitness'],
                'Std_Fitness': stats['std_fitness'],
                'Mean_Time': stats['mean_time'],
                'Total_Runs': stats['total_runs']
            })
        
        df_export = pd.DataFrame(summary_data)
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Summary (CSV)",
            data=csv,
            file_name=f"mha_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        import json
        
        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_algorithms': len(results)
            },
            'results': {alg: result for alg, result in results.items()}
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Complete Results (JSON)",
            data=json_str,
            file_name=f"mha_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

def show_about_page():
    """
    Renders the new, comprehensive "About" page, combining information
    from the README and the Enhancements Summary.
    """
    st.header("ℹ️ About the MHA Toolbox")
    st.markdown("""
    Welcome! This platform is a complete, production-ready system for the analysis, comparison, 
    and deep-dive optimization of metaheuristic algorithms.
    """)

    st.subheader("✨ Key Features at a Glance")
    st.markdown("""
    - **🧬 37+ Algorithms Included**: A massive library covering Swarm Intelligence, Evolutionary, Physics-based, and more.
    - **💾 Automatic Result Saving**: Never lose your work. All experiment results are automatically saved to the backend.
    - **🛡️ Sleep & Refresh Proof**: Thanks to a persistent state system, your work survives browser refreshes and system sleep.
    - **🔬 Intelligent Execution Modes**: The system automatically adapts, providing a deep-dive analysis for a single algorithm or a comparative overview for multiple.
    - **📊 Advanced Visualizations**: Go beyond basic charts with agent trajectory plots, fitness heatmaps, and exploration/exploitation analysis.
    - **📥 Downloads That Last**: Downloaded files are saved persistently, so they don't disappear on a page reload.
    """)

    st.markdown("---")

    # --- Core Features Explained ---
    st.subheader("🔧 Core System Enhancements Explained")
    st.info("Click on any feature below to learn more about how it works.")

    with st.expander("🛡️ Never Lose Your Work: Persistent State Management"):
        st.markdown("""
        - **Problem Solved**: Experiments vanishing if the browser was refreshed or the computer went to sleep.
        - **Solution**: A comprehensive state management system that automatically saves your session.
        - **How it Works**:
            - Your experiment's state is saved to the `persistent_state/` directory automatically.
            - If you refresh the page or your system sleeps, the application can restore you to where you left off.
            - This ensures **zero data loss** for long-running experiments.
        """)

    with st.expander("🔬 Deep Dive or Broad Comparison? Intelligent Execution Modes"):
        st.markdown("""
        - **Problem Solved**: The interface didn't distinguish between analyzing one algorithm in detail vs. comparing many.
        - **Solution**: The system intelligently detects how many algorithms you've selected.
        - **Modes**:
            - **Single Algorithm Mode (1 algorithm selected)**: Unlocks detailed analysis, including agent position tracking, population diversity metrics, and advanced visualizations to see *how* the algorithm works internally.
            - **Comparison Mode (2+ algorithms selected)**: Provides a high-level comparison of performance, speed, and stability, allowing you to quickly identify the best algorithm for your problem.
        """)

    with st.expander("📊 Beyond the Score: Advanced Agent Tracking"):
        st.markdown("""
        - **Problem Solved**: Standard results only show the final score, not the optimization journey.
        - **Solution**: In Single Algorithm Mode, the system tracks the behavior of every single agent across all iterations.
        - **Data Collected**:
            - **Agent Positions**: See the trajectory of each agent in the search space (2D/3D plots).
            - **Agent Fitness**: A heatmap showing the fitness of every agent over time.
            - **Exploration vs. Exploitation**: A plot showing whether the algorithm is searching new areas or refining known ones.
            - **Population Diversity**: Metrics to see if the agents are converging or getting stuck.
        """)

    with st.expander("📥 Downloads That Don't Disappear"):
        st.markdown("""
        - **Problem Solved**: In standard Streamlit apps, download links can break after a refresh.
        - **Solution**: All generated download files (CSV, JSON) are saved to the `persistent_state/downloads/` directory.
        - **Benefit**: The download links are always valid and the files remain accessible until you start a new session, surviving refreshes and system sleep.
        """)

    st.markdown("---")

    # --- Algorithm Compendium ---
    st.subheader("🧬 Interactive Algorithm Compendium")
    st.markdown("The toolbox includes over 37 algorithms, categorized for your convenience. Click on a category to see the available algorithms.")

    algorithm_groups = {
        "🐝 Swarm Intelligence": ["pso", "alo", "woa", "gwo", "ssa", "mrfo", "spider", "fa", "ba"],
        "🧬 Evolutionary": ["ga", "de", "eo", "innov", "sca"],
        "🌊 Physics-Based": ["sa", "hgso", "wca", "wdo", "cgo", "gbo", "fbi", "pfa"],
        "🔬 Bio-Inspired": ["csa", "coa", "msa", "sma", "tso"],
        "🌟 Novel / Other": ["ao", "aoa", "ica", "qsa", "spbo", "vcs", "vns",]
    }

    for group_name, algorithms in algorithm_groups.items():
        with st.expander(f"**{group_name}** ({len(algorithms)} algorithms)"):
            st.markdown("- " + "\n- ".join([f"`{alg.upper()}`" for alg in algorithms]))

    st.markdown("---")
    
    # --- Documentation Link ---
    st.subheader("Documentation & Source Code")
    st.markdown("For more detailed information, bug reports, or to contribute to the project, please visit our official GitHub repository.")
    st.link_button("🔗 Go to GitHub Repository", "https://github.com/Achyut103040/MHA-Algorithm")

def show_settings_page():
    """
    Renders the new Settings page for user customization.
    """
    st.markdown("## ⚙️ Settings")
    st.markdown("Customize the application's appearance, default behaviors, and data management.")
    st.markdown("---")

    # --- Section 1: Experiment & Workflow Settings ---
    st.subheader("🔬 Experiment Defaults")
    st.markdown("Set the default values for the 'Custom' preset on the New Experiment page.")
    
    with st.container(border=True):
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            # Load current value, then display the widget
            default_max_iter = st.session_state.default_params['max_iter']
            st.session_state.default_params['max_iter'] = st.number_input(
                "Default Max Iterations", 
                min_value=10, max_value=500, value=default_max_iter
            )
        with p_col2:
            default_pop_size = st.session_state.default_params['pop_size']
            st.session_state.default_params['pop_size'] = st.number_input(
                "Default Population Size", 
                min_value=5, max_value=200, value=default_pop_size
            )
        with p_col3:
            default_n_runs = st.session_state.default_params['n_runs']
            st.session_state.default_params['n_runs'] = st.number_input(
                "Default Number of Runs", 
                min_value=1, max_value=20, value=default_n_runs
            )
        st.success("✅ Your custom defaults are saved for this session.")

    st.markdown("---")

    # --- Section 2: System & Appearance Settings ---
    st.subheader("🖥️ System & Appearance")

    with st.container(border=True):
        # Keep-Awake Toggle
        st.session_state.keep_awake = st.checkbox(
            "☕ Keep System Awake During Experiments",
            value=st.session_state.keep_awake,
            help="Prevents the computer from sleeping while an experiment is running. Requires the 'wakepy' library."
        )
        if WAKEPY_AVAILABLE:
            st.info(f"Keep-awake mode is currently **{'ENABLED' if st.session_state.keep_awake else 'DISABLED'}**.")
        else:
            st.warning("`wakepy` library not installed. This feature is unavailable.")

        # Theme selection (conceptual for now)
        st.session_state.app_theme = st.radio(
            "🎨 App Theme",
            ['Dark', 'Light'],
            index=0 if st.session_state.app_theme == 'Dark' else 1,
            horizontal=True,
            help="Theme changes will be fully applied on the next app restart."
        )
        st.info("Note: Full theme changes require restarting the Streamlit application.")

    st.markdown("---")
    
    # --- Section 3: Data Management ---
    st.subheader("💾 Data Management")
    with st.container(border=True):
        st.markdown("**Application Cache**")
        st.markdown("The application caches certain data to run faster. If you encounter issues or stale data, clearing the cache can help.")
        if st.button("🧹 Clear Application Cache", use_container_width=True):
            try:
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("✅ Application cache cleared successfully! The app will now reload all data.")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Could not clear cache: {e}")

def show_results_history():
    """
    Results History Page with multi-select for viewing and deleting experiments.
    REMOVED the "Select All" checkbox for a cleaner UI.
    FIXED the empty label warning for checkboxes.
    """
    
    st.markdown("## 📚 Results History")

    # --- DELETION CONFIRMATION UI ---
    if 'confirming_delete' in st.session_state and st.session_state.confirming_delete:
        delete_info = st.session_state.confirming_delete
        
        if delete_info['type'] == 'selected':
            st.warning(f"**Are you sure you want to permanently delete the selected {len(delete_info['info'])} experiments?** This action cannot be undone.")
            with st.expander("Show experiments marked for deletion"):
                for exp in delete_info['info']:
                    st.markdown(f"- `{exp['dataset_name']}` / `{exp['session_id']}`")
        else: # type == 'all'
            st.warning("**Are you sure you want to permanently delete ALL experiments?** This will clear your entire history and cannot be undone.")

        col1, col2, col3 = st.columns([1.2, 1, 4])
        with col1:
            if st.button("✅ Yes, Delete", use_container_width=True, type="primary"):
                try:
                    count = 0
                    if delete_info['type'] == 'selected':
                        for exp in delete_info['info']:
                            managers['results'].delete_experiment(exp['dataset_name'], exp['session_id'])
                            count += 1
                        st.success(f"Successfully deleted {count} selected experiments.")
                    else: # type == 'all'
                        count = len(managers['results'].list_all_experiments())
                        managers['results'].delete_all_experiments()
                        st.success(f"All {count} experiments have been cleared.")

                    del st.session_state.confirming_delete
                    st.session_state.selected_for_deletion = []
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred during deletion: {e}")
                    del st.session_state.confirming_delete
                    st.rerun()
        with col2:
            if st.button("❌ No, Cancel", use_container_width=True):
                del st.session_state.confirming_delete
                st.rerun()
        return

    # --- VIEWING A SINGLE EXPERIMENT ---
    if 'viewing_session_info' in st.session_state and st.session_state.viewing_session_info:
        info = st.session_state.viewing_session_info
        if st.button("⬅️ Back to History List"):
            del st.session_state.viewing_session_info
            st.rerun()
        results = managers['results'].load_experiment_results(info['dataset_name'], info['session_id'])
        if results:
            show_results_dashboard(results)
        else:
            st.error(f"Failed to load results for session: {info['session_id']}")
            del st.session_state.viewing_session_info
            st.rerun()
        return

    # --- MAIN HISTORY LIST & MANAGEMENT ---
    experiments = managers['results'].list_all_experiments()
    
    if not experiments:
        st.info("📝 No previous results found. Run an experiment to build your history!")
        return
    
    # --- ACTION BAR ---
    st.markdown("#### Manage Experiments")
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        disable_delete_selected = not st.session_state.selected_for_deletion
        if st.button("🗑️ Delete Selected", use_container_width=True, disabled=disable_delete_selected):
            st.session_state.confirming_delete = {
                'type': 'selected',
                'info': st.session_state.selected_for_deletion
            }
            st.rerun()
    with col2:
        if st.button("💥 Delete All", use_container_width=True, type="primary"):
            st.session_state.confirming_delete = {'type': 'all'}
            st.rerun()
    
    st.info(f"📂 Found {len(experiments)} experiments. You have selected **{len(st.session_state.selected_for_deletion)}**.")
    st.markdown("---")

    # --- SELECTION PROCESSING ---
    checkbox_states = {}
    
    # Display experiments with individual checkboxes
    for exp in experiments:
        exp_identifier = f"{exp['dataset_name']}_{exp['session_id']}"
        is_selected = any(exp_identifier == f"{sel['dataset_name']}_{sel['session_id']}" for sel in st.session_state.selected_for_deletion)

        cols = st.columns([0.5, 4, 3, 1])
        with cols[0]:
            checkbox_key = f"select_{exp_identifier}"
            
            # --- THIS IS THE FIX ---
            checkbox_states[checkbox_key] = st.checkbox(
                label=f"select_experiment_{exp_identifier}", # Unique, non-empty label
                value=is_selected,
                key=checkbox_key,
                label_visibility="collapsed" # Hide the label from the UI
            )
        
        with cols[1]:
            st.markdown(f"**Dataset:** `{exp['dataset_name']}`")
        with cols[2]:
            st.markdown(f"**Session:** `{exp['session_id']}` ({exp['modified_at'][:10]})")
        with cols[3]:
            if st.button("📊 View", key=f"view_{exp_identifier}", use_container_width=True):
                st.session_state.viewing_session_info = exp
                st.session_state.selected_for_deletion = [] # Clear selection when viewing one
                st.rerun()
        st.markdown("""<hr style="margin: 0.5rem 0;" />""", unsafe_allow_html=True)

    # --- UPDATE SESSION STATE POST-RENDER ---
    new_selection = []
    
    for exp in experiments:
        exp_identifier = f"{exp['dataset_name']}_{exp['session_id']}"
        checkbox_key = f"select_{exp_identifier}"
        if checkbox_states.get(checkbox_key):
            new_selection.append(exp)

    selected_ids_before = {f"{sel['dataset_name']}_{sel['session_id']}" for sel in st.session_state.selected_for_deletion}
    selected_ids_after = {f"{sel['dataset_name']}_{sel['session_id']}" for sel in new_selection}

    if selected_ids_before != selected_ids_after:
        st.session_state.selected_for_deletion = new_selection
        st.rerun()

def load_dataset(dataset_name, dataset_type):
    """Load dataset based on name and type"""
    
    try:
        if dataset_type == 'sample':
            from sklearn.datasets import (load_breast_cancer, load_wine, load_iris,
                                         load_digits, fetch_california_housing, load_diabetes)
            
            if dataset_name == "Breast Cancer":
                data = load_breast_cancer()
                return data.data, data.target, "Breast Cancer"
            
            elif dataset_name == "Wine":
                data = load_wine()
                return data.data, data.target, "Wine"
            
            elif dataset_name == "Iris":
                data = load_iris()
                return data.data, data.target, "Iris"
            
            elif dataset_name == "Digits":
                data = load_digits()
                return data.data, data.target, "Digits"
            
            elif dataset_name == "California Housing":
                data = fetch_california_housing()
                return data.data, data.target, "California Housing"
            
            elif dataset_name == "Diabetes":
                data = load_diabetes()
                return data.data, data.target, "Diabetes"
        
        elif dataset_type == 'uploaded':
            # Load from session state
            df = st.session_state.get('uploaded_data')
            target_col = st.session_state.get('target_column')
            
            if df is not None and target_col:
                feature_cols = [col for col in df.columns if col != target_col]
                X = df[feature_cols].values
                y = df[target_col].values
                return X, y, dataset_name
        
        return None, None, None
        
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None, None, None


if __name__ == "__main__":
    main()
