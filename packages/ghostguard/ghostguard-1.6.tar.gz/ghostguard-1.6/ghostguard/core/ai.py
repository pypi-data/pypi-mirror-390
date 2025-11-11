from google import genai

# === Direct API key assignment ===
API_KEY = "AIzaSyAGkClOCgDqvRj3x9DowlbPBIogbvmo47A"  # Replace with your actual key


# === Gemini Client Initialization ===
client = genai.Client(api_key=API_KEY)

# === Prompt Templates ===
CODE_FIX_PROMPT = "Fix syntax errors and improve the following code:\n{}"
COMPLETION_PROMPT = "Suggest 3 possible completions for:\n{}"
GENERAL_PROMPT = "Answer the following question in simple words:\n{}"

def fix_code(code: str) -> str:
    """Fix syntax errors and improve code via Gemini."""
    try:
        prompt = CODE_FIX_PROMPT.format(code)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"[AI Error]: {e}"

def suggest_completion(prefix: str) -> list[str]:
    """Provide AI-powered code completion suggestions."""
    try:
        prompt = COMPLETION_PROMPT.format(prefix)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        return [line.strip() for line in text.split("\n") if line.strip()][:5]
    except Exception as e:
        print(f"[AI Error]: {e}")
        return []

def answer_general(question: str) -> str:
    """Answer general knowledge or conversational questions."""
    try:
        prompt = GENERAL_PROMPT.format(question)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"[AI Error]: {e}"
