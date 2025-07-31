import google.generativeai as genai
import os
from dotenv import load_dotenv

def get_llm_model():
    """
    Loads the environment variables, configures the Gemini API,
    and returns an instance of the generative model.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key for Gemini not found. Please set the GEMINI_API_KEY environment variable.")
    
    genai.configure(api_key=api_key)
    
    # Initialize the model.
    model = genai.GenerativeModel('gemma-3n-e2b-it')
    
    return model

# This block allows the script to be run directly for testing purposes.
if __name__ == "__main__":
    try:
        llm = get_llm_model()
        print("Successfully initialized the language model.")
        # Example of how to use the 'llm' object:
        # response = llm.generate_content("Tell me a joke about AI.")
        # print(response.text)
    except ValueError as e:
        print(f"Error: {e}")
