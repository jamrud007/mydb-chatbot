"""
Streamlit Dashboard for MyDB Chatbot
Consumes FastAPI backend for interactive data exploration
"""
import streamlit as st
import httpx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import json
import plotly.express as px
from datetime import datetime
from utils.visualization_helper import VisualizationHelper
from utils.dashboard_manager import DashboardManager
from utils.chart_factory import ChartFactory
import os
from config import Config

# ===== Configuration =====
# API Configuration
API_BASE_URL = Config.BACKEND_URL

st.set_page_config(
    page_title="MyDB Chatbot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)




# ===== Custom CSS for Dark Mode & UI =====
st.markdown("""
<style>
    /* 1. INPUT FIELDS: White Box + Black Bold Text (Classic Look) */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* 2. SUMMARY / EXPLANATION TEXT: White Bold (High Contrast on Dark) */
    .stCaption, .stMarkdown p {
        color: #f8f8f2 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    /* 3. CODE BLOCKS: White Box + Dark Blue/Black Text */
    .stCodeBlock {
         background-color: #ffffff !important;
         border: 1px solid #e2e8f0 !important;
         border-radius: 8px !important;
    }
    code {
        color: #1a202c !important; /* Dark Blue/Black */
        background-color: #ffffff !important;
        font-weight: bold !important;
        font-family: 'Consolas', 'Monaco', monospace !important;
    }
    
    /* Syntax Highlighting - Darker Colors for White Background */
    .token.keyword { color: #d53f8c !important; } /* Pink/Red */
    .token.string { color: #2f855a !important; } /* Green */
    .token.function { color: #3182ce !important; } /* Blue */
    .token.number { color: #805ad5 !important; } /* Purple */
    
    /* Sidebar Text */
    [data-testid="stSidebar"] {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)
# ===== Authentication Guard & Login UI =====
if not st.session_state.get('is_authenticated'):
    
    # ===== Custom CSS for Auth Pages ONLY =====
    st.markdown("""
    <style>
        /* Hide default Streamlit elements on auth page */
        [data-testid="stSidebar"] {display: none;}
        .main > div {padding-top: 2rem;}
        
        /* Modern Auth Container */
        .auth-card {
            max-width: 440px;
            margin: 0 auto;
            background: white;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }
        
        /* Title Styling */
        .auth-title {
            text-align: center;
            font-size: 1.75rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 8px;
        }
        
        .auth-subtitle {
            text-align: center;
            font-size: 0.95rem;
            color: #718096;
            margin-bottom: 24px;
        }
        
        /* Input Field Styling */
        .stTextInput > div > div > input {
            height: 44px;
            border-radius: 8px;
            border: 1.5px solid #e2e8f0;
            padding: 12px 16px;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.08);
        }
        
        .stTextInput > label {
            font-size: 0.9rem;
            font-weight: 500;
            color: #2d3748;
            margin-bottom: 6px;
        }
        
        /* Primary Button Styling */
        .stButton > button[kind="primary"] {
            height: 46px;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 2px 12px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button[kind="primary"]:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Link Styling */
        .auth-link {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .auth-link:hover {
            text-decoration: underline;
            color: #5568d3;
        }
        
        /* Security Note */
        .security-note {
            text-align: center;
            font-size: 0.8rem;
            color: #a0aec0;
            margin-top: 20px;
        }
        
        /* Form spacing */
        .stTextInput {
            margin-bottom: 14px;
        }
        
        /* Success/Error boxes */
        .element-container div[data-testid="stMarkdownContainer"] p {
            border-radius: 6px;
        }
        
        /* Larger Toast Notifications */
        .stToast {
            font-size: 1.1rem !important;
            padding: 16px 24px !important;
            min-width: 300px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
        }
        
        .stToast > div {
            font-size: 1.1rem !important;
            font-weight: 500 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Helper functions for Auth (Inline to keep main app self-contained)
    def call_auth_api(endpoint: str, method: str = "GET", data: dict = None):
        """Call FastAPI endpoint for Auth (No Token)"""
        url = f"{API_BASE_URL}{endpoint}"
        try:
            with httpx.Client(timeout=float(Config.QUERY_TIMEOUT_SECONDS)) as client:
                if method == "POST":
                    response = client.post(url, json=data)
                else:
                    return {"success": False, "error": f"Unsupported method: {method}"}
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"success": False, "error": "Invalid username/email or password"}
            elif e.response.status_code == 400:
                try:
                    error_detail = e.response.json().get('detail', str(e))
                except:
                    error_detail = str(e)
                return {"success": False, "error": error_detail}
            elif e.response.status_code == 422:
                try:
                    detail = e.response.json().get('detail', [])
                    if isinstance(detail, list):
                        # Pydantic error list
                        msg = ", ".join([f"{err['loc'][-1]}: {err['msg']}" for err in detail])
                    else:
                        msg = str(detail)
                    error_detail = f"Validation Error: {msg}"
                except:
                    error_detail = "Validation Error: Invalid input format"
                return {"success": False, "error": error_detail}
            else:
                return {"success": False, "error": f"API Error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def login_user(username_or_email, password):
        """Login user and store JWT token in session"""
        response = call_auth_api(
            "/api/auth/login",
            method="POST",
            data={"username_or_email": username_or_email, "password": password}
        )
        
        if response and response.get("access_token"):
            st.session_state['jwt_token'] = response['access_token']
            user_data = response['user']
            # Ensure role is stored (admin or user)
            if 'role' not in user_data:
                user_data['role'] = 'user'
            st.session_state['user_info'] = user_data
            st.session_state['is_authenticated'] = True
            return True, "Login successful!"
        else:
            error = response.get('error', 'Login failed') if response else 'Connection failed'
            return False, error

    def register_user(username, email, password):
        """Register new user"""
        response = call_auth_api(
            "/api/auth/register",
            method="POST",
            data={"username": username, "email": email, "password": password}
        )
        
        # Handle new registration flow: token is empty until OTP verified
        if response and response.get("user"):
            # Check if token exists (old flow: auto-login) or empty (new flow: OTP required)
            if response.get("access_token"):
                # Old flow or verification not required
                st.session_state['jwt_token'] = response['access_token']
                st.session_state['user_info'] = response['user']
                st.session_state['is_authenticated'] = True
            # Registration successful regardless of token presence
            return True, "Registration successful!"
        else:
            error = response.get('error', 'Registration failed') if response else 'Connection failed'
            return False, error

    # --- Auth Page Navigation ---
    # Initialize auth page state
    if 'auth_page' not in st.session_state:
        st.session_state['auth_page'] = 'login'
    
    current_page = st.session_state['auth_page']
    
    # --- LOGIN PAGE ---
    if current_page == 'login':
        # Center the form with columns
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            
            # A) HEADER
            st.markdown('<h1 class="auth-title">🔐 Selamat Datang Kembali</h1>', unsafe_allow_html=True)
            st.markdown('<p class="auth-subtitle">Masuk untuk melanjutkan ke dashboard</p>', unsafe_allow_html=True)
            
            # Show success toast if just registered
            if st.session_state.get('show_registration_success'):
                st.toast("🎉 Registrasi berhasil! Silakan lanjut login.", icon="✅")
                del st.session_state['show_registration_success']  # Clear flag after showing
            
            # C) FORM INPUT
            with st.form("login_form"):
                username_or_email = st.text_input(
                    "Username atau Email", 
                    placeholder="contoh@email.com",
                    key="login_username"
                )
                password = st.text_input(
                    "Kata Sandi", 
                    type="password", 
                    placeholder="Masukkan kata sandi",
                    key="login_password"
                )
                
                # D) PRIMARY CTA
                submitted = st.form_submit_button("🚀 Masuk", use_container_width=True, type="primary")
                
                # H) VALIDATION & FEEDBACK
                if submitted:
                    if not username_or_email or not password:
                        st.error("❌ Mohon isi username/email dan kata sandi")
                    else:
                        with st.spinner("Memverifikasi..."):
                            success, message = login_user(username_or_email, password)
                            if success:
                                st.success("✅ Berhasil masuk. Mengarahkan...")
                                st.rerun()
                            else:
                                # More specific error message
                                if "not found" in message.lower() or "invalid" in message.lower():
                                    st.error("❌ Username/email atau kata sandi salah")
                                else:
                                    st.error(f"❌ {message}")
            
            # E) SECONDARY ACTIONS (as links)
            st.markdown('<div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">', unsafe_allow_html=True)
            
            col_left, col_right = st.columns(2)
            with col_left:
                if st.button("Daftar", key="link_register", help="Belum punya akun?"):
                    st.session_state['auth_page'] = 'register'
                    st.rerun()
            with col_right:
                if st.button("Lupa kata sandi?", key="link_forgot"):
                    st.info("Fitur reset kata sandi segera hadir!")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # G) FOOTER NOTE (inside card)
            st.markdown('<p class="security-note">🔒 Kredensial Anda diproses dengan aman</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # --- REGISTER PAGE ---
    elif current_page == 'register':
        # Center the form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h1 class="auth-title">📝 Create New Account</h1>', unsafe_allow_html=True)
            
            # Real-time Validation - Username
            reg_username = st.text_input("Username", placeholder="Min 3 characters", help="Choose a unique username", key="reg_user")
            username_valid = False
            if reg_username:
                if len(reg_username) < 3:
                    st.error("❌ Username too short (min 3 chars)")
                else:
                    st.success("✅ Username looks good!")
                    username_valid = True

            # Real-time Validation - Email
            reg_email = st.text_input("Email", placeholder="your.email@gmail.com", help="Must be a Gmail address", key="reg_email")
            email_valid = False
            if reg_email:
                if not reg_email.endswith("@gmail.com"):
                    st.error("❌ Only @gmail.com addresses are allowed")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("❌ Invalid email format")
                else:
                    st.success("✅ Valid Gmail address")
                    email_valid = True

            # Real-time Validation - Password
            reg_password = st.text_input("Password", type="password", placeholder="Min 8 chars, Aa1!", help="Requires: 8+ chars, Uppercase, Lowercase, Digit, Symbol", key="reg_pass")
            password_valid = False
            if reg_password:
                errors = []
                if len(reg_password) < 8:
                    errors.append("Min 8 characters")
                if not any(c.isupper() for c in reg_password):
                    errors.append("1 Uppercase (A-Z)")
                if not any(c.islower() for c in reg_password):
                    errors.append("1 Lowercase (a-z)")
                if not any(c.isdigit() for c in reg_password):
                    errors.append("1 Digit (0-9)")
                
                # Special characters allowed by auth_helper.py
                special_chars = r"!@#$%^&*(),.?\":{}|<>_\\-+=/\[\];\'`~"
                if not any(c in special_chars for c in reg_password):
                    errors.append("1 Symbol (!@#$...)")
                
                if errors:
                    st.error(f"❌ Weak Password: {', '.join(errors)}")
                else:
                    st.success("✅ Password strength: Strong")
                    password_valid = True

            # Real-time Validation - Confirm Password
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
            confirm_valid = False
            if reg_confirm:
                if reg_confirm != reg_password:
                    st.error("❌ Passwords do not match")
                else:
                    st.success("✅ Passwords match")
                    confirm_valid = True

            # Submit Button
            submitted_reg = st.button("✨ Create Account", use_container_width=True, type="primary")
            
            if submitted_reg:
                if not (username_valid and email_valid and password_valid and confirm_valid):
                    st.toast("❌ Please fix the errors above before submitting", icon="⚠️")
                    st.warning("⚠️ Some fields are invalid. Please check the red boxes above.")
                else:
                    with st.spinner("Creating account..."):
                        success, message = register_user(reg_username, reg_email, reg_password)
                        if success:
                            st.balloons()
                            st.toast(f"✅ {message}", icon="🎉")
                            st.success(f"✅ {message}")
                            st.info("👉 Check your email for the OTP code.")
                            
                            # Store email and redirect to verify page
                            st.session_state['pending_verification_email'] = reg_email
                            st.session_state['auth_page'] = 'verify'
                            st.rerun()
                        else:
                            st.toast(f"❌ {message}", icon="⚠️")
                            st.error(f"❌ {message}")
            
            # Navigation link
            st.markdown("---")
            if st.button("🔙 Sudah punya akun?", use_container_width=True):
                st.session_state['auth_page'] = 'login'
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # --- VERIFY OTP PAGE ---
    elif current_page == 'verify':
        # Center the form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h1 class="auth-title">📧 Verify Your Email</h1>', unsafe_allow_html=True)
            
            email = st.session_state.get('pending_verification_email', 'N/A')
            st.info(f"OTP code has been sent to **{email}**")
            
            otp_code = st.text_input("Enter 6-Digit OTP Code", placeholder="000000", max_chars=6, key="otp_input")
            verify_button = st.button("✅ Verify Email", use_container_width=True, type="primary")
            
            if verify_button:
                if not otp_code or len(otp_code) != 6:
                    st.error("❌ Please enter a valid 6-digit OTP code")
                else:
                    with st.spinner("Verifying OTP..."):
                        response = call_auth_api(
                            "/api/auth/verify-otp",
                            method="POST",
                            data={"email": email, "otp": otp_code}
                        )
                        
                        if response and response.get("success"):
                            st.success("✅ Verifikasi email berhasil! Mengarahkan ke halaman login...")
                            st.balloons()
                            
                            # Clear verification state
                            if 'pending_verification_email' in st.session_state:
                                del st.session_state['pending_verification_email']
                            
                            # Set success message to show after redirect
                            st.session_state['show_registration_success'] = True
                            
                            # Redirect to login
                            st.session_state['auth_page'] = 'login'
                            st.rerun()
                        else:
                            error_msg = response.get('error', 'Verification failed') if response else 'Connection failed'
                            st.error(f"❌ {error_msg}")
                            st.warning("💡 Tip: Make sure you entered the correct 6-digit code from your email.")
            
            # Navigation link
            st.markdown("---")
            if st.button("🔙 Back to Login", use_container_width=True):
                st.session_state['auth_page'] = 'login'
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Stop execution so dashboard doesn't render
    st.stop()

# Initialize Session State
if 'query_input' not in st.session_state:
    st.session_state['query_input'] = ''

import os


# Inject Custom CSS
def load_css():
    """Load custom CSS file"""
    css_file = os.path.join(os.path.dirname(__file__), 'assets', 'custom.css')
    try:
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # CSS file not found, continue without it

load_css()

# ===== Authentication Guard & Login UI =====

def handle_clarification(query_text):
    """Callback to handle clarification option selection"""
    st.session_state['pending_query'] = query_text
    # process_later: Also update the widget key so the UI reflects the change on next run if possible
    st.session_state['query_input'] = query_text
    st.session_state['auto_submit_next'] = True
    st.session_state['auto_execute_sql'] = True # NEW: Auto-execute the generated SQL
    
    # Clear stale state
    if 'last_response' in st.session_state:
        del st.session_state['last_response']
    if 'current_result' in st.session_state:
        del st.session_state['current_result']

def submit_feedback(result_id: str, rating: int, comment: str = None):
    """Submit user feedback to backend"""
    try:
        response = call_api(
            "/api/feedback",
            method="POST",
            data={
                "result_id": result_id,
                "rating": rating,
                "comment": comment
            }
        )
        
        if response and response.get('success'):
            return True, response.get('message', 'Thank you for your feedback!')
        else:
            return False, response.get('error', 'Failed to submit feedback')
    except Exception as e:
        return False, str(e)

def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Call FastAPI endpoint with JWT authentication"""
    url = f"{API_BASE_URL}{endpoint}"
    
    # Get JWT token from session
    jwt_token = st.session_state.get('jwt_token')
    headers = {}
    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    
    try:
        with httpx.Client(timeout=float(Config.LLM_TIMEOUT)) as client:
            if method == "GET":
                response = client.get(url, headers=headers)
            elif method == "POST":
                response = client.post(url, json=data, headers=headers)
            elif method == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        # Handle 401 Unauthorized - token expired or invalid
        if e.response.status_code == 401:
            st.error("🔒 Session expired. Please login again.")
            st.session_state.clear()
            st.rerun()
        else:
            st.error(f"API Error: {str(e)}")
        return None
    except httpx.TimeoutException as e:
        st.error(f"⏱️ Request timeout - LLM taking too long. Try again or check API key balance.")
        return None
    except httpx.HTTPError as e:
        st.error(f"API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def create_plotly_chart(chart_config: dict):
    """Create Plotly chart from chart_config"""
    if not chart_config or not chart_config.get('can_visualize'):
        return None
    
    chart_data = chart_config.get('chart_data', {})
    chart_type = chart_data.get('type', 'bar')
    
    # Handle horizontal combo chart
    if chart_data.get('is_horizontal_combo'):
        fig = go.Figure()
        
        for dataset in chart_data.get('datasets', []):
            if dataset.get('type') == 'bar':
                fig.add_trace(go.Bar(
                    y=chart_data['labels'],
                    x=dataset['data'],
                    name=dataset['label'],
                    orientation='h',
                    marker_color=dataset.get('backgroundColor', '#3b82f6')
                ))
            elif dataset.get('type') == 'line':
                fig.add_trace(go.Scatter(
                    y=chart_data['labels'],
                    x=dataset['data'],
                    name=dataset['label'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=dataset.get('borderColor', '#10b981')
                    ),
                    xaxis='x2'
                ))
        
        fig.update_layout(
            xaxis=dict(
                title=chart_data.get('primaryAxisTitle', 'Revenue'),
                side='bottom'
            ),
            xaxis2=dict(
                title=chart_data.get('secondaryAxisTitle', 'Rating') + ' (0-5)',
                overlaying='x',
                side='top',
                range=[0, 5]
            ),
            yaxis=dict(title='Category'),
            height=600,
            template='plotly_dark',
            showlegend=True
        )
        
        return fig
    
    # Standard charts
    fig = go.Figure()
    
    if chart_type == 'bar':
        for dataset in chart_data.get('datasets', []):
            fig.add_trace(go.Bar(
                x=chart_data['labels'],
                y=dataset['data'],
                name=dataset.get('label', ''),
                marker_color=dataset.get('backgroundColor', '#3b82f6')
            ))
    
    elif chart_type == 'line':
        for dataset in chart_data.get('datasets', []):
            fig.add_trace(go.Scatter(
                x=chart_data['labels'],
                y=dataset['data'],
                name=dataset.get('label', ''),
                mode='lines+markers',
                line=dict(color=dataset.get('borderColor', '#3b82f6'))
            ))
    
    elif chart_type == 'pie':
        dataset = chart_data['datasets'][0]
        fig.add_trace(go.Pie(
            labels=chart_data['labels'],
            values=dataset['data'],
            marker=dict(colors=dataset.get('backgroundColor', []))
        ))
    
    elif chart_type == 'scatter':
        dataset = chart_data['datasets'][0]
        fig.add_trace(go.Scatter(
            x=[p['x'] for p in dataset['data']],
            y=[p['y'] for p in dataset['data']],
            mode='markers',
            marker=dict(size=10, color=dataset.get('backgroundColor', '#3b82f6')),
            text=[f"({p['x']}, {p['y']})" for p in dataset['data']],
            name=dataset.get('label', '')
        ))
    
    fig.update_layout(
        height=500,
        template='plotly_dark',
        showlegend=True
    )
    
    return fig


# ===== Main App =====

st.title("📊 MyDB Chatbot Dashboard")

# Sidebar - User Info & Logout
user_info = st.session_state.get('user_info', {})
st.sidebar.success(f"👤 Welcome, **{user_info.get('username', 'User')}**!")
st.sidebar.caption(f"📧 {user_info.get('email', 'N/A')}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# ===== Admin Panel (only visible for admin role) =====
if user_info.get('role') == 'admin':
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔧 Admin Panel", expanded=False):
        st.markdown("**System Metrics**")
        metrics = call_api("/api/metrics")
        if metrics:
            col_a, col_b = st.columns(2)
            col_a.metric("Requests", metrics.get('total_requests', 0))
            col_b.metric("Errors", metrics.get('total_errors', 0))
            slow = metrics.get('slow_queries', 0)
            latency = metrics.get('avg_query_duration_ms', 0)
            st.caption(f"Slow queries: {slow}  |  Avg latency: {latency:.0f}ms")
        else:
            st.caption("Metrics unavailable")

        st.markdown("---")
        st.markdown("**Actions**")

        if st.button("📧 Kirim Laporan Harian", use_container_width=True, key="admin_daily_report"):
            resp = call_api("/api/admin/daily-report", method="POST")
            if resp:
                st.success("✅ Laporan dikirim")
            else:
                st.error("❌ Gagal kirim laporan")

        if st.button("🗑️ Clear All Cache", use_container_width=True, key="admin_clear_cache"):
            resp = call_api("/api/cache/clear", method="DELETE")
            if resp and resp.get('success'):
                st.success("✅ Cache cleared")
                st.rerun()
            else:
                st.error("❌ Gagal clear cache")

        st.markdown("---")
        st.markdown("**Health**")
        health_admin = call_api("/api/health")
        if health_admin:
            db_status = health_admin.get('database', 'unknown')
            llm_status = health_admin.get('llm', 'unknown')
            cache_status = health_admin.get('cache', 'unknown')
            st.caption(f"DB: `{db_status}`")
            st.caption(f"LLM: `{llm_status}`")
            st.caption(f"Cache: `{cache_status}`")

st.sidebar.markdown("---")

# Sidebar - Recent Queries
st.sidebar.title("Recent Queries")

# Fetch recent queries from PERSISTENT CACHE
try:
    with st.sidebar.status("🔄 Loading cache...", expanded=False) as status:
        cache_entries_resp = call_api("/api/cache/entries?limit=10")
        status.update(label="✅ Cache loaded", state="complete")
    
    if cache_entries_resp and cache_entries_resp.get('success'):
        entries = cache_entries_resp.get('entries', [])
        
        if entries:
            # Initialize session state for tracking last loaded
            if 'last_loaded_cache_key' not in st.session_state:
                st.session_state['last_loaded_cache_key'] = None
            
            # Selectbox with auto-load capability
            selected_cache_key = st.sidebar.selectbox(
                "📜 Recent Queries (Click to auto-load)",
                options=[None] + [e['cache_key'] for e in entries],
                format_func=lambda k: "-- Select a query to load --" if k is None else next(
                    (f"[{e['row_count']} rows] {e.get('display_text') or e.get('user_question') or e['query_text'][:40] + '...'}" 
                     for e in entries if e['cache_key'] == k), 
                    k
                ),
                key='cache_selector'
            )
            
            # Auto-load when selection changes and is not None
            if selected_cache_key and selected_cache_key != st.session_state.get('last_loaded_cache_key'):
                st.session_state['last_loaded_cache_key'] = selected_cache_key
                
                # Show loading feedback
                with st.spinner("⏳ Loading query data from cache..."):
                    # Fetch full result for this key
                    full_entry_resp = call_api(f"/api/cache/entry/{selected_cache_key}")
                
                if full_entry_resp and full_entry_resp.get('success'):
                    data = full_entry_resp['data']
                    
                    # Reconstruct result object
                    st.session_state['current_result'] = {
                        'success': True,
                        'sql_query': data['query_text'],
                        'results': data['results'],
                        'columns': data['columns'],
                        'row_count': data['row_count'],
                        'nl_summary': (
                            data.get('summary_analysis')
                            or data.get('analysis')
                            or data.get('summary')
                            or f"Loaded from cache. (Query: {data['query_text']})"
                        ),
                        'visualization': VisualizationHelper.analyze_for_visualization(
                            data['results'], data['columns'], data['query_text']
                        ),
                        'from_cache': True,
                        'cache_age': data['age'],
                        'cache_access_count': data['access_count']
                    }
                    
                    # Show success notification
                    st.sidebar.success(f"✅ Loaded: {data['row_count']} rows")
                    st.rerun()
        else:
            st.sidebar.info("Cache is empty. Queries you run will appear here.")
    else:
        st.sidebar.warning("Could not load recent queries.")
        
except Exception as e:
    st.sidebar.error(f"Error loading history: {e}")

# Main Area - Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📊 Single Chart", "🎛️ Dashboard", "📋 Data Table"])

# Tab 1: Chat Interface
with tab1:
    st.header("Chat with Your Database")
    
    # Chat form
    with st.form("chat_form"):
        # SYNC: Update query_input from pending_query if it exists (BEFORE widget creation)
        if st.session_state.get('pending_query'):
            st.session_state['query_input'] = st.session_state['pending_query']
            
        user_query = st.text_area(
            "Ask a question",
            placeholder="e.g., Top 5 kategori produk dengan total pendapatan tertinggi...",
            height=100,
            key="query_input" # Controlled via session state
        )
        user_id = st.text_input("User ID (optional)", value="streamlit_user")
        submitted = st.form_submit_button("🚀 Generate SQL")
    
    # Handle auto-submission after a clarification option is selected
    if st.session_state.get('auto_submit_next'):
        submitted = True
        st.session_state['auto_submit_next'] = False
        # Prioritize pending_query set by the clarification button
        if st.session_state.get('pending_query'):
            user_query = st.session_state.get('pending_query')
            # Clear it to avoid sticking
            del st.session_state['pending_query']
        else:
            # Fallback
            user_query = st.session_state.get('query_input', user_query)
            
    # Restore last response if exists (after rerun)
    # Restore last response if exists (after rerun)
    if 'last_response' in st.session_state and not submitted:
        response = st.session_state['last_response']
        user_id = st.session_state.get('current_user_id', 'streamlit_user')
    elif submitted and user_query:
        # DEBUG: Visual indicator of execution
        st.info(f"🚀 Memproses Query: {user_query}")
        
        with st.spinner("Generating SQL queries..."):
            response = call_api(
                "/api/chat",
                method="POST",
                data={"message": user_query, "user_id": user_id}
            )
            
            if response is None:
                st.error("❌ Gagal terhubung ke API (Response None)")
            elif not response.get('success'):
                st.error(f"❌ API Error: {response.get('error')}")
    else:
        response = None
    
    # Display response if available
    if response and response.get('success'):
        # NEW: Handle clarification needed
        if response.get('type') == 'clarification_needed':
            # AUTO-RESOLVE: Bypass clarification options
            # st.warning("🤔 " + response['message'])
            st.info("⚡ Auto-resolving ambiguity (Picking best option)...")
            
            if response.get('clarification_options'):
                best_option = response['clarification_options'][0]
                
                # Directly update state safely (avoid modifying widget key directly here)
                st.session_state['pending_query'] = best_option['example_query']
                st.session_state['auto_submit_next'] = True
                st.session_state['auto_execute_sql'] = True
                
                st.rerun()


                        

        
        # EXISTING: Handle SQL generation
        elif response.get('suggested_queries'):
            st.success(response['message'])
            
            # Save to session state to persist across reruns
            st.session_state['last_response'] = response
            st.session_state['current_user_id'] = user_id
            
            # Display suggested queries
            st.subheader("Suggested SQL Queries")
            
            # Check for auto-execution flag
            auto_exec_index = None
            
            # DEBUG: Check flags
            # st.write(f"DEBUG: AutoExec={st.session_state.get('auto_execute_sql')}, Queries={len(response.get('suggested_queries', []))}")
            
            if st.session_state.get('auto_execute_sql') and response['suggested_queries']:
                auto_exec_index = 0
                st.session_state['auto_execute_sql'] = False # Consume flag
                st.info("⚡ Auto-executing refined query... (Please Wait)")

            for idx, query in enumerate(response['suggested_queries']):
                with st.expander(f"Query #{idx + 1}: {query['explanation'][:80]}...", expanded=(idx==0 or idx==auto_exec_index)):
                    # Display SQL in bold red
                    st.markdown(f"<p style='color: red; font-weight: bold; font-family: monospace; white-space: pre-wrap;'>{query['sql']}</p>", unsafe_allow_html=True)
                    st.caption(query['explanation'])
                    
                    # Execute button (or auto-execute)
                    # DEBUG: Show if we are executing
                    if auto_exec_index == idx:
                        st.text("🚀 Triggering Execution API...")
                        
                    if (auto_exec_index == idx) or st.button(f"Execute Query #{idx + 1}", key=f"exec_{idx}"):
                        with st.spinner(f"Executing Query #{idx+1}..."):
                            exec_response = call_api(
                                f"/api/execute/{idx}?user_id={user_id}",
                                method="POST"
                            )
                        
                        if exec_response and exec_response.get('success'):
                            st.session_state['current_result'] = exec_response
                            st.session_state['selected_result_id'] = exec_response.get('result_id')
                            
                            # Show success notification with guidance
                            st.success(f"""
                            ✅ **Query berhasil dijalankan!**
                            
                            📊 **{exec_response['row_count']} rows** ditemukan
                            
                            👉 Silakan lihat:
                            - Tab **📊 Visualization** untuk chart interaktif
                            - Tab **📋 Data Table** untuk detail data lengkap
                            """)
                            
                            # Render chart directly in chat
                            if exec_response.get('visualization') and exec_response['visualization'].get('can_visualize'):
                                st.divider()
                                viz_config = exec_response['visualization']
                                st.markdown(f"### 📊 {viz_config.get('chart_type', 'Chart').title()}")
                                
                                # Create and display chart
                                fig = create_plotly_chart(viz_config)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.warning("⚠️ Could not render chart")
                                
                                st.caption(f"💡 Analysis: {viz_config.get('reason', '')}")
                            
                            # Feedback buttons
                            st.markdown("---")
                            st.markdown("**Was this result helpful?**")
                            col1, col2, col3 = st.columns([1, 1, 8])
                            
                            with col1:
                                if st.button("👍", key=f"thumbs_up_{idx}", help="Good result"):
                                    success, msg = submit_feedback(
                                        exec_response.get('result_id', 'unknown'),
                                        rating=1
                                    )
                                    if success:
                                        st.toast("✅ Thank you for your feedback!", icon="👍")
                                    else:
                                        st.toast(f"❌ {msg}", icon="⚠️")
                            
                            with col2:
                                if st.button("👎", key=f"thumbs_down_{idx}", help="Poor result"):
                                    success, msg = submit_feedback(
                                        exec_response.get('result_id', 'unknown'),
                                        rating=-1
                                    )
                                    if success:
                                        st.toast("✅ Feedback received. We'll improve!", icon="👎")
                                    else:
                                        st.toast(f"❌ {msg}", icon="⚠️")
                            
                            # Rerun removed to keep the chart visible in Tab 1
                            # st.rerun()
                        elif exec_response:
                            st.error(f"❌ Execution failed: {exec_response.get('error', 'Unknown error')}")
                        else:
                            st.error("❌ Execution failed: API request failed")

# Tab 2: Visualization
with tab2:
    st.header("Data Visualization")
    
    # Load result if selected
    current_result = st.session_state.get('current_result')
    
    if not current_result and 'selected_result_id' in st.session_state:
        # Fetch from API
        result_detail = call_api(f"/api/results/{st.session_state['selected_result_id']}")
        if result_detail:
            current_result = {
                'success': True,
                'sql_query': result_detail['sql_query'],
                'results': result_detail['results'],
                'columns': result_detail['columns'],
                'row_count': result_detail['row_count'],
                'nl_summary': result_detail['nl_summary'],
                'visualization': result_detail['visualization']
            }
            st.session_state['current_result'] = current_result
    
    if current_result:
        # Display summary
        st.info(current_result.get('nl_summary', ''))
        
        # Cache indicator
        if current_result.get('from_cache'):
            cache_age = current_result.get('cache_age', 0)
            access_count = current_result.get('cache_access_count', 0)
            
            # Format age
            if cache_age < 60:
                age_str = f"{cache_age}s"
            elif cache_age < 3600:
                age_str = f"{cache_age // 60}m"
            else:
                age_str = f"{cache_age // 3600}h"
            
            st.success(f"⚡ From Cache • Age: {age_str} • Accessed: {access_count} times")
        else:
            st.info("🔍 Fresh Query • Just cached for next time")
        
        # Display SQL
        with st.expander("View SQL Query"):
            # Display SQL in bold red
            st.markdown(f"<p style='color: red; font-weight: bold; font-family: monospace; white-space: pre-wrap;'>{current_result['sql_query']}</p>", unsafe_allow_html=True)
        
        # Render chart
        viz_config = current_result.get('visualization')
        if viz_config and viz_config.get('can_visualize'):
            st.subheader(f"📊 {viz_config.get('chart_type', 'Chart').title()} Chart")
            st.caption(viz_config.get('reason', ''))
            
            fig = create_plotly_chart(viz_config)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Unable to render chart")
        else:
            st.info("ℹ️ No visualization available for this query")
            if viz_config:
                st.caption(f"Reason: {viz_config.get('reason', 'Unknown')}")
        
        # The provided snippet was intended for this location, but the instruction was for the chat tab.
        # Keeping the original structure of Tab 2 as the instruction was specific to Tab 1.
        # If the user intended to replace the existing viz logic in Tab 2, the instruction would be different.
        # The instruction was "Insert logic to render the chart immediately after the SQL query in the chat tab."
        # The provided snippet for insertion uses `result` which maps to `exec_response` in the chat tab context.
        # The snippet also includes `st.divider()` and `st.caption(f"⏱️ Processed in {result.get('execution_time', 0):.2f}s")}`
        # which makes sense to be displayed after a query execution in the chat tab.
        
    else:
        st.info("👈 Select a query from the sidebar or execute a new one in the Chat tab")

# Tab 3: Dashboard (NEW - Multi-Chart View)
with tab3:
    st.header("📊 Multi-Chart Dashboard")
    
    # Load result if selected
    current_result = st.session_state.get('current_result')
    
    if not current_result and 'selected_result_id' in st.session_state:
        # Fetch from API
        result_detail = call_api(f"/api/results/{st.session_state['selected_result_id']}")
        if result_detail:
            current_result = {
                'success': True,
                'sql_query': result_detail['sql_query'],
                'results': result_detail['results'],
                'columns': result_detail['columns'],
                'row_count': result_detail['row_count'],
                'nl_summary': result_detail['nl_summary'],
                'visualization': result_detail['visualization']
            }
            st.session_state['current_result'] = current_result
    
    if current_result and current_result.get('results'):
        # Initialize dashboard manager
        dashboard_mgr = DashboardManager()
        
        # Get available chart options
        chart_options = dashboard_mgr.get_chart_options(
            current_result['results'],
            current_result['columns']
        )
        
        if not chart_options:
            st.warning("❌ No suitable charts available for this data")
        else:
            # Display metrics cards first
            st.subheader("📈 Key Metrics")
            metrics = dashboard_mgr.get_metrics(
                current_result['results'],
                current_result['columns']
            )
            
            if metrics:
                cols = st.columns(min(len(metrics), 4))
                for i, metric in enumerate(metrics[:4]):  # Max 4 metrics
                    with cols[i]:
                        st.metric(
                            label=metric['label'],
                            value=f"{metric['value']:,.0f}" if metric['format'] == 'number' else metric['value']
                        )
            
            st.markdown("---")
            st.subheader("📊 Visualizations")
            
            # Create dashboard with top 4 charts
            selected_charts = chart_options[:4]  # Take first 4 available
            
            if len(selected_charts) >= 4:
                # 2x2 Grid
                row1_col1, row1_col2 = st.columns(2)
                row2_col1, row2_col2 = st.columns(2)
                
                with row1_col1:
                    st.markdown(f"**{selected_charts[0]['icon']} {selected_charts[0]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[0]['type'],
                        current_result['results'],
                        selected_charts[0]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with row1_col2:
                    st.markdown(f"**{selected_charts[1]['icon']} {selected_charts[1]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[1]['type'],
                        current_result['results'],
                        selected_charts[1]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with row2_col1:
                    st.markdown(f"**{selected_charts[2]['icon']} {selected_charts[2]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[2]['type'],
                        current_result['results'],
                        selected_charts[2]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with row2_col2:
                    st.markdown(f"**{selected_charts[3]['icon']} {selected_charts[3]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[3]['type'],
                        current_result['results'],
                        selected_charts[3]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            elif len(selected_charts) == 3:
                # 1 full width + 2 below
                st.markdown(f"**{selected_charts[0]['icon']} {selected_charts[0]['title']}**")
                fig = ChartFactory.create_chart(
                    selected_charts[0]['type'],
                    current_result['results'],
                    selected_charts[0]['data_config']
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{selected_charts[1]['icon']} {selected_charts[1]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[1]['type'],
                        current_result['results'],
                        selected_charts[1]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown(f"**{selected_charts[2]['icon']} {selected_charts[2]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[2]['type'],
                        current_result['results'],
                        selected_charts[2]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            elif len(selected_charts) == 2:
                # 2 side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{selected_charts[0]['icon']} {selected_charts[0]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[0]['type'],
                        current_result['results'],
                        selected_charts[0]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown(f"**{selected_charts[1]['icon']} {selected_charts[1]['title']}**")
                    fig = ChartFactory.create_chart(
                        selected_charts[1]['type'],
                        current_result['results'],
                        selected_charts[1]['data_config']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            else:
                # Single chart
                st.markdown(f"**{selected_charts[0]['icon']} {selected_charts[0]['title']}**")
                fig = ChartFactory.create_chart(
                    selected_charts[0]['type'],
                    current_result['results'],
                    selected_charts[0]['data_config']
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("👈 Execute a query to view dashboard")

# Tab 4: Data Table
with tab4:
    st.header("Raw Data")
    
    current_result = st.session_state.get('current_result')
    
    if current_result and current_result.get('results'):
        # Convert to DataFrame
        df = pd.DataFrame(current_result['results'])
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", current_result['row_count'])
        col2.metric("Columns", len(current_result['columns']))
        col3.metric("Query Time", "< 1s")
        
        # Filters
        st.subheader("Filters")
        
        # Column filter
        selected_columns = st.multiselect(
            "Select columns to display",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )
        
        if selected_columns:
            df_filtered = df[selected_columns]
        else:
            df_filtered = df
        
        # Display table
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=400
        )
        
        # Export options
        st.subheader("Export Data")
        
        col1, col2, _ = st.columns([1, 1, 5])
        
        with col1:
            # CSV export
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel export
            excel_buffer = pd.ExcelWriter('temp.xlsx', engine='openpyxl')
            df_filtered.to_excel(excel_buffer, index=False)
            excel_buffer.close()
            
            with open('temp.xlsx', 'rb') as f:
                excel_data = f.read()
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("👈 Execute a query to view data table")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### API Status")

health = call_api("/api/health")
if health:
    if health.get('status') == 'healthy':
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.warning("⚠️ API Degraded")
    
    st.sidebar.caption(f"Database: {health.get('database', 'unknown')}")
    st.sidebar.caption(f"LLM: {health.get('llm', 'unknown')}")
else:
    st.sidebar.error("❌ API Offline")

# Cache Statistics
st.sidebar.markdown("---")
st.sidebar.markdown("### Query Cache")

cache_stats = call_api("/api/cache/stats")
if cache_stats and cache_stats.get('enabled'):
    col1, col2 = st.sidebar.columns(2)
    
    hit_rate = cache_stats.get('hit_rate', 0) * 100
    col1.metric("Hit Rate", f"{hit_rate:.1f}%")
    col2.metric("Entries", cache_stats.get('total_entries', 0))
    
    size_mb = cache_stats.get('total_size_mb', 0)
    backend = cache_stats.get('backend', 'unknown').upper()
    st.sidebar.caption(f"📦 {size_mb:.2f} MB • {backend}")
    
    # Clear cache button
    if st.sidebar.button("🗑️ Clear Cache"):
        clear_response = call_api("/api/cache/clear", method="DELETE")
        if clear_response and clear_response.get('success'):
            st.sidebar.success("✅ Cache cleared!")
            st.rerun()
        else:
            st.sidebar.error("❌ Failed to clear cache")
else:
    st.sidebar.info("Cache disabled")
