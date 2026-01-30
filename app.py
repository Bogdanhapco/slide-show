import streamlit as st
from groq import Groq
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import io

# Page config
st.set_page_config(
    page_title="Genis AI - Slideshow Generator",
    page_icon="🎯",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .big-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        margin-top: 1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .example-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Get API key from secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
    api_available = True
except:
    api_available = False

# Header
st.markdown('<div class="big-title">🎯 Genis AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Slideshow Generator</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📱 Mobile Friendly!")
    st.success("✅ Downloads work on all devices")
    
    st.markdown("""
    **iPhone/iPad:**
    - Opens in PowerPoint or Keynote
    
    **Android:**
    - Opens in PowerPoint or Google Slides
    
    **Desktop:**
    - Opens in PowerPoint, Google Slides, or LibreOffice
    """)
    
    st.divider()
    
    st.info("🆓 **100% Free**\nNo signup required!")
    
    st.divider()
    
    if not api_available:
        st.error("⚠️ API key not configured")
        st.info("Add GROQ_API_KEY to secrets")
    
    st.caption("© 2025 Genis AI")
    st.caption("Powered by Genis 2.0")

# Main content
st.markdown("### 📝 What's your presentation about?")

# Input field
topic = st.text_area(
    "Describe your slideshow topic:",
    placeholder="Example: Create a 10-slide presentation about climate change and renewable energy",
    height=100,
    help="Be specific! Tell me the topic and how many slides you want.",
    label_visibility="collapsed"
)

# Advanced options
with st.expander("⚙️ Advanced Options (Optional)"):
    col1, col2 = st.columns(2)
    with col1:
        num_slides = st.number_input("Number of slides", min_value=5, max_value=20, value=10)
    with col2:
        style = st.selectbox("Style", ["Professional", "Creative", "Educational", "Minimal"])

# Generate button
if st.button("🚀 Generate Slideshow"):
    if not api_available:
        st.error("❌ API key not configured. Please add GROQ_API_KEY to Streamlit secrets.")
    elif not topic or len(topic.strip()) < 10:
        st.warning("⚠️ Please enter a more detailed topic for your slideshow.")
    else:
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Preparing
            status_text.text("🔄 Preparing your slideshow...")
            progress_bar.progress(20)
            
            # Create enhanced prompt
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
TITLE: [Slide title]
CONTENT:
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

SLIDE 3:
TITLE: [Slide title]
CONTENT:
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

Continue for all {num_slides} slides. Last slide should be a conclusion.
Make content informative, engaging, and well-structured."""

            # Step 2: Generating content
            status_text.text("🤖 Genis is creating your content...")
            progress_bar.progress(40)
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": enhanced_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=4000,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Step 3: Parsing content
            status_text.text("📊 Organizing slides...")
            progress_bar.progress(60)
            
            # Parse response
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
                st.error("❌ Failed to generate slideshow. Please try again with a different topic.")
                progress_bar.empty()
                status_text.empty()
            else:
                # Step 4: Creating presentation
                status_text.text("🎨 Genis is designing your slides...")
                progress_bar.progress(80)
                
                # Create PowerPoint
                prs = Presentation()
                prs.slide_width = Inches(10)
                prs.slide_height = Inches(5.625)
                
                # Color schemes based on style
                if style == "Professional":
                    DARK_COLOR = RGBColor(25, 50, 100)
                    ACCENT_COLOR = RGBColor(66, 135, 245)
                elif style == "Creative":
                    DARK_COLOR = RGBColor(255, 87, 51)
                    ACCENT_COLOR = RGBColor(255, 195, 0)
                elif style == "Educational":
                    DARK_COLOR = RGBColor(46, 125, 50)
                    ACCENT_COLOR = RGBColor(139, 195, 74)
                else:  # Minimal
                    DARK_COLOR = RGBColor(33, 33, 33)
                    ACCENT_COLOR = RGBColor(97, 97, 97)
                
                WHITE = RGBColor(255, 255, 255)
                GRAY = RGBColor(80, 80, 80)
                
                for idx, slide_data in enumerate(slides_data):
                    blank_layout = prs.slide_layouts[6]
                    slide = prs.slides.add_slide(blank_layout)
                    
                    if idx == 0:
                        # Title slide with dark background
                        background = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, prs.slide_height
                        )
                        background.fill.solid()
                        background.fill.fore_color.rgb = DARK_COLOR
                        background.line.fill.background()
                        
                        # Main title
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
                        
                        # Subtitle
                        subtitle_box = slide.shapes.add_textbox(
                            Inches(1), Inches(3.8), Inches(8), Inches(0.5)
                        )
                        subtitle_frame = subtitle_box.text_frame
                        subtitle_frame.text = "Powered by Genis 2.0"
                        subtitle_para = subtitle_frame.paragraphs[0]
                        subtitle_para.font.size = Pt(18)
                        subtitle_para.font.color.rgb = ACCENT_COLOR
                        subtitle_para.alignment = PP_ALIGN.CENTER
                        
                    else:
                        # Content slides with white background
                        background = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, prs.slide_height
                        )
                        background.fill.solid()
                        background.fill.fore_color.rgb = WHITE
                        background.line.fill.background()
                        
                        # Top accent bar
                        accent = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, Inches(0.2)
                        )
                        accent.fill.solid()
                        accent.fill.fore_color.rgb = ACCENT_COLOR
                        accent.line.fill.background()
                        
                        # Title
                        title_box = slide.shapes.add_textbox(
                            Inches(0.5), Inches(0.5), Inches(9), Inches(0.8)
                        )
                        title_frame = title_box.text_frame
                        title_frame.text = slide_data["title"]
                        title_para = title_frame.paragraphs[0]
                        title_para.font.size = Pt(36)
                        title_para.font.bold = True
                        title_para.font.color.rgb = DARK_COLOR
                        
                        # Content bullets
                        if slide_data["content"]:
                            content_box = slide.shapes.add_textbox(
                                Inches(1.2), Inches(1.8), Inches(7.6), Inches(3.2)
                            )
                            text_frame = content_box.text_frame
                            text_frame.word_wrap = True
                            
                            for point in slide_data["content"]:
                                p = text_frame.add_paragraph()
                                p.text = point
                                p.level = 0
                                p.font.size = Pt(20)
                                p.font.color.rgb = GRAY
                                p.space_before = Pt(14)
                                p.space_after = Pt(8)
                
                # Step 5: Finalizing
                status_text.text("✅ Finalizing your presentation...")
                progress_bar.progress(100)
                
                # Save to bytes
                pptx_bytes = io.BytesIO()
                prs.save(pptx_bytes)
                pptx_bytes.seek(0)
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
                # Success message
                st.success(f"🎉 **Success!** Your {len(slides_data)}-slide presentation is ready!")
                
                # File name
                file_name = f"{slides_data[0]['title'][:40].replace(' ', '_').replace('/', '_')}.pptx"
                
                # Download button
                st.download_button(
                    label="📥 Download Presentation",
                    data=pptx_bytes.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )
                
                # Info box
                st.info("""
                **📱 Opening on mobile:**
                - iPhone/iPad: Use PowerPoint or Keynote app
                - Android: Use PowerPoint, Google Slides, or WPS Office
                - All apps are free to download!
                """)
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error: {str(e)}")
            st.info("Please try again or rephrase your topic.")

# Examples section
st.markdown("---")
st.markdown("### 💡 Example Topics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="example-box">
    <strong>Business:</strong><br>
    "10 slides about digital marketing strategies for small businesses"
    </div>
    
    <div class="example-box">
    <strong>Education:</strong><br>
    "15 slides explaining photosynthesis for high school students"
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="example-box">
    <strong>Science:</strong><br>
    "12 slides about the solar system and planets"
    </div>
    
    <div class="example-box">
    <strong>History:</strong><br>
    "8 slides on the Industrial Revolution and its impact"
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>🎯 Genis AI</strong> - Professional Slideshows in Seconds</p>
    <p>Powered by Groq AI | 100% Free | Works on All Devices</p>
    <p style="font-size: 0.9rem;">© 2025 Genis AI. All presentations created are owned by you.</p>
</div>
""", unsafe_allow_html=True)
