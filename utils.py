import os
import re
from config import OLLAMA_PORT, BASE_LOG_DIR, LOG_FILE_PATTERN
from openai import OpenAI

def find_available_logs() -> dict:
    """
    Quét qua các thư mục con để tìm file log và trả về một dictionary
    ánh xạ từ ngày (DD-MM-YYYY) đến đường dẫn file đầy đủ.
    """
    log_files_map = {}

    if not os.path.exists(BASE_LOG_DIR):
        return log_files_map

    for root, dirs, files in os.walk(BASE_LOG_DIR):
        for filename in files:
            match = re.match(LOG_FILE_PATTERN, filename)
            if match:
                date_str = match.group(1)
                full_path = os.path.join(root, filename)
                log_files_map[date_str] = full_path

    return log_files_map

def get_local_llm_client():
    client = OpenAI(
        base_url=f'http://localhost:{OLLAMA_PORT}/v1',
        api_key='ollama',
    )
    return client

# This block allows the script to be run directly for testing purposes.
if __name__ == "__main__":
    try:
        llm = get_local_llm_client()
        print("Successfully initialized the language model.")
    except ValueError as e:
        print(f"Error: {e}")
