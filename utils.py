import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

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

def find_available_logs() -> dict:
    """
    Quét qua các thư mục con để tìm file log và trả về một dictionary
    ánh xạ từ ngày (YYYY-MM-DD) đến đường dẫn file đầy đủ.
    """
    base_dir = "NhatKyKeToan"
    pattern = r"NhatKyKeToan_(\d{4}-\d{2}-\d{2})\.xlsx"
    log_files_map = {}  # Sử dụng dictionary thay vì list

    if not os.path.exists(base_dir):
        return log_files_map

    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            match = re.match(pattern, filename)
            if match:
                date_str = match.group(1)
                # Lấy đường dẫn đầy đủ và thêm vào dictionary
                full_path = os.path.join(root, filename)
                log_files_map[date_str] = full_path

    return log_files_map
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
