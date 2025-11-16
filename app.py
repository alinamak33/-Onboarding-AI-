import csv
import os
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ---------------- Load environment ----------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("AIzaSyCsHTh6bko58GYXENJoqWd3VLHldvIO3Xw")

if GENAI_AVAILABLE and GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"⚠️ Could not configure Google Generative AI: {e}")
        GENAI_AVAILABLE = False
else:
    GENAI_AVAILABLE = False

# ---------------- Functions ----------------
def load_questions(csv_file):
    """Load all questions from CSV file"""
    questions = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'question' in row and row['question'].strip():
                    questions.append(row['question'])
    except FileNotFoundError:
        print(f"❌ File '{csv_file}' not found. Please make sure it's in the same folder.")
        exit()
    return questions


def save_response_to_csv(output_file, question, response, summary=None):
    """Save responses (and optional summary) to a CSV file"""
    write_header = not os.path.exists(output_file) or os.path.getsize(output_file) == 0
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question', 'response', 'summary'])
        if write_header:
            writer.writeheader()
        writer.writerow({'question': question, 'response': response, 'summary': summary or ''})


def summarize_response_with_gemini(response):
    """Generate a short summary of the user's response using Gemini"""
    if not GENAI_AVAILABLE:
        return None
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Summarize this short answer in 1-2 sentences: {response}"
        result = model.generate_content(prompt)
        if hasattr(result, "text"):
            return result.text.strip()
        return str(result)
    except Exception as e:
        print(f"⚠️ AI summary failed: {e}")
        return None


# ---------------- Main App ----------------
def main():
    print("🤖 Welcome to Amber AI Onboarding CLI!")
    print("----------------------------------------")

    questions = load_questions("amberdata - Sheet1.csv")
    output_file = "onboarding_data.csv"

    for i, question in enumerate(questions, start=1):
        print(f"\nQuestion {i}/{len(questions)}:")
        print(f"{question}")
        response = input("Your answer: ").strip()

        if not response:
            print("⚠️ Empty answer skipped.")
            continue

        summary = summarize_response_with_gemini(response)
        if summary:
            print(f"Gemini summary: {summary}")

        save_response_to_csv(output_file, question, response, summary)

    print("\n🎉 Thank you! All responses saved to 'onboarding_data.csv'.")


if __name__ == "__main__":
    main()
