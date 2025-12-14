import streamlit as st
import pandas as pd
import os
import calendar
import altair as alt

# --- CONFIGURATION ---
TICKET_PRICE = 18  # Dollars
THEATER_POINTS = 10
OTT_POINTS = 5

st.set_page_config(page_title="2025 Tollywood Wrapped", page_icon="🪁", layout="centered")

# --- CUSTOM CSS (FIXED VISIBILITY) ---
st.markdown("""
<style>
    /* Roast Box */
    .roast-box {
        background-color: #1E1E1E !important; 
        color: #FFFFFF !important;            
        border-left: 8px solid #FF4B4B;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    .roast-header {
        color: #FF4B4B !important;
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .roast-text {
        font-size: 18px;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Achievement Badge */
    .badge {
        background: linear-gradient(45deg, #FFD700, #FF8C00);
        color: #000;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .badge-title { font-size: 20px; text-transform: uppercase; }
    .badge-desc { font-size: 14px; opacity: 0.9; }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #FF4B4B !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. LOAD DATA ---
@st.cache_data
def load_data():
    # This gets the folder where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # This combines the folder path with the filename
    file_path = os.path.join(current_dir, "Cinemawrapped.csv")

    df = pd.read_csv(file_path)
    
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
        if 'romance' in g or 'romantic' in g: return 'Romance ❤️'
        if 'thriller' in g: return 'Thriller 🔪'
        if 'drama' in g: return 'Drama 🎭'
        if 'horror' in g: return 'Horror 👻'
        return 'Other'
    
    df['Simple_Genre'] = df['Genre'].apply(clean_genre)
    
    def get_quarter(month):
        if 1 <= month <= 3: return "Jan - Mar (Q1)"
        elif 4 <= month <= 6: return "Apr - Jun (Q2)"
        elif 7 <= month <= 9: return "Jul - Sep (Q3)"
        else: return "Oct - Dec (Q4)"
        
    df['Quarter'] = df['Month_Num'].apply(get_quarter)
    return df

df_master = load_data()

if df_master is None:
    st.error("⚠️ `Cinemawrapped.csv` not found!")
    st.stop()

if 'step' not in st.session_state:
    st.session_state.step = 1

# --- PAGE 1: INPUT ---
if st.session_state.step == 1:
    st.title("🪁 2025 Tollywood Roast")
    st.markdown("### 🎬 Select what you watched")
    
    name = st.text_input("Name:", placeholder="Enter your name")
    
    user_selections = []
    quarters = ["Jan - Mar (Q1)", "Apr - Jun (Q2)", "Jul - Sep (Q3)", "Oct - Dec (Q4)"]
    
    for q in quarters:
        q_data = df_master[df_master['Quarter'] == q].copy()
        if not q_data.empty:
            with st.expander(f"📅 {q}", expanded=False):
                display_df = pd.DataFrame({
                    "Movie Title": q_data['Movie Title'].values,
                    "Theater 🎟️": [False] * len(q_data),
                    "OTT 📺": [False] * len(q_data)
                })
                
                edited_df = st.data_editor(
                    display_df,
                    column_config={
                        "Movie Title": st.column_config.TextColumn(disabled=True),
                        "Theater 🎟️": st.column_config.CheckboxColumn(default=False),
                        "OTT 📺": st.column_config.CheckboxColumn(default=False)
                    },
                    hide_index=True,
                    use_container_width=True,
                    key=f"edit_{q}"
                )
                
                watched = edited_df[(edited_df["Theater 🎟️"] == True) | (edited_df["OTT 📺"] == True)]
                if not watched.empty:
                    user_selections.append(watched)

    st.divider()
    if st.button("Generate My Stats 🚀", type="primary", use_container_width=True):
        if not name: st.error("Enter name!")
        elif not user_selections: st.error("Select at least one movie!")
        else:
            st.session_state.name = name
            st.session_state.my_movies = pd.concat(user_selections)
            st.session_state.step = 2
            st.rerun()

# --- PAGE 2: DASHBOARD ---
elif st.session_state.step == 2:
    st.balloons()
    
    # 1. CALCULATE EVERYTHING
    my_df = st.session_state.my_movies
    full_stats = pd.merge(my_df, df_master, on="Movie Title", how="left")
    
    # Basic Stats
    theater_visits = full_stats['Theater 🎟️'].sum()
    ott_watches = full_stats['OTT 📺'].sum()
    total_movies = len(full_stats)
    total_mins = full_stats['Run Time In Min'].sum()
    days = round((total_mins / 60) / 24, 1)
    
    # Financials
    total_spent = theater_visits * TICKET_PRICE
    
    # Ratings & Verdicts
    def classify_movie(rating):
        if rating >= 7.5: return "Hit 🔥"
        elif rating >= 5.0: return "Average 😐"
        else: return "Flop 🍅"
    
    full_stats['Verdict'] = full_stats['IMDB Ratings'].apply(classify_movie)
    avg_rating = full_stats['IMDB Ratings'].mean()
    
    # Score
    score = (theater_visits * THEATER_POINTS) + (ott_watches * OTT_POINTS)
    
    # Rank
    rank = "Casual Viewer"
    if score > 100: rank = "Cinephile"
    if score > 250: rank = "Unemployed"
    if score > 400: rank = "Industry Plant"

    # --- DISPLAY START ---
    st.markdown(f"# 🎬 {st.session_state.name}'s Wrapped")
    
    # 1. ACHIEVEMENT UNLOCKED (SANKRANTI BADGE)
    theater_titles = full_stats[full_stats['Theater 🎟️'] == True]['Movie Title'].tolist()
    
    sankranti_combo = ["Game Changer", "Daaku Maharaaj", "Sankranthiki Vasthunam"]
    has_sankranti_badge = all(m in theater_titles for m in sankranti_combo)
    
    if has_sankranti_badge:
        st.markdown("""
        <div class="badge">
            <div class="badge-title">🏆 Sankranti Winner 🏆</div>
            <div class="badge-desc">You watched Game Changer, Daaku Maharaaj & Sankranthiki Vasthunam in Theaters!</div>
        </div>
        """, unsafe_allow_html=True)
        score += 50 # Bonus points

    # 2. ROAST HEADER
    roast_msg = f"You watched <b>{total_movies}</b> movies."
    if avg_rating < 5.0: roast_msg += " Your taste is tragic. Who hurt you?"
    elif total_spent > 300: roast_msg += f" You spent <b>${total_spent}</b>. The economy thanks you."
    else: roast_msg += " You are painfully average."
        
    st.markdown(f"""
    <div class="roast-box">
        <div class="roast-header">🔥 The Verdict</div>
        <div class="roast-text">{roast_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. KEY STATS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Theater", int(theater_visits))
    c2.metric("OTT", int(ott_watches))
    c3.metric("Money Blown", f"${total_spent}")
    c4.metric("Days Lost", f"{days}")
    
    st.progress(min(score/400, 1.0))
    st.caption(f"Rank: **{rank}**")

    st.divider()

    # --- 4. GENRE VIBE ---
    st.subheader("🧬 Your Movie DNA")
    c_genre1, c_genre2 = st.columns([2, 1])
    
    with c_genre1:
        genre_counts = full_stats['Simple_Genre'].value_counts()
        if not genre_counts.empty:
            top_genre = genre_counts.idxmax()
            st.write(f"You are a **{top_genre}** fan.")
            
            # Altair Bar Chart
            genre_data = genre_counts.reset_index()
            genre_data.columns = ['Genre', 'Count']
            c = alt.Chart(genre_data).mark_bar().encode(
                x='Count',
                y=alt.Y('Genre', sort='-x'),
                color=alt.Color('Genre', legend=None)
            ).properties(height=200)
            st.altair_chart(c, use_container_width=True)
        else:
            st.write("Not enough data.")

    with c_genre2:
        st.write("**Top Genres:**")
        st.dataframe(genre_counts, use_container_width=True)

    st.divider()

    # --- 5. MASS vs CLASS ---
    st.subheader("⚖️ Mass vs Class Index")
    avg_bms = full_stats['BMS Ratings'].mean()
    avg_imdb = full_stats['IMDB Ratings'].mean()
    gap = avg_bms - avg_imdb
    
    col_mass1, col_mass2 = st.columns(2)
    col_mass1.metric("BMS (Fans)", f"{avg_bms:.1f}")
    col_mass2.metric("IMDb (Critics)", f"{avg_imdb:.1f}")
    
    st.write("") 
    if gap > 2.0:
        st.error(f"🚨 **Verdict: MASS FANBOY** 🚨")
        st.caption(f"Difference: {gap:.1f}. You love movies that critics hate. (Jai Balayya?)")
    elif gap < 0.5:
        st.success(f"🍷 **Verdict: CLASS AUDIENCE** 🍷")
        st.caption("You agree with the critics. Very sophisticated.")
    else:
        st.info(f"⚖️ **Verdict: NEUTRAL**")
        st.caption("You enjoy a balance of both.")

    st.divider()

    # --- 6. FINANCIAL RUIN ---
    st.subheader("💸 Regret Meter")
    theater_df = full_stats[full_stats['Theater 🎟️'] == True]
    bad_theater = theater_df[theater_df['IMDB Ratings'] < 6.0]
    wasted = len(bad_theater) * TICKET_PRICE
    
    c_fin1, c_fin2 = st.columns(2)
    c_fin1.metric("Total Spent", f"${total_spent}")
    c_fin2.metric("Wasted on Flops", f"${wasted}", help="Movies < 6.0 Rating")
    
    if wasted > 0:
        st.warning(f"You burned ${wasted} on {len(bad_theater)} bad movies.")
        with st.expander("See what you wasted money on"):
            st.dataframe(bad_theater[['Movie Title', 'IMDB Ratings']], hide_index=True)

    st.divider()

    # --- 7. SUBSCRIPTION AUDIT ---
    st.subheader("📺 Subscription Audit")
    ott_df = full_stats[full_stats['OTT 📺'] == True]
    
    if not ott_df.empty:
        def clean_plat(x): return str(x).strip() if str(x) != 'nan' else "Unknown"
        ott_df['Platform'] = ott_df['OTT'].apply(clean_plat)
        counts = ott_df['Platform'].value_counts()
        
        if len(counts) >= 4:
            st.error(f"⚠️ **Suspicious:** {len(counts)} different apps? Likely **iBomma** user.")
        
        cols = st.columns(len(counts))
        for i, (p, c) in enumerate(counts.items()):
            if i < len(cols): cols[i].metric(p, c)
    else:
        st.info("No OTT watches.")

    st.divider()

    # --- 8. TIMELINE ---
    st.subheader("📅 Seasonality")
    monthly_counts = full_stats.groupby('Month_Name')['Movie Title'].count()
    month_order = [calendar.month_abbr[i] for i in range(1, 13)]
    monthly_counts = monthly_counts.reindex(month_order, fill_value=0)
    
    timeline_data = pd.DataFrame({'Month': monthly_counts.index, 'Count': monthly_counts.values})
    c = alt.Chart(timeline_data).mark_bar().encode(
        x=alt.X('Month', sort=month_order),
        y='Count',
        color=alt.value('#FF4B4B')
    ).properties(height=200)
    st.altair_chart(c, use_container_width=True)

    if st.button("Start Over 🔄"):
        st.session_state.step = 1
        st.rerun()