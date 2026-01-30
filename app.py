import streamlit as st
from groq import Groq
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Genis 2.0 - Slideshow Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    min-width: 300px !important;
    max-width: 300px !important;
}
.block-container {
    max-width: 900px !important;
}
.big-title {
    text-align: center;
    font-size: 3.5rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center;
    font-size: 1.3rem;
    color: #666;
}
.stButton > button {
    width: 100%;
    height: 3.5rem;
    font-size: 1.3rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API ----------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    api_available = True
except:
    api_available = False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🎯 Genis 2.0")
    st.markdown("Professional slideshow generator")
    st.markdown("---")
    st.markdown("**Limits**")
    st.info("Min: 5 slides\nMax: 100 slides")
    st.markdown("---")
    st.success("✅ System Ready" if api_available else "❌ API Not Configured")

# ---------------- MAIN ----------------
st.markdown('<div class="big-title">🎯 Genis 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Professional Slideshow Generator</div>', unsafe_allow_html=True)
st.markdown("---")

# ---------------- INPUTS ----------------
topic = st.text_area(
    "Slideshow topic",
    placeholder="Create a 10-slide presentation about artificial intelligence",
    height=100,
    label_visibility="collapsed"
)

st.markdown("### 👤 Your Name (optional)")
author_name = st.text_input(
    "Your name",
    placeholder="e.g. Alex Johnson",
    label_visibility="collapsed"
)

with st.expander("⚙️ Advanced Options"):
    col1, col2 = st.columns(2)
    with col1:
        num_slides = st.number_input("Number of slides", 5, 100, 10)
    with col2:
        style = st.selectbox(
            "Style",
            ["Professional", "Creative", "Educational", "Minimal", "Bold", "Modern"]
        )

# ---------------- GENERATE ----------------
if st.button("🚀 Generate Slideshow"):
    if not api_available:
        st.error("API not configured.")
    elif not topic.strip():
        st.warning("Please enter a topic.")
    else:
        progress = st.progress(0)

        prompt = f"""
Create slideshow content about: "{topic}"

Rules:
- Exactly {num_slides} slides
- Clear titles and bullet points
- First slide is a title slide
- Last slide is a conclusion

FORMAT STRICTLY AS:

SLIDE 1:
TITLE: Title here
CONTENT:
- No bullets

SLIDE 2:
TITLE: Title
CONTENT:
- Bullet
- Bullet

Continue until slide {num_slides}.
"""

        progress.progress(25)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=8000
        )

        progress.progress(50)

        # ---------------- PARSE ----------------
        slides = []
        current = None

        for line in response.choices[0].message.content.splitlines():
            line = line.strip()
            if line.startswith("SLIDE"):
                if current:
                    slides.append(current)
                current = {"title": "", "content": []}
            elif line.startswith("TITLE:"):
                current["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("- "):
                current["content"].append(line[2:].strip())

        if current:
            slides.append(current)

        if not slides:
            st.error("Failed to generate slides.")
            st.stop()

        progress.progress(75)

        # ---------------- PPT ----------------
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

        schemes = {
            "Professional": (RGBColor(25, 50, 100), RGBColor(66, 135, 245)),
            "Creative": (RGBColor(255, 87, 51), RGBColor(255, 195, 0)),
            "Educational": (RGBColor(46, 125, 50), RGBColor(139, 195, 74)),
            "Minimal": (RGBColor(33, 33, 33), RGBColor(120, 120, 120)),
            "Bold": (RGBColor(211, 47, 47), RGBColor(245, 124, 0)),
            "Modern": (RGBColor(102, 126, 234), RGBColor(118, 75, 162))
        }

        DARK, ACCENT = schemes[style]
        WHITE = RGBColor(255, 255, 255)
        GRAY = RGBColor(80, 80, 80)

        for i, s in enumerate(slides):
            slide = prs.slides.add_slide(prs.slide_layouts[6])

            if i == 0:
                bg = slide.shapes.add_shape(
                    1, 0, 0, prs.slide_width, prs.slide_height
                )
                bg.fill.solid()
                bg.fill.fore_color.rgb = DARK

                title_box = slide.shapes.add_textbox(
                    Inches(1), Inches(2), Inches(8), Inches(1.5)
                )
                tf = title_box.text_frame
                tf.text = s["title"]
                p = tf.paragraphs[0]
                p.font.size = Pt(48)
                p.font.bold = True
                p.font.color.rgb = WHITE
                p.alignment = PP_ALIGN.CENTER

                if author_name.strip():
                    author_box = slide.shapes.add_textbox(
                        Inches(1), Inches(3.7), Inches(8), Inches(0.6)
                    )
                    atf = author_box.text_frame
                    atf.text = f"By {author_name.strip()}"
                    ap = atf.paragraphs[0]
                    ap.font.size = Pt(20)
                    ap.font.color.rgb = ACCENT
                    ap.alignment = PP_ALIGN.CENTER

            else:
                bar = slide.shapes.add_shape(
                    1, 0, 0, prs.slide_width, Inches(0.2)
                )
                bar.fill.solid()
                bar.fill.fore_color.rgb = ACCENT

                title_box = slide.shapes.add_textbox(
                    Inches(0.5), Inches(0.5), Inches(9), Inches(1)
                )
                tf = title_box.text_frame
                tf.text = s["title"]
                tf.paragraphs[0].font.size = Pt(34)
                tf.paragraphs[0].font.bold = True
                tf.paragraphs[0].font.color.rgb = DARK

                content_box = slide.shapes.add_textbox(
                    Inches(1.2), Inches(1.8), Inches(7.6), Inches(3)
                )
                ctf = content_box.text_frame

                for point in s["content"]:
                    p = ctf.add_paragraph()
                    p.text = point
                    p.font.size = Pt(20)
                    p.font.color.rgb = GRAY

        progress.progress(100)

        buffer = io.BytesIO()
        prs.save(buffer)
        buffer.seek(0)

        st.success("🎉 Slideshow ready!")
        st.download_button(
            "📥 Download Presentation",
            buffer.getvalue(),
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#666;'>© 2025 Genis 2.0</div>",
    unsafe_allow_html=True
)
