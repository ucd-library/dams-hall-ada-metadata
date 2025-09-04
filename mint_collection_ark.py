import json
import csv
import requests
import base64
from pathlib import Path

# EZID API configuration
EZID_BASE_URL = "https://ezid.cdlib.org"
SHOULDER = "ark:/87293/d3"  # UC Davis ARK shoulder
USERNAME = "ucd-dams-3"
PASSWORD = "ezid2025!"

def get_auth_header():
    """Create Basic Auth header for EZID API"""
    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}

def mint_collection_ark(metadata):
    """Mint a new ARK for the collection using the EZID API"""
    url = f"{EZID_BASE_URL}/shoulder/{SHOULDER}"
    headers = {
        "Content-Type": "text/plain; charset=UTF-8",
        "Accept": "text/plain",
        **get_auth_header()
    }
    
    # Format metadata in ANVL format for collection
    anvl_metadata = []
    anvl_metadata.append(f"_target: {metadata.get('target_url', '')}")
    anvl_metadata.append(f"_profile: erc")
    anvl_metadata.append(f"erc.what: {metadata.get('title', '')}")
    anvl_metadata.append(f"erc.who: {metadata.get('creator', '')}")
    
    # Add subject information
    subjects = metadata.get('subjects', [])
    if subjects:
        subject_names = [subj for subj in subjects if subj]
        if subject_names:
            anvl_metadata.append(f"erc.where: {'; '.join(subject_names[:3])}")  # First 3 subjects
    
    data = "\n".join(anvl_metadata)
    
    try:
        print(f"🚀 Minting new collection ARK...")
        print(f"Metadata:\n{data}")
        
        response = requests.post(url, headers=headers, data=data)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        response.raise_for_status()
        
        if response.text.startswith("success:"):
            return response.text.split("success:")[1].strip()
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None

def update_collection_ark():
    """Update the collection with a new ARK based on metadata.csv"""
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
    
    collection_file = Path(f"collection/{collection_id}.jsonld.json")
    
    if not collection_file.exists():
        print(f"❌ File {collection_file} not found!")
        return
    
    # Read current data
    with open(collection_file, 'r') as f:
        data = json.load(f)
    
    # Get current identifier
    current_identifier = data.get('schema:identifier', [])
    print(f"📋 Current identifier: {current_identifier}")
    
    # Extract metadata
    metadata = {
        'title': data.get('schema:name', ''),
        'creator': data.get('schema:creator', ''),
        'subjects': [
            item.get('schema:name', '')
            for item in data.get('schema:about', [])
            if item.get('schema:name')
        ],
        'target_url': f"https://digital.ucdavis.edu/collection/{collection_id.lower()}"
    }
    
    print(f"📝 Title: '{metadata['title']}'")
    print(f"📝 Creator: '{metadata['creator']}'")
    print(f"📝 Subjects: {len(metadata['subjects'])} FAST headings")
    
    # Confirm
    response = input(f"\n🔄 Mint new ARK for collection? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cancelled.")
        return
    
    # Mint new ARK
    new_ark = mint_collection_ark(metadata)
    if new_ark:
        # Update identifier with new ARK
        new_identifier = [
            collection_id,
            new_ark
        ]
        
        data['schema:identifier'] = new_identifier
        
        # Save updated file
        with open(collection_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ SUCCESS!")
        print(f"🆕 New ARK: {new_ark}")
        print(f"📁 Updated: {collection_file}")
        print(f"🔧 Updated identifier with new ARK")
        
    else:
        print(f"❌ Failed to mint new ARK")

if __name__ == "__main__":
    print("🔧 MINTING NEW COLLECTION ARK")
    print("="*50)
    update_collection_ark() 