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
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🎯 Genis AI - Slideshow Generator")
st.caption("Powered by Genis 2.0")

# Sidebar
with st.sidebar:
    st.header("About Genis AI")
    st.markdown("""
    🎨 **AI-Powered Slideshows**
    
    Ask me to create presentations and I'll generate them instantly!
    
    **Example prompts:**
    - "Create a 10-slide presentation about climate change"
    - "Make a slideshow on the history of computers"
    - "Generate a business pitch about electric cars"
    """)
    
    st.divider()
    
    # Get API key from secrets
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("✅ API Connected")
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error("❌ API key not found")
        st.info("Add GROQ_API_KEY to Streamlit secrets")
        api_key = None
        client = None
    
    st.divider()
    st.info("🆓 **100% Free**\n14,400 requests/day!")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.caption("© 2025 Genis AI")

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])
            
            # Show download button if this message has a file
            if "file_data" in message and message["file_data"] is not None:
                st.download_button(
                    label="📥 Download Presentation",
                    data=message["file_data"],
                    file_name=message.get("file_name", "presentation.pptx"),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key=f"download_{i}"
                )

# Chat input
if prompt := st.chat_input("Ask me to create a slideshow..."):
    if not api_key or not client:
        st.error("⚠️ Please configure your API key in Streamlit secrets")
        st.stop()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            # Check if slideshow request
            slideshow_keywords = ["slideshow", "presentation", "powerpoint", "pptx", "slides", "deck", "create", "make", "generate"]
            is_slideshow_request = any(keyword in prompt.lower() for keyword in slideshow_keywords)
            
            if is_slideshow_request:
                response_placeholder.markdown("🎨 Genis is creating your slideshow... This will take about 10-20 seconds...")
                
                # Ask AI for slideshow content
                enhanced_prompt = f"""The user asked: "{prompt}"

Please analyze this request and provide slideshow content in this EXACT format:

TOPIC: [Main topic]
SLIDES: [Number of slides, default to 10 if not specified]

Then provide slide content like this:

SLIDE 1:
TITLE: [Slide title]
CONTENT:
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

SLIDE 2:
TITLE: [Slide title]
CONTENT:
- [Bullet point 1]
- [Bullet point 2]

Continue for all slides. Make content informative and engaging. Include a title slide and conclusion."""

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": enhanced_prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=4000,
                )
                
                response_text = chat_completion.choices[0].message.content
                
                # Parse the response
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
                    elif line.startswith('- ') or line.startswith('• '):
                        if current_slide is not None:
                            current_slide["content"].append(line[2:].strip())
                
                if current_slide:
                    slides_data.append(current_slide)
                
                # Create PowerPoint
                if slides_data:
                    prs = Presentation()
                    prs.slide_width = Inches(10)
                    prs.slide_height = Inches(5.625)
                    
                    # Colors
                    DARK_BLUE = RGBColor(25, 50, 100)
                    LIGHT_BLUE = RGBColor(66, 135, 245)
                    WHITE = RGBColor(255, 255, 255)
                    GRAY = RGBColor(100, 100, 100)
                    
                    for idx, slide_data in enumerate(slides_data):
                        blank_layout = prs.slide_layouts[6]
                        slide = prs.slides.add_slide(blank_layout)
                        
                        if idx == 0:
                            # Title slide
                            background = slide.shapes.add_shape(
                                1, 0, 0, prs.slide_width, prs.slide_height
                            )
                            background.fill.solid()
                            background.fill.fore_color.rgb = DARK_BLUE
                            background.line.fill.background()
                            
                            title_box = slide.shapes.add_textbox(
                                Inches(1), Inches(2), Inches(8), Inches(1.5)
                            )
                            title_frame = title_box.text_frame
                            title_frame.text = slide_data["title"]
                            title_para = title_frame.paragraphs[0]
                            title_para.font.size = Pt(54)
                            title_para.font.bold = True
                            title_para.font.color.rgb = WHITE
                            title_para.alignment = PP_ALIGN.CENTER
                        else:
                            # Content slides
                            background = slide.shapes.add_shape(
                                1, 0, 0, prs.slide_width, prs.slide_height
                            )
                            background.fill.solid()
                            background.fill.fore_color.rgb = WHITE
                            background.line.fill.background()
                            
                            accent = slide.shapes.add_shape(
                                1, 0, 0, prs.slide_width, Inches(0.15)
                            )
                            accent.fill.solid()
                            accent.fill.fore_color.rgb = LIGHT_BLUE
                            accent.line.fill.background()
                            
                            title_box = slide.shapes.add_textbox(
                                Inches(0.5), Inches(0.4), Inches(9), Inches(0.8)
                            )
                            title_frame = title_box.text_frame
                            title_frame.text = slide_data["title"]
                            title_para = title_frame.paragraphs[0]
                            title_para.font.size = Pt(40)
                            title_para.font.bold = True
                            title_para.font.color.rgb = DARK_BLUE
                            
                            if slide_data["content"]:
                                content_box = slide.shapes.add_textbox(
                                    Inches(1), Inches(1.5), Inches(8), Inches(3.5)
                                )
                                text_frame = content_box.text_frame
                                text_frame.word_wrap = True
                                
                                for point in slide_data["content"]:
                                    p = text_frame.add_paragraph()
                                    p.text = point
                                    p.level = 0
                                    p.font.size = Pt(18)
                                    p.font.color.rgb = GRAY
                                    p.space_before = Pt(12)
                    
                    # Save to bytes
                    pptx_bytes = io.BytesIO()
                    prs.save(pptx_bytes)
                    pptx_bytes.seek(0)
                    
                    response_placeholder.markdown(f"""✅ **Slideshow Created Successfully!**

I've created a {len(slides_data)}-slide presentation for you.

**What's included:**
- Professional design
- Title slide
- {len(slides_data)-2} content slides
- Conclusion slide

Click download below!""")
                    
                    file_name = f"{slides_data[0]['title'][:30].replace(' ', '_')}.pptx"
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"""✅ **Slideshow Created Successfully!**

I've created a {len(slides_data)}-slide presentation for you.

Click download below!""",
                        "file_data": pptx_bytes.getvalue(),
                        "file_name": file_name
                    })
                    
                    st.download_button(
                        label="📥 Download Presentation",
                        data=pptx_bytes.getvalue(),
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                else:
                    response_placeholder.markdown("❌ Couldn't create slideshow. Try rephrasing.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "❌ Couldn't create slideshow. Try rephrasing."
                    })
            else:
                # Regular chat
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                response_text = chat_completion.choices[0].message.content
                response_placeholder.markdown(response_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            response_placeholder.markdown(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# Welcome message
if len(st.session_state.messages) == 0:
    st.markdown("""
    ### 👋 Welcome to Genis AI!
    
    I can create professional slideshows instantly!
    
    **Try these:**
    
    💡 *"Create a 10-slide presentation about space exploration"*
    
    💡 *"Make a slideshow about healthy eating"*
    
    💡 *"Generate a pitch deck about AI startups"*
    
    ---
    
    **Features:**
    - ✨ AI-generated content
    - 🎨 Professional designs
    - 💾 Instant download
    - 🆓 100% Free!
    """)
