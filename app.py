import streamlit as st
from groq import Groq
import io
import json
import re

# Page config
st.set_page_config(
    page_title="Genis 2.0 - Slideshow Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }

    .block-container {
        max-width: 900px !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .big-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #00f5d4 0%, #7b2ff7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Syne', sans-serif;
        letter-spacing: -1px;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #888;
        margin-bottom: 2rem;
        font-family: 'Space Mono', monospace;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.1rem;
        font-weight: bold;
        background: linear-gradient(135deg, #00f5d4 0%, #7b2ff7 100%);
        color: #0a0a0a;
        border: none;
        border-radius: 8px;
        margin-top: 1rem;
        font-family: 'Space Mono', monospace;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,245,212,0.3);
    }

    .style-card {
        background: #111;
        border: 1px solid #222;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: border-color 0.2s;
    }

    .style-card:hover {
        border-color: #00f5d4;
    }

    .info-card {
        background: #0d1117;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 3px solid #00f5d4;
        margin: 1rem 0;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# API setup
try:
    groq_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=groq_key)
    api_available = True
except:
    api_available = False

# Style presets
STYLE_PRESETS = {
    "🌑 Dark / Neon (Cyberpunk)": {
        "description": "Dark background, glowing neon accents, futuristic typography",
        "prompt": """Dark cyberpunk aesthetic. Background: #0a0a0f. Neon accent colors: #00f5d4 (cyan) and #ff2d78 (pink). 
        Font: use Google Fonts 'Orbitron' for titles, 'Share Tech Mono' for body. 
        Slide title: glowing text-shadow in cyan. Bullets: neon green dots (#39ff14). 
        Slide number in corner with neon glow. Add subtle scanline CSS overlay (repeating-linear-gradient). 
        Navigation buttons: dark with neon border. Progress bar: neon gradient."""
    },
    "🤍 Clean / Minimal (White)": {
        "description": "Pure white, razor-sharp typography, extreme negative space",
        "prompt": """Ultra-minimal editorial aesthetic. Background: #fafafa. Text: #0d0d0d. 
        Font: use Google Fonts 'Playfair Display' for titles, 'DM Sans' for body. 
        Accent: single color #1a1a2e. Generous padding and whitespace. 
        Slide number: subtle small text top-right. Thin 1px lines as dividers. 
        Navigation: minimal text arrows. No shadows, no gradients — pure type and space."""
    },
    "💼 Bold / Corporate": {
        "description": "Strong structure, confident colors, authoritative presence",
        "prompt": """Bold corporate powerhouse aesthetic. Background: #0f1923. Accent: #f7c948 (gold). 
        Font: use Google Fonts 'Barlow Condensed' (800 weight) for titles, 'IBM Plex Sans' for body. 
        Titles: massive, all-caps, tracked. Left accent bar: 4px solid gold on slide titles. 
        Bullets: gold square markers. Navigation: rectangular flat buttons in gold. 
        Slide counter: gold / total in corner. Dark professional feel with high contrast."""
    },
    "🌈 Gradient / Modern": {
        "description": "Lush mesh gradients, glass morphism, smooth and contemporary",
        "prompt": """Modern glassmorphism + gradient mesh aesthetic. Background: deep gradient #0f0c29 → #302b63 → #24243e. 
        Frosted glass slide cards: background rgba(255,255,255,0.05), backdrop-filter blur(20px), border 1px solid rgba(255,255,255,0.1). 
        Font: use Google Fonts 'Plus Jakarta Sans' for titles, 'Nunito' for body. 
        Accent: vivid gradient text on titles (#f953c6 → #b91d73). 
        Navigation: glass pill buttons with hover glow. Smooth slide transitions with scale + fade."""
    },
    "✏️ Custom": {
        "description": "Describe your own style",
        "prompt": None
    }
}

# Animation descriptions for the AI
ANIMATION_STYLES = {
    "🌑 Dark / Neon (Cyberpunk)": "glitch-flicker entrance for title, scan-line wipe for bullets",
    "🤍 Clean / Minimal (White)": "elegant fade-up for title, staggered fade-in for bullets",
    "💼 Bold / Corporate": "slide-in-left for title, cascade drop for bullets",
    "🌈 Gradient / Modern": "scale-up with blur-clear for title, float-up stagger for bullets",
    "✏️ Custom": "smooth fade and slide-up transitions"
}

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Genis 2.0")
    st.markdown("---")
    st.markdown("### ⚡ Features")
    st.markdown("""
- 🎨 4 style presets + custom
- 💡 AI-generated HTML slides
- 🎬 Slide animations toggle
- ⌨️ Keyboard + click navigation
- 🔄 Auto-advance mode
- 📥 Download as .html
    """)
    st.markdown("---")
    st.markdown("### 📱 Opening the file")
    st.info("Double-click the downloaded `.html` file — opens in any browser on any device.")
    st.markdown("""
**Print to PDF:**  
Browser → Print → Save as PDF  
(preserves full styling)
    """)
    st.markdown("---")
    st.markdown("### 🔢 Limits")
    st.info("**Max slides:** 60  \n**Min slides:** 3")
    st.markdown("---")
    if not api_available:
        st.error("⚠️ Groq API not configured")
    else:
        st.success("✅ AI System Ready")
    st.markdown("---")
    st.caption("© 2025 Genis 2.0")

# ─── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="big-title">🎯 Genis 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">HTML Slideshow Generator</div>', unsafe_allow_html=True)

st.markdown("---")

# Author name
st.markdown("### 👤 Your Information")
author_name = st.text_input(
    "Your Name (appears on title slide)",
    placeholder="e.g., John Smith"
)

# Topic
st.markdown("### 📝 What would you like to create?")
topic = st.text_area(
    "Describe your slideshow:",
    placeholder="Example: Create a 10-slide presentation about the future of AI in healthcare",
    height=100,
    label_visibility="collapsed"
)

# Options
with st.expander("⚙️ Customization Options", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        num_slides = st.number_input(
            "Number of slides",
            min_value=3,
            max_value=60,
            value=10
        )
        pres_style = st.selectbox(
            "Presentation style",
            ["Professional", "Creative", "Educational", "Storytelling", "Technical"]
        )

    with col2:
        selected_theme = st.selectbox(
            "Visual theme",
            list(STYLE_PRESETS.keys())
        )
        enable_animations = st.toggle("🎬 Enable slide animations", value=True)
        auto_advance = st.toggle("⏩ Auto-advance slides", value=False)
        if auto_advance:
            advance_seconds = st.slider("Seconds per slide", 2, 15, 5)
        else:
            advance_seconds = 0

    # Custom style input
    if selected_theme == "✏️ Custom":
        st.markdown("**Describe your custom style:**")
        custom_style_desc = st.text_area(
            "Style description",
            placeholder="e.g., Retro 80s vibe, warm sunset colors (#ff6b35, #f7c59f), serif fonts, vintage grain texture overlay, bold italic titles...",
            height=100,
            label_visibility="collapsed"
        )
    else:
        custom_style_desc = ""
        theme_info = STYLE_PRESETS[selected_theme]
        st.markdown(f"**Preview:** *{theme_info['description']}*")

# ─── Generate ──────────────────────────────────────────────────────────────────
if st.button("🚀 Generate HTML Slideshow"):
    if not api_available:
        st.error("❌ Groq API not configured.")
    elif not topic or len(topic.strip()) < 10:
        st.warning("⚠️ Please enter a more detailed topic.")
    elif not author_name or len(author_name.strip()) < 2:
        st.warning("⚠️ Please enter your name.")
    elif selected_theme == "✏️ Custom" and len(custom_style_desc.strip()) < 15:
        st.warning("⚠️ Please describe your custom style in more detail.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Build style prompt
            if selected_theme == "✏️ Custom":
                style_prompt = custom_style_desc.strip()
                anim_style = "smooth fade and slide-up transitions"
            else:
                style_prompt = STYLE_PRESETS[selected_theme]["prompt"]
                anim_style = ANIMATION_STYLES[selected_theme]

            animation_instructions = ""
            if enable_animations:
                animation_instructions = f"""
ANIMATIONS: Include CSS keyframe animations on each slide.
- Title animates in on slide enter: {anim_style}
- Bullet points stagger in one by one (animation-delay: 0.1s increments)
- Add a class 'slide-active' that triggers animations — JS adds this class when slide becomes visible
- Use will-change: transform for performance
"""
            else:
                animation_instructions = "ANIMATIONS: No animations. All elements appear instantly."

            auto_advance_js = ""
            if auto_advance and advance_seconds > 0:
                auto_advance_js = f"setInterval(() => {{ if(currentSlide < totalSlides - 1) goToSlide(currentSlide + 1); }}, {advance_seconds * 1000});"

            # Step 2: Generate slide content
            status_text.text("🧠 Generating slide content...")
            progress_bar.progress(15)

            content_prompt = f"""Create slideshow content for: "{topic}"

Requirements:
- Number of slides: {num_slides}
- Style: {pres_style}
- First slide: title slide only (no bullets)
- Last slide: strong conclusion/summary
- Each content slide: 3-5 concise bullet points (not full sentences, punchy)

Respond in this EXACT format, nothing else:

SLIDE 1:
TITLE: [Main presentation title]
SUBTITLE: [optional short tagline or leave blank]

SLIDE 2:
TITLE: [slide title]
BULLETS:
- [point 1]
- [point 2]
- [point 3]

Continue this pattern for all {num_slides} slides. No extra commentary."""

            content_resp = client.chat.completions.create(
                messages=[{"role": "user", "content": content_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=6000,
            )
            raw_content = content_resp.choices[0].message.content

            # Step 3: Parse slides
            status_text.text("📊 Structuring slides...")
            progress_bar.progress(35)

            slides_data = []
            current_slide = None
            in_bullets = False

            for line in raw_content.split('\n'):
                line = line.strip()
                if re.match(r'^SLIDE \d+:', line):
                    if current_slide:
                        slides_data.append(current_slide)
                    current_slide = {"title": "", "subtitle": "", "bullets": []}
                    in_bullets = False
                elif line.startswith('TITLE:') and current_slide is not None:
                    current_slide["title"] = line.replace('TITLE:', '').strip()
                elif line.startswith('SUBTITLE:') and current_slide is not None:
                    current_slide["subtitle"] = line.replace('SUBTITLE:', '').strip()
                elif line == 'BULLETS:':
                    in_bullets = True
                elif (line.startswith('- ') or line.startswith('• ')) and in_bullets and current_slide is not None:
                    current_slide["bullets"].append(line[2:].strip())

            if current_slide:
                slides_data.append(current_slide)

            if not slides_data:
                st.error("❌ Failed to parse slide content. Please try again.")
                progress_bar.empty()
                status_text.empty()
                st.stop()

            # Step 4: Generate HTML
            status_text.text("🎨 Designing your HTML slideshow...")
            progress_bar.progress(55)

            slides_json = json.dumps(slides_data, ensure_ascii=False)

            html_prompt = f"""Generate a complete, self-contained HTML5 slideshow presentation file.

SLIDE DATA (JSON):
{slides_json}

AUTHOR: {author_name.strip()}
TOTAL SLIDES: {len(slides_data)}

VISUAL STYLE:
{style_prompt}

{animation_instructions}

AUTO-ADVANCE JS (insert after navigation setup if not empty): {auto_advance_js if auto_advance_js else "// no auto-advance"}

NAVIGATION REQUIREMENTS:
1. Left/right on-screen arrow buttons (elegant, styled to theme)
2. Keyboard: ArrowLeft, ArrowRight, Space (next), Home (first), End (last)
3. Slide counter: "3 / 10" format, styled to theme
4. Progress bar at top or bottom
5. Click/tap anywhere on slide = next slide

ANIMATION TOGGLE:
- Add a small toggle button in corner labeled "✨ FX" 
- When clicked, adds/removes class 'animations-off' on <body>
- When 'animations-off': all transitions instant (transition: none !important on everything)
- Default state: animations {"ON" if enable_animations else "OFF"} (set class accordingly on load)

SLIDE STRUCTURE:
- Each slide is a <div class="slide"> inside a <div id="slideshow">
- First slide: large centered title + subtitle + "by {author_name.strip()}"
- Content slides: title at top, bullets below with custom markers per theme
- Active slide has class 'slide-active', others have display:none or opacity:0

TECHNICAL REQUIREMENTS:
- Pure HTML/CSS/JS — NO external dependencies except Google Fonts (ok to use CDN)
- 100vw x 100vh full screen
- Mobile responsive (touch swipe support: touchstart + touchend deltaX > 50 = navigate)
- All slide content from the JSON above — DO NOT invent or skip any slides
- Include all {len(slides_data)} slides
- File must work by double-clicking and opening in any browser

OUTPUT: Return ONLY the complete HTML file, starting with <!DOCTYPE html>. Nothing else, no explanation, no markdown code blocks."""

            html_resp = client.chat.completions.create(
                messages=[{"role": "user", "content": html_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.4,
                max_tokens=16000,
            )

            html_output = html_resp.choices[0].message.content.strip()

            # Strip markdown fences if AI wrapped it
            if html_output.startswith("```"):
                html_output = re.sub(r'^```[a-z]*\n?', '', html_output)
                html_output = re.sub(r'\n?```$', '', html_output.strip())

            if not html_output.startswith("<!DOCTYPE") and not html_output.startswith("<html"):
                st.error("❌ AI returned invalid HTML. Please try again.")
                progress_bar.empty()
                status_text.empty()
                st.stop()

            # Step 5: Done
            status_text.text("✅ Finalizing...")
            progress_bar.progress(100)
            progress_bar.empty()
            status_text.empty()

            st.balloons()
            st.success(f"🎉 **Done!** Your {len(slides_data)}-slide HTML presentation is ready!")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Slides", len(slides_data))
            with col2:
                st.metric("Theme", selected_theme.split()[1] if len(selected_theme.split()) > 1 else selected_theme)
            with col3:
                st.metric("Animations", "ON ✨" if enable_animations else "OFF")

            safe_title = slides_data[0]['title'][:40].replace(' ', '_').replace('/', '_').replace('\\', '_')
            file_name = f"{safe_title}.html"

            # Preview iframe
            st.markdown("### 👁️ Preview")
            st.components.v1.html(html_output, height=520, scrolling=False)

            st.markdown("### 📥 Download")
            st.download_button(
                label="📥 Download as .html file",
                data=html_output.encode("utf-8"),
                file_name=file_name,
                mime="text/html",
                use_container_width=True
            )

            st.markdown("""
<div class="info-card">
<strong>💡 Tips:</strong><br>
• Double-click the .html file to open in your browser<br>
• Use arrow keys or on-screen buttons to navigate<br>
• Toggle <strong>✨ FX</strong> button to turn animations on/off<br>
• Browser → Print → Save as PDF to export as PDF
</div>
""", unsafe_allow_html=True)

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error: {str(e)}")
            st.info("Please try again or rephrase your topic.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #555; padding: 2rem 0; font-family: monospace; font-size: 0.85rem;">
    <strong style="font-size: 1.1rem;">GENIS 2.0</strong><br>
    HTML Slideshows · Powered by Groq<br>
    <span style="opacity:0.5;">© 2025 Genis 2.0</span>
</div>
""", unsafe_allow_html=True)
