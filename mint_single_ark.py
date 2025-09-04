import json
import csv
import os
import requests
import base64
from pathlib import Path
import time

# EZID API configuration
EZID_BASE_URL = "https://ezid.cdlib.org"
SHOULDER = "ark:/87293/d3"  # UC Davis ARK shoulder
USERNAME = "ucd-dams-3"
PASSWORD = "ezid2025!"

def get_auth_header():
    """Create Basic Auth header for EZID API"""
    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}

def mint_ark(metadata):
    """Mint a new ARK using the EZID API"""
    url = f"{EZID_BASE_URL}/shoulder/{SHOULDER}"
    headers = {
        "Content-Type": "text/plain; charset=UTF-8",
        "Accept": "text/plain",
        **get_auth_header()
    }
    
    # Format metadata in ANVL format
    anvl_metadata = []
    anvl_metadata.append(f"_target: {metadata.get('target_url', '')}")
    anvl_metadata.append(f"_profile: erc")
    anvl_metadata.append(f"erc.what: {metadata.get('title', '')}")
    
    # Combine all FAST IDs into a single erc.who field
    fast_names = [fast_id['name'] for fast_id in metadata.get('fast_ids', [])]
    if fast_names:
        anvl_metadata.append(f"erc.who: {'; '.join(fast_names)}")
    
    # Join metadata with newlines
    data = "\n".join(anvl_metadata)
    
    try:
        print(f"Sending request to {url}")
        print(f"With metadata:\n{data}")
        
        response = requests.post(url, headers=headers, data=data)
        
        # Print full response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        response.raise_for_status()
        
        # Extract ARK from response
        if response.text.startswith("success:"):
            return response.text.split("success:")[1].strip()
        else:
            print(f"Error minting ARK: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Error response: {e.response.text}")
        return None

def process_jsonld_file(file_path):
    """Process a single JSON-LD file to mint and update ARK"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check if file already has an ARK
        existing_ark = data.get('schema:identifier', [])
        print(f"Current ARK: {existing_ark}")
        
        # Extract metadata
        metadata = {
            'title': data.get('schema:name', ''),
            'fast_ids': [
                {
                    'id': item.get('@id', ''),
                    'name': item.get('schema:name', '')
                }
                for item in data.get('schema:about', [])
            ],
            'target_url': f"https://digital.ucdavis.edu/collection/{os.path.basename(file_path).replace('.jsonld.json', '')}"
        }
        
        print(f"Extracted metadata: title='{metadata['title']}', fast_ids={len(metadata['fast_ids'])}")
        
        # Mint new ARK
        new_ark = mint_ark(metadata)
        if new_ark:
            # Update JSON-LD with new ARK
            data['schema:identifier'] = [new_ark]
            
            # Write updated JSON-LD back to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Updated {file_path} with new ARK: {new_ark}")
            
            # Respect rate limits
            time.sleep(1)
        else:
            print(f"Failed to mint ARK for {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Read metadata to get collection ID
    try:
        with open('metadata.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            row = next(reader)
            collection_id = row.get('collection_id', '').strip()
    except Exception as e:
        print(f"❌ Error reading metadata.csv: {e}")
        return
    
    if not collection_id:
        print("❌ No collection_id found in metadata.csv")
        return
    
    # Process the main item JSON-LD file
    item_file = Path(f"items/{collection_id}.jsonld.json")
    
    if not item_file.exists():
        print(f"Item file {item_file} does not exist!")
        return
    
    print(f"Processing main item file: {item_file}")
    print(f"{'='*50}")
    process_jsonld_file(item_file)

if __name__ == "__main__":
    main() 