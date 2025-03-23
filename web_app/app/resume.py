import pdfplumber
from docx import Document
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download stopwords (only required once)
#nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

# 📌 Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

# 📌 Extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()

# 📌 Extract text based on file type
def extract_resume_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are allowed.")

# 📌 Preprocess text for NLP
def preprocess_text(text):
    text = re.sub(r'[^a-z0-9\s]', '', text.lower())  # Remove special characters
    text = text.replace("powerbi", "power bi")  # Ensure "Power BI" is detected  # Convert to lowercase
    text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
    return text

# 📌 Compute similarity score using TF-IDF + Cosine Similarity
def calculate_similarity_score(job_description, resume_text):
    # Preprocess text
    job_description = re.sub(r'[^a-z0-9\s]', '', job_description.lower())
    resume_text = re.sub(r'[^a-z0-9\s]', '', resume_text.lower())
    # Debugging prints
    print("Job Description (First 500 characters):", job_description[:500])
    print("Resume Text (First 500 characters):", resume_text[:500])

    if not job_description or not resume_text:
        return 0.0  # Avoid errors from empty text

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return round(similarity * 100, 2)  # Convert to percentage
# 📌 Extract skills from text
def extract_skills(text, skill_list):
    text = text.lower()  # Convert everything to lowercase
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove special characters
    text_words = set(text.split())  # Convert to a set of words

    matched_skills = [skill for skill in skill_list if skill.lower() in text_words]
    return matched_skills

# 📌 Compute skills match score
def skills_match_score(job_skills, resume_text):
    # Preprocess job skills & resume text
    resume_text = resume_text.lower()
    resume_text = re.sub(r'[^a-z0-9\s]', '', resume_text)  # Remove special characters

    # Normalize job skills (remove extra spaces & special characters)
    job_skills = [re.sub(r'[^a-z0-9\s]', '', skill.strip().lower()) for skill in job_skills.split(",")]

    # Find matched and missing skills
    matched_skills = [skill for skill in job_skills if skill in resume_text.split()]
    additional_info = [skill for skill in job_skills if skill not in matched_skills]

    # Ensure no empty lists
    matched_skills = matched_skills if matched_skills else ["None"]
    additional_info = additional_info if additional_info else ["None"]

    return (len(matched_skills) / len(job_skills)) * 100, matched_skills, additional_info

# 📌 Identify missing skills
def missing_skills(job_skills, resume_text):
    job_skills_set = set(job_skills.lower().split(","))
    resume_skills = set(extract_skills(resume_text, job_skills_set))
    return list(job_skills_set - resume_skills)

def process_scorecard(file_path):
    text = ""

    # 🛑 **Check if the file is an Image → Convert to PDF**
    if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        print("[INFO] Converting Image to PDF...")
        file_path = convert_image_to_pdf(file_path)  # Convert to PDF

    # ✅ **Extract Text from PDF**
    print("[INFO] Extracting text from PDF...")
    text = extract_text_from_pdf(file_path)

    # 🛑 **If text extraction fails → Use OCR**
    if not text.strip():
        print("[INFO] PDF text extraction failed! Using OCR...")
        text = extract_text_from_image(file_path)  # OCR Extraction

    return text



