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

# Custom CSS
st.markdown("""
<style>
    /* Force sidebar to always show on left */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }
    
    /* Center main content */
    .block-container {
        max-width: 900px !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    .big-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        font-size: 1.3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        margin-top: 1.5rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .info-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
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

# Initialize session state
if "example_prompts" not in st.session_state:
    st.session_state.example_prompts = []
if "selected_example" not in st.session_state:
    st.session_state.selected_example = ""

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Genis 2.0")
    st.markdown("---")
    
    st.markdown("### ⚡ Features")
    st.markdown("""
    - 🎨 Professional designs
    - 📊 Custom layouts
    - 🎯 AI-powered content
    - 📱 Mobile compatible
    - 💾 Instant download
    """)
    
    st.markdown("---")
    
    st.markdown("### 📱 Device Support")
    st.success("✅ Works on all devices")
    st.markdown("""
    **iPhone/iPad:**  
    PowerPoint or Keynote
    
    **Android:**  
    PowerPoint or Google Slides
    
    **Desktop:**  
    PowerPoint, Google Slides, LibreOffice
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔢 Limits")
    st.info("**Max slides:** 100  \n**Min slides:** 5")
    
    st.markdown("---")
    
    if not api_available:
        st.error("⚠️ API not configured")
    else:
        st.success("✅ System Ready")
    
    st.markdown("---")
    st.caption("© 2025 Genis 2.0")

# Main content
st.markdown('<div class="big-title">🎯 Genis 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Professional Slideshow Generator</div>', unsafe_allow_html=True)

# Generate example prompts if not already generated
if not st.session_state.example_prompts and api_available:
    with st.spinner("🎲 Generating example ideas..."):
        try:
            example_prompt = """Generate 4 diverse and interesting slideshow topic examples. 
            Make them varied across different fields (business, education, science, technology, health, history, etc.).
            
            Format each as a complete request like:
            "Create a 12-slide presentation about [topic]"
            
            Make them specific and engaging. Return ONLY the 4 examples, one per line, nothing else."""
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": example_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.9,
                max_tokens=300,
            )
            
            examples = response.choices[0].message.content.strip().split('\n')
            st.session_state.example_prompts = [ex.strip() for ex in examples if ex.strip()]
        except:
            st.session_state.example_prompts = [
                "Create a 10-slide presentation about renewable energy sources",
                "Create a 15-slide presentation about the human brain and memory",
                "Create a 12-slide presentation about digital marketing strategies",
                "Create an 8-slide presentation about ancient Egyptian civilization"
            ]

# Show examples
if st.session_state.example_prompts:
    st.markdown("### 💡 Need inspiration? Try these:")
    
    cols = st.columns(2)
    for idx, example in enumerate(st.session_state.example_prompts[:4]):
        with cols[idx % 2]:
            if st.button(f"📄 {example}", key=f"example_{idx}", use_container_width=True):
                st.session_state.selected_example = example

# Refresh examples button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 New Examples", use_container_width=True):
        st.session_state.example_prompts = []
        st.rerun()

st.markdown("---")

# Input fields
st.markdown("### 👤 Your Information")

author_name = st.text_input(
    "Your Name (will appear on title slide)",
    placeholder="e.g., John Smith",
    help="This will be shown as the author on the first slide"
)

st.markdown("### 📝 What would you like to create?")

# Topic input - use selected example if available
if st.session_state.selected_example:
    topic = st.text_area(
        "Describe your slideshow:",
        value=st.session_state.selected_example,
        placeholder="Example: Create a 10-slide presentation about climate change",
        height=100,
        label_visibility="collapsed",
        key="topic_input"
    )
else:
    topic = st.text_area(
        "Describe your slideshow:",
        placeholder="Example: Create a 10-slide presentation about climate change",
        height=100,
        label_visibility="collapsed",
        key="topic_input"
    )

# Advanced options
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
    # Clear the selected example after generation attempt
    st.session_state.selected_example = ""
    
    if not api_available:
        st.error("❌ System not configured. Please contact administrator.")
    elif not topic or len(topic.strip()) < 10:
        st.warning("⚠️ Please enter a more detailed topic for your slideshow.")
    elif not author_name or len(author_name.strip()) < 2:
        st.warning("⚠️ Please enter your name to continue.")
    else:
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Preparing
            status_text.text("🔄 Initializing Genis 2.0...")
            progress_bar.progress(15)
            
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

Continue for all {num_slides} slides. Last slide should be a strong conclusion.
Make content informative, engaging, and well-structured."""

            # Step 2: Generating content
            status_text.text("🧠 Generating content...")
            progress_bar.progress(35)
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": enhanced_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=8000,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Step 3: Parsing content
            status_text.text("📊 Structuring slides...")
            progress_bar.progress(55)
            
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
                status_text.text("🎨 Designing presentation...")
                progress_bar.progress(75)
                
                # Create PowerPoint
                prs = Presentation()
                prs.slide_width = Inches(10)
                prs.slide_height = Inches(5.625)
                
                # Color schemes based on style
                color_schemes = {
                    "Professional": (RGBColor(25, 50, 100), RGBColor(66, 135, 245)),
                    "Creative": (RGBColor(255, 87, 51), RGBColor(255, 195, 0)),
                    "Educational": (RGBColor(46, 125, 50), RGBColor(139, 195, 74)),
                    "Minimal": (RGBColor(33, 33, 33), RGBColor(97, 97, 97)),
                    "Bold": (RGBColor(211, 47, 47), RGBColor(245, 124, 0)),
                    "Modern": (RGBColor(102, 126, 234), RGBColor(118, 75, 162))
                }
                
                DARK_COLOR, ACCENT_COLOR = color_schemes.get(style, color_schemes["Professional"])
                WHITE = RGBColor(255, 255, 255)
                GRAY = RGBColor(80, 80, 80)
                
                for idx, slide_data in enumerate(slides_data):
                    blank_layout = prs.slide_layouts[6]
                    slide = prs.slides.add_slide(blank_layout)
                    
                    if idx == 0:
                        # Title slide
                        background = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, prs.slide_height
                        )
                        background.fill.solid()
                        background.fill.fore_color.rgb = DARK_COLOR
                        background.line.fill.background()
                        
                        # Main title
                        title_box = slide.shapes.add_textbox(
                            Inches(1), Inches(1.5), Inches(8), Inches(1.8)
                        )
                        title_frame = title_box.text_frame
                        title_frame.text = slide_data["title"]
                        title_frame.word_wrap = True
                        title_para = title_frame.paragraphs[0]
                        title_para.font.size = Pt(48)
                        title_para.font.bold = True
                        title_para.font.color.rgb = WHITE
                        title_para.alignment = PP_ALIGN.CENTER
                        
                        # Author name - "by [Name]"
                        subtitle_box = slide.shapes.add_textbox(
                            Inches(1), Inches(3.5), Inches(8), Inches(0.6)
                        )
                        subtitle_frame = subtitle_box.text_frame
                        subtitle_frame.text = f"by {author_name.strip()}"
                        subtitle_para = subtitle_frame.paragraphs[0]
                        subtitle_para.font.size = Pt(24)
                        subtitle_para.font.color.rgb = ACCENT_COLOR
                        subtitle_para.alignment = PP_ALIGN.CENTER
                        
                    else:
                        # Content slides
                        background = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, prs.slide_height
                        )
                        background.fill.solid()
                        background.fill.fore_color.rgb = WHITE
                        background.line.fill.background()
                        
                        accent = slide.shapes.add_shape(
                            1, 0, 0, prs.slide_width, Inches(0.2)
                        )
                        accent.fill.solid()
                        accent.fill.fore_color.rgb = ACCENT_COLOR
                        accent.line.fill.background()
                        
                        title_box = slide.shapes.add_textbox(
                            Inches(0.5), Inches(0.5), Inches(9), Inches(0.8)
                        )
                        title_frame = title_box.text_frame
                        title_frame.text = slide_data["title"]
                        title_para = title_frame.paragraphs[0]
                        title_para.font.size = Pt(36)
                        title_para.font.bold = True
                        title_para.font.color.rgb = DARK_COLOR
                        
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
                status_text.text("✅ Finalizing presentation...")
                progress_bar.progress(95)
                
                # Save to bytes
                pptx_bytes = io.BytesIO()
                prs.save(pptx_bytes)
                pptx_bytes.seek(0)
                
                progress_bar.progress(100)
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
                # Success message
                st.balloons()
                st.success(f"🎉 **Success!** Your {len(slides_data)}-slide presentation is ready!")
                
                # Stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Slides Created", len(slides_data))
                with col2:
                    st.metric("Style", style)
                with col3:
                    st.metric("Author", author_name)
                
                # File name
                safe_title = slides_data[0]['title'][:40].replace(' ', '_').replace('/', '_').replace('\\', '_')
                file_name = f"{safe_title}.pptx"
                
                # Download button
                st.download_button(
                    label="📥 Download Presentation",
                    data=pptx_bytes.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )
                
                # Mobile info
                st.markdown("""
                <div class="info-card">
                    <strong>📱 Opening on your device:</strong><br>
                    • <strong>iPhone/iPad:</strong> PowerPoint or Keynote app<br>
                    • <strong>Android:</strong> PowerPoint or Google Slides<br>
                    • <strong>Desktop:</strong> PowerPoint, Google Slides, or LibreOffice
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
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <h3 style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Genis 2.0
    </h3>
    <p>Professional Slideshows in Seconds</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">© 2025 Genis 2.0. All presentations created are owned by you.</p>
</div>
""", unsafe_allow_html=True)
