import os
import json
import time
import fitz
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

# ----------------------------
# Load Environment Variables
# ----------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("GEMINI_API_KEY not found in .env")

# Create Gemini Client
client = genai.Client(api_key=API_KEY)

# ----------------------------
# Flask App
# ----------------------------

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ----------------------------
# Home
# ----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# Analyze Resume
# ----------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # ----------------------------
        # Check File
        # ----------------------------

        if "resume" not in request.files:
            return jsonify({"error": "No resume uploaded"}), 400

        file = request.files["resume"]

        if file.filename == "":
            return jsonify({"error": "Please select a PDF"}), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

        file.save(filepath)

        # ----------------------------
        # Extract PDF Text
        # ----------------------------

        resume_text = ""

        doc = fitz.open(filepath)

        for page in doc:
            resume_text += page.get_text()

        doc.close()

        if resume_text.strip() == "":
            return jsonify({"error": "No readable text found in the PDF"}), 400

        # ----------------------------
        # Prompt
        # ----------------------------

        prompt = f"""
You are an experienced HR recruiter.

Analyze the following resume.

Return ONLY valid JSON.

Do NOT include markdown.
Do NOT include ```json.

Return exactly in this format:

{{
    "summary":"",

    "skills":[
        "",
        ""
    ],

    "strengths":[
        "",
        ""
    ],

    "weaknesses":[
        "",
        ""
    ],

    "suggestions":[
        "",
        ""
    ]
}}

Resume:

{resume_text}
"""

       # ----------------------------
# Gemini
# ----------------------------

        # ----------------------------
        # Gemini
        # ----------------------------

        response = None

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

                break

            except Exception as e:

                print(f"Attempt {attempt + 1} failed: {e}")

                if attempt == 2:
                    raise e

                time.sleep(5)

        if response is None:
            return jsonify({"error": "Failed to get response from Gemini"}), 500

        ai_text = response.text

        if not ai_text:
            return jsonify({"error": "Gemini returned an empty response"}), 500

        ai_text = ai_text.strip()

        # Remove markdown if Gemini returns it
        ai_text = ai_text.replace("```json", "")
        ai_text = ai_text.replace("```", "")
        ai_text = ai_text.strip()

        

        # Remove markdown if Gemini returns it
        ai_text = ai_text.replace("```json", "")
        ai_text = ai_text.replace("```", "")
        ai_text = ai_text.strip()

        # ----------------------------
        # Convert JSON
        # ----------------------------

        try:

            result = json.loads(ai_text)

        except json.JSONDecodeError:

            result = {
                "summary": ai_text,
                "skills": [],
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }

        return jsonify(result)

    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


# ----------------------------
# Run App
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)