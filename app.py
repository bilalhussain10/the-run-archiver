import streamlit as st
import datetime
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rundata.db")


def _get_secret(key):
    """Read a credential from Streamlit secrets, falling back to env vars."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key)


TURSO_DATABASE_URL = _get_secret("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = _get_secret("TURSO_AUTH_TOKEN")
USING_TURSO = bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN)


# ---------- DB helpers ----------
def get_conn():
    """
    Returns a live connection.
    - If TURSO_DATABASE_URL / TURSO_AUTH_TOKEN are configured (via st.secrets
      or env vars), connect to the permanent, cloud-hosted Turso database.
    - Otherwise fall back to a local SQLite file (handy for local dev, but
      NOT persistent on most free cloud hosts).
    """
    if USING_TURSO:
        import libsql
        conn = libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT,
            run_type TEXT,
            distance TEXT,
            pace TEXT,
            feel TEXT,
            result TEXT
        )
    """)
    conn.commit()
    return conn

def insert_run(run_date, run_type, distance, pace, feel, result):
    conn = get_conn()
    conn.execute(
        "INSERT INTO runs (run_date, run_type, distance, pace, feel, result) VALUES (?, ?, ?, ?, ?, ?)",
        (run_date, run_type, distance, pace, feel, result),
    )
    conn.commit()
    conn.close()

def fetch_runs():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, run_date, run_type, distance, pace, feel, result FROM runs ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows

def delete_run(run_id):
    conn = get_conn()
    conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
    conn.commit()
    conn.close()

# ---------- Quotes ----------
QUOTES = [
    '"You are in danger of living a life so comfortable and soft that you will die without ever realizing your true potential." - David Goggins',
    '"I hated every minute of training, but I said, \'Don\'t quit. Suffer now and live the rest of your life as a champion.\'" - Muhammad Ali',
    '"The only limit to our realization of tomorrow will be our doubts of today." - Franklin D. Roosevelt',
    '"The pain you feel today will be the strength you feel tomorrow." - Unknown',
    '"When you think that you are done, you\'re only at 40 percent into what your body\'s capable of doing." - David Goggins',
    '"He who is not courageous enough to take risks will accomplish nothing in life." - Muhammad Ali',
    '"It always seems impossible until it\'s done." - Nelson Mandela',
    '"If you can\'t fly then run, if you can\'t run then walk, if you can\'t walk then crawl, but whatever you do you have to keep moving forward." - Martin Luther King Jr.',
    '"Comfort zones are where dreams go to die." - David Goggins',
    '"Champions aren\'t made in gyms. Champions are made from something they have deep inside them-a desire, a dream, a vision." - Muhammad Ali',
    '"Do not pray for an easy life, pray for the strength to endure a difficult one." - Bruce Lee',
    '"Strength does not come from winning. Your struggles develop your strengths." - Arnold Schwarzenegger',
    '"You must build calluses on your brain just like you do on your hands." - David Goggins',
    '"Don\'t count the days, make the days count." - Muhammad Ali',
    '"Hard times create strong men. Strong men create good times." - G. Michael Hopf',
    '"The only way to define your limits is by going beyond them." - Arthur C. Clarke',
    '"Pain is the definition of growth." - David Goggins',
    '"I am the greatest, I said that even before I knew I was." - Muhammad Ali',
    '"If it doesn\'t challenge you, it won\'t change you." - Fred DeVito',
    '"The man who moves a mountain begins by carrying away small stones." - Confucius',
    '"You have to be willing to go to war with yourself before you can find peace." - David Goggins',
    '"Impossible is just a big word thrown around by small men who find it easier to live in the world they\'ve been given than to explore the power they have to change it." - Muhammad Ali',
    '"Continuous effort, not strength or intelligence, is the key to unlocking our potential." - Winston Churchill',
    '"Fall seven times, stand up eight." - Japanese Proverb',
    '"To find peace you must go through friction." - David Goggins',
    '"The man who has no imagination has no wings." - Muhammad Ali',
    '"Great things are done by a series of small things brought together." - Vincent van Gogh',
    '"Out of suffering have emerged the strongest souls; the most massive characters are seared with scars." - Kahlil Gibran',
    '"Motivation is crap. Inspiration is crap. You have to be driven." - David Goggins',
    '"Only a man who knows what it is like to be defeated can reach down to the bottom of his soul and come up with the extra ounce of power it takes to win when the match is even." - Muhammad Ali',
]

# ---------- Page config & style (matches the original Tkinter look) ----------
st.set_page_config(page_title="The Run Archiver", layout="centered")

st.markdown(
    """
    <style>
    :root {
        --ivory: #FFFFF0;
        --maroon: #800000;
        --navy: #000080;
        --darkblue: #00008B;
        --magenta: #FF00FF;
        --font-quote: "Times New Roman", Times, serif;
        --font-date: Constantia, Georgia, serif;
        --font-label: Cambria, Georgia, serif;
        --font-entry: Bahnschrift, "Segoe UI", Verdana, sans-serif;
        --font-button: Impact, "Arial Narrow Bold", "Haettenschweiler", sans-serif;
    }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: var(--ivory) !important;
    }

    /* Quote */
    .quote-box {
        color: var(--maroon);
        font-family: var(--font-quote);
        font-style: italic;
        font-weight: bold;
        font-size: 22px;
        text-align: center;
        padding: 20px 10px 5px 10px;
    }

    /* Date */
    .date-box {
        color: black;
        font-family: var(--font-date);
        font-weight: bold;
        font-size: 20px;
        text-align: center;
        padding-bottom: 15px;
    }

    /* Field labels (Run Type, Distance, etc.) */
    [data-testid="stWidgetLabel"] p {
        font-family: var(--font-label) !important;
        color: black !important;
        font-size: 18px !important;
    }

    /* All text inputs: ivory text, Bahnschrift, centered, thick black border */
    div[data-testid="stTextInput"] input {
        font-family: var(--font-entry) !important;
        color: var(--ivory) !important;
        text-align: center !important;
        border: 3px solid black !important;
        border-radius: 4px !important;
    }

    /* Alternate maroon / dark-blue entry backgrounds, same pattern as the original */
    .st-key-type_field input,
    .st-key-pace_field input,
    .st-key-success_field input {
        background-color: var(--maroon) !important;
    }
    .st-key-dist_field input,
    .st-key-feel_field input {
        background-color: var(--darkblue) !important;
    }

    /* LOG RUN button: centered and Impact font */
    .stFormSubmitButton button {
        font-family: var(--font-button) !important;
        font-size: 20px !important;
        color: var(--ivory) !important;
        background-color: var(--navy) !important;
        border: none !important;
        border-radius: 4px !important;
        width: 40% !important;
        padding: 10px 0 !important; 
        display: block !important;
        margin: 0 auto !important;
        text-align: center !important;
    }
    .stFormSubmitButton button:hover {
        background-color: #000060 !important;
        color: var(--ivory) !important;
    }

    /* Success/Failure/Invalid response banners styled like the old magenta 'response' label */
    .response-box {
        font-family: var(--font-button);
        font-size: 20px;
        text-align: center;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Keep one quote for the whole session instead of re-rolling on every rerun
if "quote" not in st.session_state:
    st.session_state.quote = random.choice(QUOTES)

st.markdown(f"<div class='quote-box'>{st.session_state.quote}</div>", unsafe_allow_html=True)

today = datetime.datetime.now().strftime("%a, %d %b, %y")
st.markdown(f"<div class='date-box'>{today}</div>", unsafe_allow_html=True)



# ---------- Form ----------
with st.form("run_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        with st.container(key="type_field"):
            run_type = st.text_input("Run Type:")
        with st.container(key="dist_field"):
            distance = st.text_input("Distance in Meters:")
    with col2:
        with st.container(key="pace_field"):
            pace = st.text_input("Time & Pace:")
        with st.container(key="feel_field"):
            feel = st.text_input("Experience & Conditions:")

    with st.container(key="success_field"):
        success_input = st.text_input("Was it A Success? yes OR no")

    submitted = st.form_submit_button("LOG RUN")

    if submitted:
        if not run_type.strip() or not distance.strip() or not pace.strip():
            st.error("Run Type, Distance, and Time & Pace are required.")
        else:
            answer = success_input.strip().lower()
            if answer == "yes":
                result = "Success"
                st.markdown(
                    "<div class='response-box' style='color:blue;'>CONGRATULATIONS!</div>",
                    unsafe_allow_html=True,
                )
            elif answer == "no":
                result = "Failure"
                st.markdown(
                    "<div class='response-box' style='color:red;'>Hard Luck, kill it next time</div>",
                    unsafe_allow_html=True,
                )
            else:
                result = "Unknown"
                if success_input.strip():
                    st.markdown(
                        "<div class='response-box' style='color:black;'>Invalid Response</div>",
                        unsafe_allow_html=True,
                    )

            insert_run(today, run_type.strip(), distance.strip(), pace.strip(), feel.strip(), result)
            st.rerun()

# ---------- History ----------
st.markdown(
    "<h2 style='font-family: Cambria, Georgia, serif; color: black; text-align:center;'>History</h2>",
    unsafe_allow_html=True,
)

runs = fetch_runs()

if not runs:
    st.info("")
else:
    for run_id, run_date, run_type, distance, pace, feel, result in runs:
        c1, c2 = st.columns([9, 1])
        with c1:
            st.markdown(
                f"<div style='font-family: Cambria, Georgia, serif; color: var(--ivory); background-color: var(--maroon); "
                f"font-size:16px; padding: 8px 10px; border-radius:6px;'>"
                f"<b>{run_date}</b> | {run_type} | {distance} m | {pace} | {feel} | {result}"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("🗑", key=f"del_{run_id}"):
                delete_run(run_id)
                st.rerun()
