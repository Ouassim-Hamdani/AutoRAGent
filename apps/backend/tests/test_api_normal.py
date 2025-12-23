import requests
import json
import sys

def test_chat_stream():
    url = "http://localhost:2003/chat"
    
    # Test payload
    # The new query is now the last element of the history
    history = [
        {
            "role": "user",
            "content": "Can you list all available collections in the vector database?",
            "files_paths": []
        }
    ]
    
    payload = {
        "session_id": "test-session-001",
        "history": json.dumps(history) # Send as JSON string
    }

    print(f"Sending request to {url}...")
    print("-" * 50)

    try:
        with requests.post(url, data=payload, stream=True) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    # Decode the bytes to string
                    decoded_line = line.decode('utf-8')
                    try:
                        # Parse the NDJSON line
                        data = json.loads(decoded_line)
                        
                        event_type = data.get("type")
                        content = data.get("content")
                        
                        # Print based on type
                        if event_type == "code":
                            print(f"\n[CODE GENERATION]:\n{content}")
                        elif event_type == "final":
                            print(f"\n[FINAL ANSWER]:\n{content}")
                        else:
                            print(f"[LOG]: {content}")
                            
                    except json.JSONDecodeError:
                        print(f"Raw output: {decoded_line}")
                        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running on port 2003?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_chat_stream()
