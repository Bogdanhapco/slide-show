import streamlit as st
import google.generativeai as genai
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
    .block-container { max-width:860px !important; padding: 2rem; }

    .big-title {
        text-align:center; font-size:3.2rem; font-weight:800;
        background: linear-gradient(135deg,#00f5d4 0%,#7b2ff7 100%);
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
    .stButton > button:hover { opacity:.88; transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,245,212,.3); }
    .info-card {
        background:#0d1117; padding:1.2rem; border-radius:10px;
        border-left:3px solid #00f5d4; margin:1rem 0;
        font-family:'Space Mono',monospace; font-size:.84rem; color:#ccc;
    }
</style>
""", unsafe_allow_html=True)

# ── API setup ──────────────────────────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    api_available = True
except Exception:
    api_available = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Genis 2.0")
    st.markdown("---")
    st.markdown("### ⚡ Features")
    st.markdown("""
- 🤖 Gemini Flash 2.0 generation
- 🎨 Fully unique AI-designed themes
- 🎬 Per-slide animations
- ✨ FX on/off toggle in slideshow
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
GEMINI_API_KEY = "your-key-here"
```
Get key free at [aistudio.google.com](https://aistudio.google.com)
    """)
    st.markdown("---")
    st.markdown("### 📂 Opening the file")
    st.info("Double-click the `.html` file → opens in any browser.\n\nPrint → Save as PDF to share.")
    st.markdown("---")
    if not api_available:
        st.error("⚠️ GEMINI_API_KEY not configured")
    else:
        st.success("✅ Gemini Flash Ready")
    st.markdown("---")
    st.caption("© 2025 Genis 2.0")

# ── Main UI ────────────────────────────────────────────────────────────────────
st.markdown('<div class="big-title">🎯 Genis 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI HTML Slideshow Generator</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### 👤 Author")
author_name = st.text_input("Your name (shown on title slide)", placeholder="e.g. John Smith")

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
        pres_style = st.selectbox("Content tone", ["Professional", "Creative", "Educational", "Storytelling", "Technical", "Inspirational"])
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
        placeholder="e.g. dark and dramatic  /  warm and earthy  /  electric neon  /  clean and corporate",
        label_visibility="collapsed"
    )

# ── Generate ───────────────────────────────────────────────────────────────────
if st.button("🚀 Generate Slideshow"):
    if not api_available:
        st.error("❌ GEMINI_API_KEY not set in Streamlit secrets.")
    elif not topic or len(topic.strip()) < 10:
        st.warning("⚠️ Please enter a more detailed topic.")
    elif not author_name or len(author_name.strip()) < 2:
        st.warning("⚠️ Please enter your name.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()

        try:
            # ── Step 1: generate slide content ──────────────────────────────
            status.text("🧠 Writing slide content...")
            progress_bar.progress(10)

            content_prompt = f"""You are a world-class presentation writer.

Topic: {topic}
Tone: {pres_style}
Slides: {num_slides}
Author: {author_name.strip()}

Write {num_slides} slides. Return ONLY a valid JSON array, no markdown, no explanation.

Each slide object:
{{
  "index": 0,
  "type": "title" | "statement" | "split" | "grid" | "quote" | "timeline" | "stats" | "closing",
  "title": "...",
  "subtitle": "...",
  "body": "...",
  "bullets": ["...", "..."],
  "stats": [{{"value":"82%","label":"of companies use AI"}}],
  "quote": "...",
  "quote_author": "...",
  "grid_items": [{{"icon":"emoji","text":"short label"}}],
  "timeline_items": [{{"year":"2020","event":"..."}}],
  "accent_word": "..."
}}

Rules:
- Slide 0 must be type "title", last slide type "closing"
- Use a MIX of types — never repeat same type twice in a row
- body and bullets should NOT both be filled — pick one
- Keep text SHORT and PUNCHY
- stats slides: 2-4 big numbers with labels
- grid slides: exactly 4-6 items with relevant emojis
- quote slides: real or paraphrased relevant quote
- timeline slides: 4-5 chronological events
- For non-applicable fields use empty string "" or empty array []"""

            content_resp = model.generate_content(content_prompt)
            raw = content_resp.text.strip()
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

            # ── Step 2: generate full HTML ───────────────────────────────────
            status.text("🎨 Designing your slideshow — this takes ~20 seconds...")
            progress_bar.progress(45)

            mood_line = f'Mood/vibe from user: "{mood_hint.strip()}"' if mood_hint.strip() else "No mood hint — go wild. Design something bold, unique, and memorable."

            anim_block = """
━━━ ANIMATIONS ━━━
Use CSS keyframe animations triggered by JS adding class 'active' to the current slide.
- Title slide: massive scale+blur entrance for the h1 (scale 1.2→1, blur 8px→0, opacity 0→1)
- Statement slide: text slams in with slight rotation (-2deg→0) + fade
- Split slide: left panel slides from left, right panel slides from right simultaneously  
- Grid slide: cards fan in with staggered scale+fade (0.08s delay increments)
- Quote slide: quote mark scales in first, then text fades up
- Stats slide: numbers animate counting up from 0 using JS requestAnimationFrame
- Timeline slide: dots and lines draw in sequentially
- Closing slide: same energy as title
- Body text / bullets: each line fades up with 0.1s stagger delay
- A fixed button id="fx-btn" (bottom-right corner, small, elegant) toggles class 'no-anim' on <body>
  CSS: body.no-anim * { animation-duration: 0.001s !important; transition-duration: 0.001s !important; }
  Button shows "✨" when animations on, "○" when off
""" if enable_animations else """
━━━ ANIMATIONS ━━━
No entrance animations. Everything appears instantly.
Include the #fx-btn toggle button anyway (bottom-right), default state OFF showing "○".
User can click to enable animations if they want.
"""

            auto_block = f"""
━━━ AUTO-ADVANCE ━━━
After navigation is set up, add:
setInterval(() => {{ if (currentIndex < totalSlides - 1) goTo(currentIndex + 1); }}, {advance_secs * 1000});
""" if auto_advance and advance_secs > 0 else ""

            html_prompt = f"""You are an elite front-end designer and creative director. Generate a STUNNING, production-quality, self-contained HTML5 slideshow.

{mood_line}

SLIDE DATA:
{json.dumps(slides_data, ensure_ascii=False, indent=2)}

AUTHOR: {author_name.strip()}
TOTAL SLIDES: {len(slides_data)}

━━━ VISUAL DESIGN MANDATE ━━━
Design a UNIQUE, cohesive visual identity from scratch. Choose:
1. A color palette (2-3 main colors + neutrals). Be bold — not default blue/purple.
2. Two Google Fonts: one dramatic display font for titles, one refined font for body text.
3. A signature graphic motif woven through the design — pick ONE:
   - Diagonal geometric cuts / slanted panels
   - Floating abstract SVG blobs / organic shapes
   - Fine grid or dot-grid background texture
   - Noise/grain overlay (CSS filter or SVG feTurbulence)
   - Layered gradient mesh
   - Bold typographic oversized background letters
   - Duotone color treatment
   - Art deco geometric ornaments
   - etc. — be creative, pick what fits the mood

The design must feel like a real design agency made it. NOT generic PowerPoint.

━━━ SLIDE LAYOUT RULES ━━━
Each slide type gets a DISTINCT layout — never the same structure twice:

"title"     → Full-bleed hero. Massive centered title (7-10vw font). Subtitle below. "by {author_name.strip()}" as small elegant byline. Use the signature motif prominently.
"statement" → One giant sentence takes up 60-80% of the slide. Minimal everything else. Dramatic.
"split"     → Exactly 50/50. Left: title + content. Right: pure design — a color block, big SVG shape, giant accent number, oversized accent word, abstract art — NO text except maybe one word.
"grid"      → Render grid_items as styled cards in CSS grid (2×2 or 2×3). Each card: big emoji + label. Cards styled to match theme.
"quote"     → Giant decorative quotation marks (styled with font or SVG). Quote text large and italic. Author attribution small below with a line/rule.
"timeline"  → Visual timeline element (horizontal or vertical). Each event: year in accent color, event text beside it. Connected by line with dots.
"stats"     → 2-4 stats in a dramatic layout. Numbers HUGE (10-15vw). Labels small below. Arranged asymmetrically or in a grid. Numbers count up on enter.
"closing"   → Mirrors title energy. Strong closing message. Can include a CTA or summary line.

STRICT RULES:
- NEVER use <ul><li> bullet lists — instead use styled <div> rows, cards, or big text
- If bullets array has items, render them as styled rows (e.g., numbered with accent color, or as pill tags, or as icon+text rows)
- Each slide must look visually different — vary font sizes, layouts, color usage

━━━ NAVIGATION ━━━
- Left/right arrow buttons (styled to the design, positioned at slide edges or bottom)
- Keyboard: ArrowLeft=prev, ArrowRight/Space=next, Home=first, End=last
- Click/tap anywhere on slide = next (exclude nav buttons with event.stopPropagation)
- Touch swipe: touchstart + touchend, if deltaX > 50 navigate
- Slide counter "2 / 10" — elegant, positioned in corner
- Progress bar (thin, top or bottom of screen)
- JS functions: goTo(index), next(), prev()
- Track currentIndex, totalSlides

{anim_block}

{auto_block}

━━━ TECHNICAL ━━━
- Single self-contained HTML file — NO external JS libraries
- Google Fonts via @import in <style> — OK
- 100vw × 100vh, overflow hidden
- Only one slide visible at a time
- Works offline after first load (fonts may need internet)
- Mobile responsive

━━━ OUTPUT ━━━
Return ONLY the raw HTML starting with <!DOCTYPE html>
NO markdown. NO code fences. NO explanation. Just HTML."""

            html_resp = model.generate_content(
                html_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    max_output_tokens=16000,
                )
            )

            html_output = html_resp.text.strip()
            html_output = re.sub(r'^```[a-z]*\n?', '', html_output)
            html_output = re.sub(r'\n?```$', '', html_output.strip())

            if not (html_output.startswith("<!DOCTYPE") or html_output.startswith("<html")):
                st.error("❌ Gemini returned invalid output. Please try again.")
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
• <strong>✨</strong> button (bottom-right) toggles animations<br>
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
    <strong>GENIS 2.0</strong> · HTML Slideshows · Powered by Genis 3.0<br>
    <span style="opacity:.4;">© 2025 Genis 2.0</span>
</div>
""", unsafe_allow_html=True)
