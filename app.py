"""
🏥 AI-Based Gamified Rehabilitation System
==========================================
Main Streamlit application entry point.

This is the home page where users log in (by entering their name)
and see their quick stats overview. Navigation to other pages happens
via the Streamlit sidebar.

Run with: streamlit run app.py
"""
import streamlit as st
from firebase_utils.config import init_firebase
from firebase_utils.db import create_or_get_user, get_user
from gamification.levels import get_level, get_level_progress, get_next_level

# ============================================================
# PAGE CONFIG (must be first Streamlit command)
# ============================================================
st.set_page_config(
    page_title="AI Rehab System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS FOR DARK THEME STYLING
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 5px;
    }
    .stat-card h2 {
        color: #e94560;
        font-size: 2.2rem;
        margin: 0;
    }
    .stat-card p {
        color: #a0a0a0;
        font-size: 0.9rem;
        margin: 5px 0 0 0;
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 20px;
        color: white;
    }
    .welcome-banner h1 {
        margin: 0;
        font-size: 2rem;
    }
    .welcome-banner p {
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    
    /* Level progress bar */
    .level-bar {
        background-color: #1a1a2e;
        border-radius: 10px;
        height: 25px;
        margin: 10px 0;
        overflow: hidden;
    }
    .level-fill {
        background: linear-gradient(90deg, #00b4d8, #0077b6);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE FIREBASE (runs once)
# ============================================================
if 'firebase_initialized' not in st.session_state:
    init_firebase()
    st.session_state.firebase_initialized = True

# ============================================================
# LOGIN / USER SELECTION
# ============================================================
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # Show login screen
    st.markdown("")  # Spacing
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🏥 AI Rehab System")
        st.markdown("### AI-Based Gamified Rehabilitation Platform")
        st.markdown("---")
        
        st.markdown("#### 👤 Enter your name to get started")
        name = st.text_input("Your Name", placeholder="e.g., Om Prasad", label_visibility="collapsed")
        
        if st.button("🚀 Start Exercising", use_container_width=True, type="primary"):
            if name.strip():
                # Create or get user from database
                user = create_or_get_user(name.strip())
                st.session_state.user = user
                st.rerun()
            else:
                st.warning("Please enter your name!")
        
        st.markdown("---")
        st.caption("Your progress is saved automatically. Just enter the same name next time!")

else:
    # ============================================================
    # MAIN HOME PAGE (logged in)
    # ============================================================
    user = st.session_state.user
    user_id = user['id']
    
    # Refresh user data from database
    fresh_user = get_user(user_id)
    if fresh_user:
        user = fresh_user
        st.session_state.user = user
    
    # Welcome banner
    level_info = get_level(user.get('total_xp', 0))
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>👋 Welcome back, {user.get('name', 'User')}!</h1>
        <p>Level {level_info['level']} — {level_info['title']} | Keep pushing your limits!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---- QUICK STATS ----
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>⚡ {user.get('total_xp', 0)}</h2>
            <p>Total XP</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>🏋️ {user.get('total_reps', 0)}</h2>
            <p>Total Reps</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2>🔥 {user.get('streak_days', 0)}</h2>
            <p>Day Streak</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h2>📊 {user.get('total_sessions', 0)}</h2>
            <p>Sessions</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ---- LEVEL PROGRESS ----
    st.markdown("### 📈 Level Progress")
    progress = get_level_progress(user.get('total_xp', 0))
    next_lvl = get_next_level(user.get('total_xp', 0))
    
    if next_lvl:
        st.progress(progress, text=f"Level {level_info['level']} ({level_info['title']}) → Level {next_lvl['level']} ({next_lvl['title']}) — {next_lvl['xp_remaining']} XP to go")
    else:
        st.progress(1.0, text=f"🎉 MAX LEVEL REACHED — Level {level_info['level']} ({level_info['title']})")
    
    # ---- QUICK NAVIGATION ----
    st.markdown("### 🚀 Quick Start")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🏋️ Exercise
        Start a live exercise session with real-time pose tracking.
        
        👈 Click **Exercise** in the sidebar to begin!
        """)
    
    with col2:
        st.markdown("""
        #### 📊 Dashboard
        View your session history, progress charts, and analytics.
        
        👈 Click **Dashboard** in the sidebar!
        """)
    
    with col3:
        st.markdown("""
        #### 🏆 Achievements
        Track your badges, milestones, and leaderboard position.
        
        👈 Click **Achievements** in the sidebar!
        """)
    
    # ---- SIDEBAR ----
    with st.sidebar:
        st.markdown(f"### 👤 {user.get('name', 'User')}")
        st.markdown(f"**Level {level_info['level']}** — {level_info['title']}")
        st.markdown(f"⚡ {user.get('total_xp', 0)} XP")
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
