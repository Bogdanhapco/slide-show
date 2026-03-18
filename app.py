import streamlit as st
from groq import Groq
import re
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Genis 2.0 – Slideshow Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    [data-testid="stSidebar"] { min-width:300px !important; max-width:300px !important; }
    .block-container { max-width:860px !important; padding:2rem; }

    .big-title {
        text-align:center; font-size:3.2rem; font-weight:800;
        background:linear-gradient(135deg,#00f5d4 0%,#7b2ff7 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        font-family:'Syne',sans-serif; letter-spacing:-1px; margin-bottom:0.2rem;
    }
    .subtitle {
        text-align:center; font-size:1rem; color:#888; margin-bottom:2rem;
        font-family:'Space Mono',monospace; letter-spacing:2px; text-transform:uppercase;
    }
    .stButton > button {
        width:100%; height:3.5rem; font-size:1.1rem; font-weight:bold;
        background:linear-gradient(135deg,#00f5d4 0%,#7b2ff7 100%);
        color:#0a0a0a; border:none; border-radius:8px; margin-top:1rem;
        font-family:'Space Mono',monospace; letter-spacing:1px;
    }
    .stButton > button:hover {
        opacity:.88; transform:translateY(-2px);
        box-shadow:0 6px 20px rgba(0,245,212,.3);
    }
    .info-card {
        background:#0d1117; padding:1.2rem; border-radius:10px;
        border-left:3px solid #00f5d4; margin:1rem 0;
        font-family:'Space Mono',monospace; font-size:.84rem; color:#ccc;
    }
</style>
""", unsafe_allow_html=True)

# ── API setup ──────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    api_available = True
except Exception:
    api_available = False

MODEL = "openai/gpt-oss-120b"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Genis 2.0")
    st.markdown("---")
    st.markdown("### ⚡ Features")
    st.markdown("""
- 🤖 new Genis 3
- 🎨 Fully AI-designed unique themes
- 🎬 Per-slide entrance animations
- ✨ FX toggle inside slideshow
- ⌨️ Keyboard + click + swipe nav
- ⏩ Auto-advance mode
- 📥 Download as .html
- 🖨️ Print → PDF export
    """)
    st.markdown("---")
    st.markdown("### 🔑 Setup")
    st.markdown("""
Add to Streamlit secrets:
```
GROQ_API_KEY = "your-key-here"
```
Get key free at [console.groq.com](https://console.groq.com)
    """)
    st.markdown("---")
    st.markdown("### 📂 Using the file")
    st.info("Double-click the `.html` file → opens in any browser.\n\nBrowser → Print → Save as PDF to share.")
    st.markdown("---")
    if not api_available:
        st.error("⚠️ GROQ_API_KEY not configured")
    else:
        st.success("✅ Genis 3 120B Ready")
    st.markdown("---")
    st.caption("© 2025 Genis 2.0")

# ── Main UI ────────────────────────────────────────────────────────────────────
st.markdown('<div class="big-title">🎯 Genis 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI HTML Slideshow Generator</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### 👤 Author")
author_name = st.text_input(
    "Your name (shown on title slide)",
    placeholder="e.g. John Smith"
)

st.markdown("### 📝 Topic")
topic = st.text_area(
    "Describe your slideshow:",
    placeholder="e.g. The future of renewable energy and why it will reshape the global economy by 2040",
    height=110,
    label_visibility="collapsed"
)

with st.expander("⚙️ Options", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        num_slides = st.number_input("Number of slides", min_value=3, max_value=40, value=10)
        pres_style = st.selectbox(
            "Content tone",
            ["Professional", "Creative", "Educational", "Storytelling", "Technical", "Inspirational"]
        )
    with col2:
        enable_animations = st.toggle("🎬 Animations", value=True)
        auto_advance = st.toggle("⏩ Auto-advance", value=False)
        if auto_advance:
            advance_secs = st.slider("Seconds per slide", 2, 20, 6)
        else:
            advance_secs = 0

    st.markdown("**🎨 Mood hint** *(optional — leave blank for full AI surprise)*")
    mood_hint = st.text_input(
        "mood",
        placeholder="e.g. dark and dramatic  /  warm retro 70s  /  electric neon  /  clean minimal",
        label_visibility="collapsed"
    )

# ── Generate ───────────────────────────────────────────────────────────────────
if st.button("🚀 Generate Slideshow"):
    if not api_available:
        st.error("❌ GROQ_API_KEY not set in Streamlit secrets.")
    elif not topic or len(topic.strip()) < 10:
        st.warning("⚠️ Please enter a more detailed topic.")
    elif not author_name or len(author_name.strip()) < 2:
        st.warning("⚠️ Please enter your name.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()

        try:
            # ── Step 1: Generate structured slide content ────────────────────
            status.text("🧠 Writing slide content...")
            progress_bar.progress(10)

            content_prompt = f"""You are a world-class presentation writer.

Topic: {topic}
Tone: {pres_style}
Slides: {num_slides}
Author: {author_name.strip()}

Write exactly {num_slides} slides. Return ONLY a valid JSON array. No markdown, no explanation, no code fences.

Each slide is an object with these fields:
{{
  "index": 0,
  "type": "title" | "statement" | "split" | "grid" | "quote" | "timeline" | "stats" | "closing",
  "title": "short punchy title",
  "subtitle": "optional tagline or empty string",
  "body": "one punchy paragraph OR empty string",
  "bullets": ["short point", "short point"],
  "stats": [{{"value": "82%", "label": "of companies use AI"}}],
  "quote": "the quote text or empty string",
  "quote_author": "Name, Title or empty string",
  "grid_items": [{{"icon": "🚀", "text": "short label"}}],
  "timeline_items": [{{"year": "2020", "event": "short description"}}],
  "accent_word": "one impactful word from the title"
}}

STRICT RULES:
- Slide index 0 MUST be type "title"
- Last slide MUST be type "closing"
- Use a VARIETY of types across the deck — no same type twice in a row
- body and bullets should NOT both be filled — pick one or neither
- Keep all text SHORT and PUNCHY — this is a visual slideshow not an essay
- stats slides: 2-4 dramatic numbers with context labels
- grid slides: exactly 4-6 items with relevant emojis as icons
- quote slides: a real or well-paraphrased relevant quote
- timeline slides: 4-5 key events in chronological order
- For unused fields use empty string "" or empty array []

Return the JSON array only."""

            content_resp = client.chat.completions.create(
                messages=[{"role": "user", "content": content_prompt}],
                model=MODEL,
                temperature=0.7,
                max_tokens=6000,
            )
            raw = content_resp.choices[0].message.content.strip()
            raw = re.sub(r'^```[a-z]*\n?', '', raw)
            raw = re.sub(r'\n?```$', '', raw.strip())

            try:
                slides_data = json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r'\[.*\]', raw, re.DOTALL)
                if match:
                    slides_data = json.loads(match.group())
                else:
                    st.error("❌ Failed to parse slide content. Please try again.")
                    progress_bar.empty(); status.empty(); st.stop()

            progress_bar.progress(35)

            # ── Step 2: Generate full HTML slideshow ─────────────────────────
            status.text("🎨 Designing your slideshow — this may take ~30 seconds...")
            progress_bar.progress(45)

            mood_line = (
                f'Mood/vibe requested by user: "{mood_hint.strip()}" — honor this strongly.'
                if mood_hint.strip()
                else "No mood hint given — go wild. Invent something bold, unique, and memorable. Surprise the user."
            )

            anim_block = """
━━━ ANIMATIONS ━━━
Use CSS @keyframes triggered by JavaScript adding class "active" to the visible slide div.
Only the active slide animates — others are display:none.

Per slide type entrance animations:
- title: h1 does scale(1.15)→scale(1) + blur(10px)→blur(0) + opacity 0→1 over 0.7s
- statement: giant text slams in with translateY(40px)→0 + opacity 0→1, slight overshoot
- split: left panel slides from translateX(-60px)→0, right panel from translateX(60px)→0, simultaneously
- grid: each card scales from 0.8→1 + opacity 0→1, staggered 0.08s delay per card
- quote: quotation mark symbol scales in first (0.5s), then quote text fades up (delay 0.4s)
- stats: numbers count up from 0 to their value using JS requestAnimationFrame on slide enter
- timeline: items fade+slide in sequentially from left, 0.15s stagger
- closing: same as title

Body text / bullet rows: each staggered, translateY(20px)→0, opacity 0→1, 0.1s delay increments

FX Toggle button:
- Fixed position, bottom-right corner, z-index 9999
- Small elegant pill button, id="fx-btn"
- Toggles class "no-anim" on <body>
- CSS: body.no-anim * { animation-duration:0.001s !important; transition-duration:0.001s !important; }
- Shows "✨ FX" when animations ON, "○ FX" when OFF
- Default state: animations ON
""" if enable_animations else """
━━━ ANIMATIONS ━━━
No animations. Everything appears instantly when slide becomes active.
Still include the #fx-btn toggle button (bottom-right), default state OFF showing "○ FX".
User can click to enable if they want.
"""

            auto_block = f"""
━━━ AUTO-ADVANCE ━━━
After setting up navigation, add this:
setInterval(() => {{ if (currentIndex < totalSlides - 1) goTo(currentIndex + 1); }}, {advance_secs * 1000});
""" if auto_advance and advance_secs > 0 else "// No auto-advance."

            html_prompt = f"""You are an elite front-end designer and creative director. Generate a complete, self-contained, production-quality HTML5 slideshow file.

{mood_line}

SLIDE DATA (JSON):
{json.dumps(slides_data, ensure_ascii=False, indent=2)}

AUTHOR: {author_name.strip()}
TOTAL SLIDES: {len(slides_data)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL DESIGN — INVENT FROM SCRATCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Design a unique visual identity. You must choose:

1. COLOR PALETTE — 2-3 main colors + neutrals. Be bold and specific. Examples of directions:
   - Deep navy + electric lime + white
   - Warm cream + burnt sienna + dark chocolate  
   - Pure black + hot magenta + silver
   - Forest green + gold + off-white
   - Rich indigo + coral + soft grey
   NOT generic blue/purple gradients. Pick something with personality.

2. TYPOGRAPHY — Two Google Fonts. Examples of pairings:
   - Bebas Neue (titles) + Lato (body)
   - Playfair Display (titles) + DM Sans (body)
   - Anton (titles) + IBM Plex Sans (body)
   - Fraunces (titles) + Inter (body)
   - Clash Display (titles) + Manrope (body)
   Import via @import in <style>.

3. SIGNATURE GRAPHIC MOTIF — one recurring visual element across ALL slides. Pick ONE:
   - Large diagonal color band slicing across corner of each slide
   - Floating abstract SVG blob shapes as background accents
   - Fine dot-grid pattern as slide background texture (CSS radial-gradient dots)
   - Oversized blurred circle gradients in background corners
   - Bold geometric half-circle or quarter-circle decorative element
   - Thin rule lines framing content areas
   - Large faded watermark numeral (slide number) in background
   - Noise/grain texture overlay (SVG feTurbulence or CSS)
   The motif must appear consistently but subtly on every slide.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SLIDE LAYOUTS — ONE PER TYPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Each type gets a DISTINCT, purpose-built layout:

"title" →
  Full-bleed hero. Title is MASSIVE (8-12vw). Centered or left-aligned with dramatic spacing.
  Subtitle below in lighter weight. "by {author_name.strip()}" as small elegant byline.
  Use the signature motif prominently here.

"statement" →
  ONE big sentence dominates 70-80% of the slide area.
  Font size: 5-8vw. Minimal everything else — maybe just a thin rule or accent color block.
  The text IS the design on this slide.

"split" →
  Exactly 50/50 vertical split.
  Left panel: title + body text OR bullet rows.
  Right panel: pure visual design — a large solid color block, big SVG abstract shape,
  oversized accent word (10-15vw, barely visible), geometric art, gradient — NO body text on right.

"grid" →
  Render grid_items as cards in CSS grid (2×2 or 2×3 depending on count).
  Each card: big emoji (2-3rem) + label text. Cards have subtle border or background.
  Title above the grid.

"quote" →
  Giant decorative quotation mark (" " ") as a design element — large, accent color, positioned behind text.
  Quote text: large, elegant, italic, centered or left-aligned.
  Attribution: small, below, with a thin decorative rule above it.

"timeline" →
  Render timeline_items with a real visual timeline.
  Option A: horizontal line with dots, years above, events below.
  Option B: vertical line on left, year labels on left, event text on right.
  Use accent color for dots/line. Animate items in sequentially.

"stats" →
  2-4 stats arranged dramatically. Each stat: number in HUGE font (10-15vw), label in small font below.
  Arrange in a row or 2×2 grid. Numbers count up from 0 on slide enter (JS).
  Background can use a bold color or the signature motif prominently.

"closing" →
  Similar energy and layout to the title slide — mirrors it visually.
  Strong closing message. Can show title + subtitle + body.
  Give it a sense of completion/resolution.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT RENDERING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- NEVER use <ul> or <li> — banned entirely
- If a slide has "bullets" array, render each as a styled <div> row. Options:
    • Numbered: large accent-colored number + text side by side
    • Icon rows: a small square/dot/dash in accent color + text
    • Pill tags: each bullet as a rounded pill/badge
    • Card rows: each bullet in its own mini card with subtle background
  Choose whichever fits the overall design aesthetic.
- "body" text: render as a styled paragraph, large enough to read comfortably
- accent_word: use this word in the title with accent color highlight

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NAVIGATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Left/right arrow buttons — styled to match the design (not default browser buttons)
  Position them at left/right edges or bottom center of screen
- Keyboard: ArrowLeft = prev, ArrowRight / Space = next, Home = first, End = last
- Click anywhere on slide = next slide (use event delegation, exclude nav buttons with stopPropagation)
- Touch swipe: touchstart + touchend listeners, if Math.abs(deltaX) > 50 navigate
- Slide counter "3 / 10" — elegant typography, positioned in a corner, styled to theme
- Progress bar: thin (3-4px), full width, top or bottom of viewport, fills as slides advance
- JS structure: currentIndex variable, totalSlides, goTo(n), next(), prev() functions
- On goTo: hide current slide (display:none or remove 'active' class), show new slide, update counter + progress

{anim_block}

{auto_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TECHNICAL REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Single self-contained HTML file — zero external JS libraries
- Google Fonts via @import in CSS — allowed
- Each slide: <div class="slide" id="slide-N"> — only one visible at a time
- 100vw × 100vh, overflow:hidden on body
- All {len(slides_data)} slides must be present and fully rendered
- Mobile responsive — works on phones
- File opens by double-clicking in any browser

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Return ONLY the raw HTML file.
Start with <!DOCTYPE html>
NO markdown. NO code fences. NO explanation. Just the HTML."""

            html_resp = client.chat.completions.create(
                messages=[{"role": "user", "content": html_prompt}],
                model=MODEL,
                temperature=0.85,
                max_tokens=16000,
            )

            html_output = html_resp.choices[0].message.content.strip()
            html_output = re.sub(r'^```[a-z]*\n?', '', html_output)
            html_output = re.sub(r'\n?```$', '', html_output.strip())

            if not (html_output.startswith("<!DOCTYPE") or html_output.startswith("<html")):
                st.error("❌ Model returned invalid output. Please try again.")
                progress_bar.empty(); status.empty(); st.stop()

            # ── Done ─────────────────────────────────────────────────────────
            progress_bar.progress(100)
            progress_bar.empty()
            status.empty()

            st.balloons()
            st.success(f"🎉 Your {len(slides_data)}-slide presentation is ready!")

            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Slides", len(slides_data))
            with col2: st.metric("Tone", pres_style)
            with col3: st.metric("Animations", "ON ✨" if enable_animations else "OFF")

            st.markdown("### 👁️ Preview")
            st.components.v1.html(html_output, height=540, scrolling=False)

            safe_title = re.sub(r'[^\w\s-]', '', slides_data[0].get('title', 'slideshow'))[:40].replace(' ', '_')
            st.markdown("### 📥 Download")
            st.download_button(
                label="📥 Download .html file",
                data=html_output.encode("utf-8"),
                file_name=f"{safe_title}.html",
                mime="text/html",
                use_container_width=True
            )

            st.markdown("""
<div class="info-card">
💡 <strong>Tips:</strong><br>
• Double-click the .html → opens in any browser<br>
• Arrow keys or on-screen buttons to navigate<br>
• <strong>✨ FX</strong> button (bottom-right) toggles animations<br>
• Browser → Print → Save as PDF to export
</div>
""", unsafe_allow_html=True)

        except Exception as e:
            progress_bar.empty()
            status.empty()
            st.error(f"❌ Error: {str(e)}")
            st.info("Try again or simplify your topic.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#555;padding:1.5rem 0;font-family:monospace;font-size:.85rem;">
    <strong>GENIS 2.0</strong> · HTML Slideshows · Powered by Genis 3<br>
    <span style="opacity:.4;">© 2025 Genis 2.0</span>
</div>
""", unsafe_allow_html=True)
