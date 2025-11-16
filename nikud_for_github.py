"""
סקריפט ניקוד פשוט עם Dicta API - להרצה ב-GitHub Actions
"""
import requests
import time
import sys


def add_nikud_dicta(text):
    """הוספת ניקוד באמצעות Dicta API"""
    urls = [
        "https://nakdan-5-2.loadbalancer.dicta.org.il/addnikud",
        "https://nakdan-5-1.loadbalancer.dicta.org.il/addnikud", 
        "https://nakdan-5-0.loadbalancer.dicta.org.il/addnikud",
    ]
    
    for url in urls:
        try:
            response = requests.post(
                url,
                json={"data": text, "genre": "modern"},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    result = response.json()
                    return result.get('data', text)
                else:
                    print(f"Not JSON from {url}: {content_type}", file=sys.stderr)
                    continue
            else:
                print(f"Error {response.status_code} from {url}", file=sys.stderr)
                continue
                
        except Exception as e:
            print(f"Exception from {url}: {str(e)}", file=sys.stderr)
            continue
    
    return None


def process_vocabulary():
    """מעבד את כל הוקבולרי"""
    print("Loading names...")
    
    with open("vocabulary_expanded.txt", 'r', encoding='utf-8') as f:
        names = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(names)} names")
    print("Adding nikud (this will take a few minutes)...")
    
    results = []
    batch_size = 50
    success_count = 0
    
    for i in range(0, len(names), batch_size):
        batch = names[i:i+batch_size]
        text_batch = "\n".join(batch)
        
        nikud = add_nikud_dicta(text_batch)
        
        if nikud:
            lines = nikud.split('\n')
            results.extend(lines[:len(batch)])
            success_count += len(lines)
            print(f"Progress: {min(i+batch_size, len(names))}/{len(names)}")
        else:
            # Failed - save without nikud
            results.extend(batch)
            print(f"Failed batch: {i//batch_size + 1}")
        
        time.sleep(0.5)  # Wait between requests
    
    # Save results
    with open("vocabulary_expanded_nikud.txt", 'w', encoding='utf-8') as f:
        for result in results:
            f.write(result + '\n')
    
    print(f"\nCompleted!")
    print(f"Success: {success_count}/{len(names)} names")
    
    return success_count, len(names)


if __name__ == "__main__":
    success, total = process_vocabulary()
    
    # Exit with error if less than 50% success
    if success < total * 0.5:
        sys.exit(1)
