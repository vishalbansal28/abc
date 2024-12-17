import streamlit as st
st.set_page_config(layout="wide")
from utils import resume_utils, ui_utils, local_match_utils, resume_generator
import PyPDF2
import io
import os
import re


st.title("Resume Tailoring Application")

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state['resume_data'] = {}
if 'resume_text' not in st.session_state:
    st.session_state['resume_text'] = None
if 'pdf_uploaded' not in st.session_state:
    st.session_state['pdf_uploaded'] = False
if 'resume_path' not in st.session_state:
    st.session_state['resume_path'] = None
if 'categorized_keywords' not in st.session_state:
    st.session_state['categorized_keywords'] = None
if 'job_description' not in st.session_state:
    st.session_state['job_description'] = None
if 'job_title' not in st.session_state:
    st.session_state['job_title'] = None

# Load existing resumes
existing_resumes = resume_utils.list_resumes()

# Create two columns for the layout
col1, col2 = st.columns([1, 2])

with col1:
    # Option to select existing resume
    selected_resume = st.selectbox("Select Existing Resume", [""] + existing_resumes)

    if selected_resume:
        resume_path = os.path.join(resume_utils.RESUME_DIR, selected_resume)
        st.session_state['resume_path'] = resume_path
        st.session_state['resume_text'] = resume_utils.load_resume(resume_path).get('text', '')
        st.session_state['pdf_uploaded'] = True
        st.success(f"Resume '{selected_resume}' loaded successfully!")
    else:
        # File uploader for PDF resume
        uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=['pdf'])

        if uploaded_file is not None and not st.session_state['pdf_uploaded']:
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                
                # Save uploaded resume
                resume_name = uploaded_file.name.replace(".pdf", "")
                resume_path = resume_utils.save_uploaded_resume(uploaded_file, resume_name, resume_text)
                st.session_state['resume_path'] = resume_path
                st.session_state['resume_text'] = resume_text
                st.session_state['pdf_uploaded'] = True
                st.success("Resume uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")

with col2:
    # Only show the rest of the interface if PDF is uploaded
    if st.session_state['pdf_uploaded']:
        # Job details input
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description")

        if st.button("Analyze Resume"):
            if job_description and job_title:
                with st.spinner("Analyzing your resume..."):
                    # Process with local matching
                    keywords = local_match_utils.extract_keywords_from_text(job_description)
                    categorized_keywords = local_match_utils.categorize_keywords(keywords)
                    # Store in session state
                    st.session_state['categorized_keywords'] = categorized_keywords
                    st.session_state['job_description'] = job_description
                    st.session_state['job_title'] = job_title
                    
                    # Calculate scores
                    overall_score = local_match_utils.calculate_keyword_match_score(
                        job_description, st.session_state['resume_text'], keywords)
                    technical_score = local_match_utils.calculate_technical_skills_match_score(
                        job_description, st.session_state['resume_text'])
                    
                    # Display overall match score with a progress bar
                    st.subheader("Overall Match Score")
                    st.progress(overall_score / 100)
                    st.write(f"{overall_score}% match with the job description")
                    
                    # Display technical skills score
                    st.subheader("Technical Skills Match")
                    st.progress(technical_score / 100)
                    st.write(f"{technical_score}% match on technical skills")
                    
                    # Count matched keywords
                    matched_count = sum(1 for v in local_match_utils.get_keyword_matches(keywords, st.session_state['resume_text']).values() if v)
                    total_count = len(keywords)
                    
                    # Display keyword match summary
                    st.subheader("Keyword Match Analysis")
                    status = "Excellent" if overall_score >= 70 else "Needs Work"
                    st.write(f"Status: {status}")
                    st.write(f"Your resume matches {matched_count} out of {total_count} keywords from the job description.")
                    
                    # Create two columns for high and low priority keywords
                    col_high, col_low = st.columns(2)
                    
                    with col_high:
                        st.subheader("High Priority Keywords")
                        matched_high = []
                        unmatched_high = []
                        for keyword in categorized_keywords["high"]:
                            if local_match_utils.get_keyword_matches(keywords, st.session_state['resume_text']).get(keyword, False):
                                matched_high.append(f"✓ {keyword}")
                            else:
                                unmatched_high.append(f"✗ {keyword}")
                        
                        all_high_keywords = "\n".join(matched_high + unmatched_high)
                        st.text_area(
                            "Matched (✓) and Unmatched (✗) Technical Skills",
                            value=all_high_keywords,
                            height=200,
                            key="high_priority_keywords"
                        )
                    
                    with col_low:
                        st.subheader("Low Priority Keywords")
                        matched_low = []
                        unmatched_low = []
                        for keyword in categorized_keywords["low"]:
                            if local_match_utils.get_keyword_matches(keywords, st.session_state['resume_text']).get(keyword, False):
                                matched_low.append(f"✓ {keyword}")
                            else:
                                unmatched_low.append(f"✗ {keyword}")
                        
                        all_low_keywords = "\n".join(matched_low + unmatched_low)
                        st.text_area(
                            "Matched (✓) and Unmatched (✗) Soft Skills",
                            value=all_low_keywords,
                            height=200,
                            key="low_priority_keywords"
                        )
                    
                    if overall_score < 70:
                        st.warning("Try to get your score above 70% to increase your chances!")
                        st.write("Tips to improve your score:")
                        st.write("1. Add missing keywords naturally in your resume")
                        st.write("2. Focus on adding technical skills that are missing")
                        st.write("3. Use similar terminology as the job description")
                st.markdown("---")  # Add a separator
                if st.button("🎯 Tailor Resume", key="tailor_resume_btn"):
                    if 'categorized_keywords' not in st.session_state or not st.session_state['categorized_keywords']:
                        st.error("Please analyze your resume first to extract keywords.")
                        st.stop()

                    with st.spinner("Generating tailored resume..."):
                        # Personal information (you can make this configurable through UI later)
                        personal_info = {
                            "name": "Vishal Bansal",
                            "location": "Bharatpur, RJ",
                            "phone": "+91 9057291541",
                            "email": "bvansal.vb@gmail.com",
                            "linkedin": "www.linkedin.com/in/vishal-bansal-62a727192/",
                            "github": "https://github.com/vishalbansal28",
                            "website": "https://vishal-portfolio-tawny.vercel.app/"
                        }
                        
                        education = {
                            "institute": "National Institute Of Technology, Bhopal",
                            "degree": "Bachelor of Technology",
                            "major": "Electronics and Communication Engineering",
                            "duration": "Nov 2020-April 2024",
                            "cgpa": "7.58"
                        }
                        
                        try:
                            # Get technical and soft skills from categorized keywords
                            technical_skills = st.session_state['categorized_keywords'].get("high", [])
                            soft_skills = st.session_state['categorized_keywords'].get("low", [])
                            
                            if not technical_skills and not soft_skills:
                                st.error("No keywords found. Please analyze your resume first.")
                                st.stop()
                            
                            # Generate PDF resume
                            pdf_path = resume_generator.generate_latex_resume(
                                personal_info=personal_info,
                                education=education,
                                job_description=st.session_state['job_description'],
                                job_title=st.session_state['job_title'],
                                technical_skills=technical_skills,
                                soft_skills=soft_skills
                            )
                            
                            if pdf_path:
                                # Add download button for the PDF file
                                with open(pdf_path, "rb") as pdf_file:
                                    st.download_button(
                                        label="Download PDF Resume",
                                        data=pdf_file,
                                        file_name="tailored_resume.pdf",
                                        mime="application/pdf"
                                    )
                            else:
                                st.error("Failed to generate resume. Please check the error messages above.")
                        except Exception as e:
                            st.error(f"Error generating resume: {str(e)}")
            else:
                st.warning("Please enter both job description and job title to analyze.")
    else:
        st.info("Please upload your resume or select an existing one to begin the analysis.")
