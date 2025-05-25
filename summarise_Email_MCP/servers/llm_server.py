from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uvicorn
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import with error handling
try:
    import google.generativeai as genai
    logger.info("Google GenerativeAI imported successfully")
except ImportError as e:
    logger.error(f"Failed to import google.generativeai: {e}")
    raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

# Set your Gemini API Key
def read_api_key_from_file(path: str = "gemini_api_key.txt") -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("❌ API key file not found. Please create gemini_api_key.txt")

API_KEY = read_api_key_from_file()

try:
    genai.configure(api_key=API_KEY)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise

app = FastAPI(title="Email Summarizer API", version="1.0.0")

class SummaryRequest(BaseModel):
    input: str

class SummaryResponse(BaseModel):
    summary: str

@app.get("/")
def read_root():
    return {"message": "Email Summarizer API is running"}

def clean_email_text(text: str) -> str:
    """Pre-process and truncate email text"""
    # Strip out URLs, long signatures, special chars
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text)  # Flatten newlines
    text = text.strip()
    return text[:4000]  # Gemini token safety

@app.post("/summarize", response_model=SummaryResponse)
def summarize(req: SummaryRequest):
    logger.info(f"Received summarize request with input length: {len(req.input)}")
    
    # Pre-clean input
    cleaned_input = clean_email_text(req.input)
    logger.info(f"Cleaned input length: {len(cleaned_input)}")
    
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-pro"
    ]
    
    for model_name in models_to_try:
        try:
            logger.info(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""Please summarize the following email in 2-3 lines, highlighting the main points or action items:\n\n{cleaned_input}"""
            
            logger.info("Sending request to Gemini API")
            response = model.generate_content(prompt)
            logger.info("Received response from Gemini API")
            
            if response and hasattr(response, 'text') and response.text:
                summary_text = response.text.strip()
                logger.info(f"Successfully generated summary using {model_name}")
                return SummaryResponse(summary=summary_text)
            else:
                logger.warning(f"No valid response from {model_name}")
                continue
                
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {str(e)}")
            continue
    
    logger.error("All models failed")
    raise HTTPException(status_code=500, detail="All available models failed to generate summary")

@app.get("/health")
def health_check():
    try:
        logger.info("Testing Gemini API connection")
        model = genai.GenerativeModel("gemini-1.5-flash")
        test_response = model.generate_content("Test summarization")
        return {
            "status": "healthy", 
            "gemini_api": "accessible",
            "test_response": bool(test_response and test_response.text)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

