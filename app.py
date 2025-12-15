import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import time

# --- CONFIGURATION ---
TICKET_PRICE = 18
THEATER_POINTS = 10
OTT_POINTS = 5
HYPE_THRESHOLD_BMS = 45000

st.set_page_config(
    page_title="2025 Tollywood Wrapped", 
    page_icon="🎬", 
    layout="wide"
)

# --- PREMIUM CINEMATIC UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global Variables */
    :root {
        --cinema-gold: #D4AF37;
        --cinema-red: #DC2626;
        --cinema-black: #0A0A0A;
        --cinema-silver: #C0C0C0;
        --neon-blue: #00D4FF;
        --dark-surface: #1A1A1A;
        --gradient-primary: linear-gradient(135deg, #D4AF37 0%, #B8860B 50%, #DAA520 100%);
        --gradient-danger: linear-gradient(135deg, #DC2626 0%, #B91C1C 50%, #991B1B 100%);
        --gradient-surface: linear-gradient(145deg, #1A1A1A 0%, #2D2D2D 100%);
        --shadow-gold: 0 8px 32px rgba(212, 175, 55, 0.3);
        --shadow-red: 0 8px 32px rgba(220, 38, 38, 0.3);
        --shadow-neon: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Global Background */
    .stApp {
        background: radial-gradient(circle at 20% 50%, #1a1a2e 0%, #0f0f0f 100%);
        color: white;
    }
    
    /* Cinema Header */
    .cinema-header {
        background: var(--gradient-primary);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-gold);
        border: 2px solid var(--cinema-gold);
    }
    
    .cinema-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="filmstrip" width="10" height="100" patternUnits="userSpaceOnUse"><rect width="10" height="15" fill="rgba(0,0,0,0.1)"/><rect width="10" height="5" y="20" fill="rgba(0,0,0,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23filmstrip)"/></svg>');
        pointer-events: none;
        opacity: 0.1;
    }
    
    .cinema-header h1 {
        font-family: 'Cinzel', serif;
        font-weight: 700;
        font-size: 3.5rem;
        color: var(--cinema-black);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
        position: relative;
        z-index: 2;
        letter-spacing: 2px;
    }
    
    .cinema-header .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.4rem;
        color: var(--cinema-black);
        margin-top: 0.5rem;
        font-weight: 400;
        position: relative;
        z-index: 2;
        opacity: 0.9;
    }
    
    /* Roast Box with Cinema Aesthetic */
    .roast-box {
        background: var(--gradient-danger);
        color: white;
        border: 3px solid var(--cinema-red);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-red);
        backdrop-filter: blur(10px);
    }
    
    .roast-box::before {
        content: '🔥';
        position: absolute;
        top: -10px;
        right: -10px;
        font-size: 8rem;
        opacity: 0.1;
        z-index: 1;
    }
    
    .roast-header { 
        font-family: 'Cinzel', serif;
        color: var(--cinema-gold);
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        position: relative;
        z-index: 2;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .roast-text { 
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.4rem;
        font-weight: 400;
        line-height: 1.7;
        position: relative;
        z-index: 2;
        text-align: left;
        padding: 0 2rem;
    }
    
    .roast-text ul {
        list-style-type: none; 
        padding: 0;
        margin: 0;
    }
    
    .roast-text li {
        position: relative;
        padding-left: 30px;
        margin-bottom: 15px;
    }
    
    .roast-text li::before {
        content: '🔥'; 
        position: absolute;
        left: 0;
        top: 2px;
        font-size: 1.2rem;
    }
            
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #2A2A2A 0%, #1F1F1F 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid rgba(212, 175, 55, 0.7);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .metric-card:hover::before {
        transform: translateX(0);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-gold), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: var(--cinema-gold);
        background: linear-gradient(145deg, #3A3A3A 0%, #2F2F2F 100%);
    }
    
    .metric-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: var(--cinema-gold);
        text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
        background: linear-gradient(45deg, #D4AF37, #FFD700);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        color: #F5F5F5;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    
    /* Achievement Badges with Animations */
    .achievement-section {
        background: var(--gradient-surface);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid var(--cinema-gold);
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .achievement-section::before {
        content: '🏆';
        position: absolute;
        top: -20px;
        left: -20px;
        font-size: 6rem;
        opacity: 0.1;
        transform: rotate(-15deg);
    }
    
    .achievement-title {
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        color: var(--cinema-gold);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .achievement-badge {
        background: var(--gradient-primary);
        color: var(--cinema-black);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        text-align: center;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        margin: 1rem;
        border: 2px solid var(--cinema-gold);
        box-shadow: var(--shadow-gold);
        animation: achievementPulse 3s infinite;
        position: relative;
        overflow: hidden;
        font-size: 1.1rem;
    }
    
    .achievement-badge::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes achievementPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes shine {
        0% { transform: translateX(-200%) translateY(-200%) rotate(45deg); }
        100% { transform: translateX(200%) translateY(200%) rotate(45deg); }
    }
    
    /* Section Headers */
    .section-header {
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        color: var(--cinema-gold);
        margin: 3rem 0 2rem 0;
        text-align: center;
        position: relative;
        padding: 1rem 0;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 3px;
        background: var(--gradient-primary);
        border-radius: 2px;
    }
    
    /* Premium Tables */
    .premium-table {
        background: var(--gradient-surface);
        border: 2px solid rgba(212, 175, 55, 0.3);
        border-radius: 15px;
        overflow: hidden;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
    }
    
    .table-header {
        background: var(--gradient-primary);
        color: var(--cinema-black);
        padding: 1rem;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 1rem;
        text-align: center;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
    }
    
    /* Chart Container */
    .chart-container {
        background: linear-gradient(145deg, #2A2A2A 0%, #1F1F1F 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid rgba(212, 175, 55, 0.5);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Success/Error Boxes */
    .success-box {
        background: linear-gradient(135deg, #065F46, #047857);
        border: 2px solid #10B981;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
    
    .error-box {
        background: linear-gradient(135deg, #DC2626, #B91C1C);
        border: 2px solid #EF4444;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.2);
    }
    
    /* Buttons Premium Style */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: var(--cinema-black) !important;
        border: 2px solid var(--cinema-gold) !important;
        border-radius: 10px !important;
        padding: 1rem 2rem !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-gold) !important;
    }
    
    /* Progress Bar Cinema Style */
    .stProgress > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 10px !important;
        box-shadow: var(--shadow-gold) !important;
    }
    
    /* Data Editor Styling */
    .stDataFrame {
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stDataFrame [data-testid="stDataFrame"] {
        border: 2px solid var(--cinema-gold) !important;
        border-radius: 15px !important;
        overflow: hidden !important;
        background: var(--gradient-surface) !important;
    }
    
    /* Loading Animation */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }
    
    .film-reel {
        width: 80px;
        height: 80px;
        border: 8px solid var(--cinema-gold);
        border-radius: 50%;
        border-top: 8px solid transparent;
        animation: filmSpin 1s linear infinite;
    }
    
    @keyframes filmSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Cinemawrapped.csv")
    except FileNotFoundError:
        st.error("⚠️ Cinemawrapped.csv not found! Please make sure the file is in the same directory.")
        return None
    
    # Clean Numeric Columns
    for col in ['Run Time In Min', 'IMDB Voted', 'IMDB Ratings', 'BMS Tickets', 'BMS Ratings']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Dates
    df['Release Date'] = pd.to_datetime(df['Release Date'], format='%b %d, %Y', errors='coerce')
    df['Month_Num'] = df['Release Date'].dt.month
    df['Month_Name'] = df['Release Date'].dt.strftime('%b')
    
    # Simplify Genre
    def clean_genre(g):
        g = str(g).lower()
        if 'action' in g: return 'Action 🧨'
        if 'comedy' in g: return 'Comedy 😂'
        if 'romance' in g: return 'Romance ❤️'
        if 'thriller' in g: return 'Thriller 🔪'
        if 'drama' in g: return 'Drama 🎭'
        return 'Other'
    
    df['Simple_Genre'] = df['Genre'].apply(clean_genre)
    
    def get_quarter(month):
        if pd.isna(month):
            return "Unknown"
        if 1 <= month <= 3: return "Jan - Mar (Q1)"
        elif 4 <= month <= 6: return "Apr - Jun (Q2)"
        elif 7 <= month <= 9: return "Jul - Sep (Q3)"
        else: return "Oct - Dec (Q4)"
        
    df['Quarter'] = df['Month_Num'].apply(get_quarter)
    return df

# --- ENHANCED ROAST GENERATOR ---
def get_personalized_roast(total_movies, avg_rating, total_spent, theater_visits, ott_watches, bad_choices, platform_count):
    roasts = []
    
    # Platform roast (toned down)
    if platform_count >= 4:
        roasts.append("🏴‍☠️ Four+ platforms? Impressive subscription collection... or creative sourcing skills!")
    
    # Movie count roasts
    if total_movies > 50:
        roasts.append("50+ movies? Touch grass exists. Your couch is probably filing a restraining order.")
    elif total_movies < 10:
        roasts.append("Less than 10 movies? Your social media algorithm has seen more Telugu content than you.")
    elif total_movies > 30:
        roasts.append("30+ movies! Either you're unemployed or you've discovered the secret of time manipulation.")
    
    # Rating-based brutal roasts
    if avg_rating < 4.0:
        roasts.append("Average rating below 4? Your movie taste has the accuracy of a broken compass.")
    elif avg_rating < 5.0:
        roasts.append("Below 5 average? You're personally funding the destruction of Telugu cinema.")
    elif avg_rating > 8.0:
        roasts.append("8+ average? Either you have divine taste or you're lying about that one disaster.")
    
    # Spending roasts
    if total_spent > 500:
        roasts.append(f"${total_spent} on tickets? The theater owner probably has your photo in their office as 'Employee of the Month'.")
    elif total_spent == 0:
        roasts.append("Zero theater visits? You're the reason multiplex owners have trust issues.")
    elif total_spent > 200:
        roasts.append(f"${total_spent}? You could've bought something that you like instead of sponsoring cinematic terrorism.")
    
    # Platform behavior roasts
    if ott_watches > theater_visits * 3:
        roasts.append("Home streaming champion! Your Netflix account is considering therapy.")
    elif theater_visits > ott_watches * 2:
        roasts.append("Theater purist! You probably have the snack counter memorized and a reserved parking spot.")
    
    # Bad movie specific roasts
    if len(bad_choices) >= 3:
        roasts.append(f"You survived {len(bad_choices)} certified disasters. NASA wants to study your pain tolerance.")
    elif len(bad_choices) >= 1:
        roasts.append("At least one catastrophic choice. We all make mistakes, but yours have IMDb evidence.")
    
    if not roasts:
        return "You're surprisingly balanced. That's... actually impressive and slightly suspicious!"
    
    # Format as HTML list (UPDATED)
    formatted_roasts = "".join([f"<li>{r}</li>" for r in roasts])
    return f"<ul>{formatted_roasts}</ul>"

# --- PLATFORM DETECTION ---
def detect_platform_behavior(full_stats):
    """Analyze platform usage patterns"""
    ott_movies = full_stats[full_stats['Home 📺'] == True]
    if ott_movies.empty:
        return False, 0, []
    
    def clean_platform(platform):
        return str(platform).strip().lower() if str(platform) != 'nan' else 'unknown'
    
    platforms = ott_movies['OTT'].apply(clean_platform).unique()
    platform_counts = ott_movies['OTT'].apply(clean_platform).value_counts()
    
    valid_platforms = [p for p in platforms if p not in ['unknown', 'nan', '', 'none']]
    
    return len(valid_platforms) >= 4, len(valid_platforms), platform_counts.to_dict()

# --- EXPORT FUNCTIONALITY ---
def create_shareable_summary(name, stats_dict):
    img = Image.new('RGB', (1080, 1350), color='#0A0A0A')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Header with gold gradient effect
    draw.text((540, 80), f"{name}'s Tollywood Wrapped", fill='#D4AF37', 
              font=font, anchor="mm")
    draw.text((540, 140), "2025 • JUDGMENT DAY", fill='#B8860B', font=font, anchor="mm")
    
    # Stats with proper spacing
    y = 220
    stats_text = [
        f"🎬 Movies Consumed: {stats_dict['total_movies']}",
        f"🎟️ Theater Pilgrimages: {stats_dict['theater_visits']}",
        f"📺 Home Binges: {stats_dict['ott_watches']}",
        f"💰 Financial Damage: ${stats_dict['total_spent']}",
        f"⭐ Taste Level: {stats_dict['avg_rating']:.1f}/10",
        f"🏆 Final Verdict: {stats_dict['rank']}"
    ]
    
    for text in stats_text:
        draw.text((100, y), text, fill='white', font=font)
        y += 70
    
    # Footer
    draw.text((540, 1250), "🎬 ROASTED BY TOLLYWOOD WRAPPED 🔥", fill='#666666', 
              font=font, anchor="mm")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

# --- MAIN APPLICATION ---
def main():
    # Load data
    df_master = load_data()
    if df_master is None:
        return
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    # PAGE 1: PREMIUM MOVIE SELECTION
    if st.session_state.step == 1:
        st.markdown("""
        <div class="cinema-header">
            <h1>🎬 TOLLYWOOD WRAPPED</h1>
            <div class="subtitle">Your 2025 Telugu Cinema Journey • Judgment Day Edition</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Premium name input
        st.markdown('<div style="text-align: center; margin: 2rem 0;"><p style="font-family: \'Cinzel\', serif; font-size: 1.5rem; color: #D4AF37; margin-bottom: 1rem;">Enter Your Name for Judgment</p></div>', unsafe_allow_html=True)
        
        name = st.text_input("", placeholder="Your name here...", label_visibility="collapsed")
        
        st.markdown('<div class="section-header">🎯 MOVIE SELECTION CHAMBER</div>', unsafe_allow_html=True)
        st.warning("⚠️ **TRUTH PROTOCOL ACTIVATED** • Only titles visible • Pure honesty required", icon="🔍")
        
        user_selections = []
        quarters = ["Jan - Mar (Q1)", "Apr - Jun (Q2)", "Jul - Sep (Q3)", "Oct - Dec (Q4)"]
        
        for q in quarters:
            q_data = df_master[df_master['Quarter'] == q].copy()
            if not q_data.empty:
                with st.expander(f"🎬 {q} • {len(q_data)} Movies Released", expanded=False):
                    # Create data editor with premium styling
                    table_data = pd.DataFrame({
                        "Movie Title": q_data['Movie Title'].values,
                        "Theatre 🎟️": [False] * len(q_data),
                        "Home 📺": [False] * len(q_data)
                    })
                    
                    edited_df = st.data_editor(
                        table_data,
                        column_config={
                            "Movie Title": st.column_config.TextColumn(
                                "🎬 Movie Title",
                                disabled=True,
                                width="large"
                            ),
                            "Theatre 🎟️": st.column_config.CheckboxColumn(
                                "Theatre 🎟️",
                                help="Watched in theater",
                                default=False,
                                width="medium"
                            ),
                            "Home 📺": st.column_config.CheckboxColumn(
                                "Home 📺", 
                                help="Watched at home (OTT/Streaming)",
                                default=False,
                                width="medium"
                            )
                        },
                        hide_index=True,
                        use_container_width=True,
                        key=f"movies_{q}",
                        height=300
                    )
                    
                    # Extract selections
                    watched_movies = edited_df[(edited_df["Theatre 🎟️"] == True) | (edited_df["Home 📺"] == True)]
                    if not watched_movies.empty:
                        for _, row in watched_movies.iterrows():
                            user_selections.append({
                                'Movie Title': row['Movie Title'],
                                'Theater 🎟️': row['Theatre 🎟️'],
                                'OTT 📺': row['Home 📺']
                            })
        
        st.markdown("---")
        
        # Premium generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔥 INITIATE ROASTING PROTOCOL 🔥", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("🚨 Name required for identification", icon="⚠️")
                elif not user_selections:
                    st.error("🎬 Select at least one movie for analysis", icon="📋")
                else:
                    # Show loading animation
                    st.markdown("""
                    <div class="loading-animation">
                        <div class="film-reel"></div>
                    </div>
                    <p style="text-align: center; color: #D4AF37; font-family: 'Rajdhani', sans-serif; font-size: 1.2rem;">
                        ANALYZING CHOICES... PREPARING ROAST...
                    </p>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(2)
                    
                    # Process selections
                    my_movies_df = pd.DataFrame(user_selections)
                    my_movies_df = my_movies_df.groupby('Movie Title').agg({
                        'Theater 🎟️': 'any',
                        'OTT 📺': 'any'
                    }).reset_index()
                    
                    st.session_state.name = name.strip()
                    st.session_state.my_movies = my_movies_df
                    st.session_state.step = 2
                    st.rerun()

    # PAGE 2: PREMIUM JUDGMENT DAY
    elif st.session_state.step == 2:
        st.balloons()
        
        # Calculate statistics
        my_df = st.session_state.my_movies
        full_stats = pd.merge(my_df, df_master, on="Movie Title", how="left")
        full_stats['Home 📺'] = full_stats['OTT 📺']
        
        theater_visits = int(full_stats['Theater 🎟️'].sum())
        ott_watches = int(full_stats['Home 📺'].sum())
        total_movies = len(full_stats)
        total_mins = int(full_stats['Run Time In Min'].sum())
        days = round((total_mins / 60) / 24, 1)
        total_spent = theater_visits * TICKET_PRICE
        avg_rating = full_stats['IMDB Ratings'].mean() if total_movies > 0 else 0
        
        # Platform detection
        multiple_platforms, platform_count, platform_breakdown = detect_platform_behavior(full_stats)
        
        # Classifications
        bad_choices = full_stats[full_stats['IMDB Ratings'] < 5.0]['Movie Title'].tolist()
        great_choices = full_stats[full_stats['IMDB Ratings'] >= 8.0]['Movie Title'].tolist()
        
        # Scoring
        score = (theater_visits * THEATER_POINTS) + (ott_watches * OTT_POINTS)
        rank = "Casual Observer 😴"
        if score > 100: rank = "Cinema Enthusiast 🎬"
        if score > 250: rank = "Unemployed Critic 🍿"
        if score > 400: rank = "Industry Plant 🤖"
        
        # Enhanced Achievement System
        user_titles = full_stats['Movie Title'].tolist()
        theater_titles = full_stats[full_stats['Theater 🎟️'] == True]['Movie Title'].tolist()
        
        badges = []
        
        # Festival Achievements
        sankranti_movies = ["Game Changer", "Daaku Maharaaj", "Sankranthiki Vasthunam"]
        if all(m in theater_titles for m in sankranti_movies):
            badges.append("🎆 SANKRANTI CHAMPION")
        
        # Genre-based achievements
        genre_counts = full_stats['Simple_Genre'].value_counts()
        if not genre_counts.empty:
            top_genre = genre_counts.index[0]
            if "Action" in top_genre and genre_counts.iloc[0] >= 5:
                badges.append("💥 ACTION ADDICT")
            elif "Comedy" in top_genre and genre_counts.iloc[0] >= 5:
                badges.append("😂 COMEDY CONNOISSEUR")
            elif "Romance" in top_genre and genre_counts.iloc[0] >= 3:
                badges.append("❤️ HOPELESS ROMANTIC")
        
        # Quality-based achievements
        if len(great_choices) >= 5:
            badges.append("💎 TASTE MASTER")
        elif len(great_choices) >= 3:
            badges.append("⭐ QUALITY HUNTER")
        
        if len(bad_choices) >= 5:
            badges.append("💀 DISASTER SURVIVOR")
        elif len(bad_choices) >= 3:
            badges.append("🍅 MASOCHIST")
        
        # Rating achievements
        if avg_rating >= 8.0:
            badges.append("🏆 ELITE CURATOR")
        elif avg_rating < 4.0:
            badges.append("🗑️ TRASH COLLECTOR")
        
        # Spending achievements
        if total_spent > 300:
            badges.append("💸 THEATER SPONSOR")
        elif total_spent == 0:
            badges.append("🏴‍☠️ FREELOADER")
        
        # Platform achievement
        if multiple_platforms:
            badges.append("🏴‍☠️ PLATFORM COLLECTOR")
        
        # Specific Movie Achievements - Based on Actual Dataset
        if any("baahubali" in m.lower() for m in user_titles):
            badges.append("⚔️ JAI MAHISHMATI")
        if any("oh" in m.lower() and ("call" in m.lower() or "they" in m.lower()) for m in user_titles):
            badges.append("🐆 HUNGRY CHEETAH")
        if any("mahavatar" in m.lower() and "narsimha" in m.lower() for m in user_titles):
            badges.append("🦁 NARASIMHA NAMO")
        if any("coolie" in m.lower() for m in user_titles):
            badges.append("💪 POWER HOUSE")
        if any("little hearts" in m.lower() for m in user_titles):
            badges.append("💖 KATYAYANI BONCHESAVA")
        if any("thandel" in m.lower() for m in user_titles):
            badges.append("🌊 BUJJI THALLI")
        if any("dude" in m.lower() for m in user_titles):
            badges.append("🎓 DEVDAS SIR")
        if "Dragon" in user_titles:
            badges.append("🐉 DRAGON SLAYER")
        if any("court" in m.lower() for m in user_titles):
            badges.append("⚖️ JUSTICE SEEKER")
        if any("kantara" in m.lower() for m in user_titles):
            badges.append("👹 DIVINE SPIRIT")
        if total_movies >= 40:
            badges.append("🎬 CINEMA MANIAC")
        
        # Header
        st.markdown(f"""
        <div class="cinema-header">
            <h1>🔥 {st.session_state.name.upper()}'S JUDGMENT</h1>
            <div class="subtitle">BRUTAL ANALYSIS COMPLETE • DAMAGE ASSESSMENT BELOW</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ACHIEVEMENTS SECTION - Enhanced Display
        if badges:
            st.markdown("""
            <div class="achievement-section">
                <div class="achievement-title">🏆 ACHIEVEMENTS UNLOCKED</div>
            """, unsafe_allow_html=True)
            
            # Create columns for badges
            cols = st.columns(min(len(badges), 3))
            for i, badge in enumerate(badges):
                col_idx = i % 3
                with cols[col_idx]:
                    st.markdown(f'<div class="achievement-badge">{badge}</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # THE BRUTAL ROAST (NOW BULLETED)
        roast_msg = get_personalized_roast(total_movies, avg_rating, total_spent, theater_visits, ott_watches, bad_choices, platform_count)
        
        st.markdown(f"""
        <div class="roast-box">
            <div class="roast-header">THE BRUTAL VERDICT</div>
            <div class="roast-text">{roast_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # PREMIUM METRICS - Enhanced Visibility
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">🎟️</span>
                <div class="metric-value">{theater_visits}</div>
                <div class="metric-label">Theater Visits</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">📺</span>
                <div class="metric-value">{ott_watches}</div>
                <div class="metric-label">Home Streams</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">💰</span>
                <div class="metric-value">${total_spent}</div>
                <div class="metric-label">Money Burned</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">⏰</span>
                <div class="metric-value">{days}</div>
                <div class="metric-label">Days Wasted</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Cinema Addiction Meter
        progress_value = min(score/400, 1.0)
        st.markdown(f'<div class="section-header">CINEMA ADDICTION METER</div>', unsafe_allow_html=True)
        st.progress(progress_value, text=f"Addiction Level: {int(progress_value*100)}% • Final Rank: {rank}")
        
        st.divider()
        
        # Platform Investigation Bureau (MODIFIED: Just List, No Efficiency)
        if ott_watches > 0:
            st.markdown('<div class="section-header">📺 Platform Investigation Bureau</div>', unsafe_allow_html=True)
            
            # Logic to build the HTML list first
            platform_html = ""
            if multiple_platforms:
                status_msg = f"<div style='color: #60A5FA; margin-bottom: 10px;'>📺 <strong>{platform_count} platforms detected</strong> • Diverse taste!</div>"
                for platform, count in platform_breakdown.items():
                    if platform not in ['unknown', 'nan', '']:
                        platform_html += f"<div style='display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;'><span>{platform.title()}</span><span style='color: #D4AF37;'>{count}</span></div>"
            else:
                status_msg = f"<div style='color: #10B981; margin-bottom: 10px;'>✅ <strong>{platform_count} platforms</strong> • Focused viewer</div>"
                for platform, count in platform_breakdown.items():
                    if platform not in ['unknown', 'nan', '']:
                        platform_html += f"<div style='text-align: center; font-size: 2rem; color: #D4AF37; margin: 10px 0;'>{count}</div><div style='text-align: center;'>{platform.title()}</div>"

            # Render ONLY the List box (Subscription Efficiency removed)
            st.markdown(f"""
            <div class="chart-container">
                <h3 style="color: #D4AF37; font-family: 'Cinzel', serif; margin-top: 0; text-align: center;">Platform Usage Analysis</h3>
                {status_msg}
                <div style="margin-top: 15px; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem;">
                    {platform_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # The Hall of Shame vs Hall of Fame (FIXED: REMOVED OUTER CHART-CONTAINER)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🍅 Hall of Shame")
            if bad_choices:
                st.markdown(f"""
                <div class="error-box">
                    <h4>DISASTERS SURVIVED: {len(bad_choices)}</h4>
                </div>
                """, unsafe_allow_html=True)
                for movie in bad_choices:
                    rating = full_stats[full_stats['Movie Title']==movie]['IMDB Ratings'].iloc[0]
                    st.markdown(f"💀 **{movie}** - {rating:.1f}/10")
            else:
                st.markdown("""
                <div class="success-box">
                    <h4>✨ NO DISASTERS ON RECORD</h4>
                    <p>Impressive taste detected!</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("💎 Hall of Fame")
            if great_choices:
                st.markdown(f"""
                <div class="success-box">
                    <h4>MASTERPIECES DISCOVERED: {len(great_choices)}</h4>
                </div>
                """, unsafe_allow_html=True)
                for movie in great_choices:
                    rating = full_stats[full_stats['Movie Title']==movie]['IMDB Ratings'].iloc[0]
                    st.markdown(f"⭐ **{movie}** - {rating:.1f}/10")
            else:
                st.markdown("""
                <div class="error-box">
                    <h4>😔 NO GEMS FOUND</h4>
                    <p>You missed all the good stuff!</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Financial Damage Assessment (RESTORED)
        st.markdown('<div class="section-header">💸 Financial Damage Assessment</div>', unsafe_allow_html=True)
        
        theater_disasters = full_stats[(full_stats['Theater 🎟️']==True) & (full_stats['IMDB Ratings']<6)]
        wasted_money = len(theater_disasters) * TICKET_PRICE
        
        if not theater_disasters.empty:
            st.markdown(f"""
            <div class="error-box">
                <h3 style="color: white; margin: 0;">💸 Money Wasted: ${wasted_money}</h3>
                <p style="margin: 15px 0; font-style: italic; font-size: 1.1rem;">
                    <em>"Ivi theater lo choosvanate... aa gunde bratakali..."</em>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**💀 Your Expensive Mistakes:**")
            for _, movie in theater_disasters.iterrows():
                st.markdown(f"• **{movie['Movie Title']}** - {movie['IMDB Ratings']:.1f}/10")
        else:
            st.markdown("""
            <div class="success-box">
                <h3 style="color: white; margin: 0;">✨ Financial Genius!</h3>
                <p style="margin: 15px 0;">You avoided all theater disasters. Your wallet is proud!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Export Section
        st.markdown('<div class="section-header">📤 Share Your Judgment</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📱 CREATE ROAST IMAGE", use_container_width=True):
                stats_dict = {
                    'total_movies': total_movies,
                    'theater_visits': theater_visits,
                    'ott_watches': ott_watches,
                    'total_spent': total_spent,
                    'avg_rating': avg_rating,
                    'rank': rank
                }
                img_data = create_shareable_summary(st.session_state.name, stats_dict)
                
                st.image(f"data:image/png;base64,{img_data}", caption="Your Premium Roast Summary")
                
                st.download_button(
                    label="⬇️ DOWNLOAD ROAST",
                    data=base64.b64decode(img_data),
                    file_name=f"{st.session_state.name}_tollywood_roast_2025.png",
                    mime="image/png",
                    use_container_width=True
                )
        
        with col2:
            export_data = {
                "name": st.session_state.name,
                "judgment_date": datetime.now().strftime("%Y-%m-%d"),
                "summary": {
                    "total_movies": total_movies,
                    "theater_visits": theater_visits,
                    "ott_watches": ott_watches,
                    "total_spent": total_spent,
                    "avg_rating": round(avg_rating, 2),
                    "rank": rank,
                    "platform_count": platform_count,
                    "score": score
                },
                "roast": roast_msg,
                "achievements": badges,
                "hall_of_shame": bad_choices,
                "hall_of_fame": great_choices
            }
            
            st.download_button(
                label="📄 DOWNLOAD REPORT",
                data=json.dumps(export_data, indent=2),
                file_name=f"{st.session_state.name}_tollywood_judgment.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 JUDGE ANOTHER VICTIM", use_container_width=True):
                for key in ['step', 'name', 'my_movies']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()
