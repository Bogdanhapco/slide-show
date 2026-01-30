import streamlit as st
from groq import Groq
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import io
import random

# Page config
st.set_page_config(
    page_title="Genis 2.0 - Slideshow Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (unchanged) ──
st.markdown("""
<style>
    /* ... your existing CSS ... */
</style>
""", unsafe_allow_html=True)

# Get API key from secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
    api_available = True
except:
    api_available = False

# Initialize session state for examples
if "example_prompts" not in st.session_state:
    st.session_state.example_prompts = []

# ── NEW: Name input (placed near the topic input for good UX) ──
st.markdown("### 👤 Your Name (optional)")
presenter_name = st.text_input(
    "Enter your name to appear on the title slide",
    placeholder="e.g. Bogdan Smith",
    value="",
    label_visibility="collapsed"
)

# Sidebar (unchanged)
with st.sidebar:
    st.markdown("## 🎯 Genis 2.0")
    st.markdown("---")
    # ... rest of sidebar unchanged ...

# Main content
st.markdown('<div class="big-title">🎯 Genis 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Professional Slideshow Generator</div>', unsafe_allow_html=True)

# Example prompts generation (unchanged)
# ... your existing example prompts code ...

# Input field
st.markdown("### 📝 What would you like to create?")

default_value = st.session_state.get("user_topic", "")
if default_value:
    topic = st.text_area(
        "Describe your slideshow:",
        value=default_value,
        placeholder="Example: Create a 10-slide presentation about climate change",
        height=100,
        label_visibility="collapsed"
    )
    if "user_topic" in st.session_state:
        del st.session_state.user_topic
else:
    topic = st.text_area(
        "Describe your slideshow:",
        placeholder="Example: Create a 10-slide presentation about climate change",
        height=100,
        label_visibility="collapsed"
    )

# Advanced options (unchanged)
with st.expander("⚙️ Advanced Options"):
    col1, col2 = st.columns(2)
    with col1:
        num_slides = st.number_input(
            "Number of slides",
            min_value=5,
            max_value=100,
            value=10,
            help="Choose between 5 and 100 slides"
        )
    with col2:
        style = st.selectbox(
            "Presentation style",
            ["Professional", "Creative", "Educational", "Minimal", "Bold", "Modern"]
        )

# Generate button
if st.button("🚀 Generate Slideshow"):
    if not api_available:
        st.error("❌ System not configured. Please contact administrator.")
    elif not topic or len(topic.strip()) < 10:
        st.warning("⚠️ Please enter a more detailed topic for your slideshow.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # ── Your existing prompt generation ──
            enhanced_prompt = f"""Create slideshow content about: "{topic}"
Requirements:
- Number of slides: {num_slides}
- Style: {style}
Provide content in this EXACT format:
SLIDE 1:
TITLE: [Compelling title for the presentation]
CONTENT:
- [This is the title slide, no bullet points needed]
SLIDE 2:
..."""  # (rest unchanged)

            # Generate content from Groq (unchanged)
            status_text.text("🧠 Generating content...")
            progress_bar.progress(35)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": enhanced_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=8000,
            )
            response_text = chat_completion.choices[0].message.content

            # Parse slides (unchanged)
            lines = response_text.split('\n')
            slides_data = []
            current_slide = None
            for line in lines:
                line = line.strip()
                if line.startswith('SLIDE '):
                    if current_slide:
                        slides_data.append(current_slide)
                    current_slide = {"title": "", "content": []}
                elif line.startswith('TITLE:'):
                    if current_slide is not None:
                        current_slide["title"] = line.replace('TITLE:', '').strip()
                elif (line.startswith('- ') or line.startswith('• ')) and current_slide is not None:
                    current_slide["content"].append(line[2:].strip())
            if current_slide:
                slides_data.append(current_slide)

            if not slides_data:
                st.error("❌ Failed to generate slideshow. Please try again.")
                progress_bar.empty()
                status_text.empty()
            else:
                status_text.text("🎨 Designing presentation...")
                progress_bar.progress(75)

                prs = Presentation()
                prs.slide_width = Inches(10)
                prs.slide_height = Inches(5.625)

                # Color schemes (unchanged)
                color_schemes = { ... }  # your existing dict
                DARK_COLOR, ACCENT_COLOR = color_schemes.get(style, color_schemes["Professional"])
                WHITE = RGBColor(255, 255, 255)
                GRAY = RGBColor(80, 80, 80)

                for idx, slide_data in enumerate(slides_data):
                    blank_layout = prs.slide_layouts[6]
                    slide = prs.slides.add_slide(blank_layout)

                    if idx == 0:
                        # ── Title slide ──
                        background = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, prs.slide_height
                        )
                        background.fill.solid()
                        background.fill.fore_color.rgb = DARK_COLOR
                        background.line.fill.background()

                        title_box = slide.shapes.add_textbox(
                            Inches(1), Inches(1.8), Inches(8), Inches(1.8)
                        )
                        title_frame = title_box.text_frame
                        title_frame.text = slide_data["title"]
                        title_frame.word_wrap = True
                        title_para = title_frame.paragraphs[0]
                        title_para.font.size = Pt(48)
                        title_para.font.bold = True
                        title_para.font.color.rgb = WHITE
                        title_para.alignment = PP_ALIGN.CENTER

                        # ── CHANGED: Show presenter's name instead of "Created with Genis 2.0" ──
                        if presenter_name.strip():
                            credit_text = f"by {presenter_name.strip()}"
                        else:
                            credit_text = ""   # nothing if left empty

                        subtitle_box = slide.shapes.add_textbox(
                            Inches(1), Inches(3.8), Inches(8), Inches(0.5)
                        )
                        subtitle_frame = subtitle_box.text_frame
                        subtitle_frame.text = credit_text
                        subtitle_para = subtitle_frame.paragraphs[0]
                        subtitle_para.font.size = Pt(20)
                        subtitle_para.font.color.rgb = ACCENT_COLOR
                        subtitle_para.alignment = PP_ALIGN.CENTER

                    else:
                        # Content slides (unchanged)
                        # ... your existing code for content slides ...

                # Save and offer download (unchanged, except possibly filename)
                pptx_bytes = io.BytesIO()
                prs.save(pptx_bytes)
                pptx_bytes.seek(0)

                progress_bar.progress(100)
                progress_bar.empty()
                status_text.empty()

                st.balloons()
                st.success(f"🎉 **Success!** Your {len(slides_data)}-slide presentation is ready!")

                # Stats and download (unchanged)
                # ... your columns + download_button ...

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error: {str(e)}")
            st.info("Please try again or rephrase your topic.")

# Footer (unchanged)
st.markdown("---")
# ... your footer markdown ...
