#!/usr/bin/env python3
"""
Script to create metadata for photo album collections.
This generates collection-level and page-level JSON-LD files for book-style collections.
"""

import os
import csv
import json
from pathlib import Path

def create_jsonld_context():
    """Create the JSON-LD context for DAMS collections"""
    return {
        "ldp": "http://www.w3.org/ns/ldp#",
        "schema": "http://schema.org/",
        "fedora": "http://fedora.info/definitions/v4/repository#",
        "webac": "http://fedora.info/definitions/v4/webac#",
        "acl": "http://www.w3.org/ns/auth/acl#",
        "ucdlib": "http://digital.ucdavis.edu/schema#",
        "ebucore": "http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#"
    }

def build_fast_subjects(metadata_row):
    """Build schema:about array from FAST ID columns in the CSV"""
    subjects = []
    
    # Check for FAST ID columns (fast_id_1, fast_id_2, fast_id_3, etc.)
    for i in range(1, 13):  # Check up to 12 FAST IDs
        fast_id_col = f'fast_id_{i}'
        
        if fast_id_col in metadata_row:
            fast_id = metadata_row[fast_id_col].strip()
            
            if fast_id:  # Only add if fast_id exists
                subjects.append({
                    "@id": fast_id
                })
    
    return subjects

def create_collection_jsonld(metadata_row, collection_id):
    """Create the main collection JSON-LD file"""
    
    # Build FAST subjects
    fast_subjects = build_fast_subjects(metadata_row)
    
    collection_data = {
        "@context": create_jsonld_context(),
        "@id": "",
        "@type": [
            "schema:Collection",
            "http://fedora.info/definitions/v4/repository#ArchivalGroup"
        ],
        "ucdlib:hasLabel": {
            "@id": "@base:/labels"
        },
        "schema:name": metadata_row.get('title', '').strip(),
        "schema:description": metadata_row.get('description', '').strip(),
        "schema:creator": metadata_row.get('creator', '').strip(),
        "schema:datePublished": {
            "@type": "http://www.w3.org/2001/XMLSchema#gYear",
            "@value": metadata_row.get('date_range', '').strip()
        },
        "schema:identifier": [
            collection_id,
            "ark:/87293/d3028pm2g"  # Placeholder - will be updated by ARK minting
        ],
        "schema:image": {
            "@id": f"info:fedora/item/ark:/87293/d3028pm2g/media/images/{collection_id}_0001.tif"
        },
        "schema:license": {
            "@id": "http://rightsstatements.org/vocab/InC-NC/1.0/"
        },
        "schema:publisher": [
            "UC Davis Library, Archives and Special Collections",
            {
                "@id": "http://id.loc.gov/authorities/names/no2008108707"
            }
        ],
        "schema:sdDatePublished": {
            "@type": "http://www.w3.org/2001/XMLSchema#gYear",
            "@value": "2025"
        },
        "schema:sdLicense": {
            "@id": "http://rightsstatements.org/vocab/InC-NC/1.0/"
        },
        "schema:sdPublisher": "UC Davis Library, Archives and Special Collections"
    }
    
    # Only add schema:about if we have FAST subjects
    if fast_subjects:
        collection_data["schema:about"] = fast_subjects
    
    return collection_data

def create_labels_jsonld(metadata_row):
    """Create the labels JSON-LD file"""
    
    # Start with the service definition
    labels_data = [
        {
            "@id": "",
            "@context": {
                "ucdlib": "http://digital.ucdavis.edu/schema#"
            },
            "@type": [
                "ucdlib:LabelService",
                "ucdlib:Service"
            ]
        }
    ]
    
    # Add FAST subject labels
    fast_subjects = build_fast_subjects(metadata_row)
    for subject in fast_subjects:
        fast_id = subject["@id"]
        # Get the actual subject name from FAST API
        subject_name = get_fast_subject_name(fast_id)
        
        labels_data.append({
            "@id": fast_id,
            "http://schema.org/name": subject_name
        })
    
    return labels_data

def get_fast_subject_name(fast_id):
    """Get the actual subject name from FAST API"""
    try:
        import requests
        
        # Extract the FAST number from the URL
        fast_number = fast_id.split('/')[-1]
        
        # Use the FAST API to get the actual subject name
        api_url = f"https://experimental.worldcat.org/fast/{fast_number}.json"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Look for the preferred label in the response
            if 'preferredLabel' in data:
                return data['preferredLabel']
            elif 'label' in data:
                return data['label']
            elif 'name' in data:
                return data['name']
            else:
                # If no label found, return the FAST ID as fallback
                return fast_id
        else:
            # If API call fails, return the FAST ID as fallback
            return fast_id
            
    except Exception as e:
        # If any error occurs, return the FAST ID as fallback
        print(f"Warning: Could not fetch FAST subject name for {fast_id}: {e}")
        return fast_id

def create_item_jsonld(metadata_row, collection_id):
    """Create the item JSON-LD file for the photo album"""
    
    # Build FAST subjects
    fast_subjects = build_fast_subjects(metadata_row)
    
    item_data = {
        "@context": create_jsonld_context(),
        "@id": "",
        "@type": [
            "schema:CreativeWork",
            "schema:Book",
            "http://fedora.info/definitions/v4/repository#ArchivalGroup"
        ],
        "schema:associatedMedia": [
            {
                "@id": "@base:/media/images"
            }
        ],
        "schema:creator": metadata_row.get('creator', '').strip(),
        "schema:datePublished": {
            "@type": "http://www.w3.org/2001/XMLSchema#gYear",
            "@value": metadata_row.get('date_range', '').strip()
        },
        "schema:identifier": [
            collection_id,
            "ark:/87293/d3028pm2g"  # Placeholder - will be updated by ARK minting
        ],
        "schema:image": {
            "@id": f"@base:/media/images/{collection_id}_0001.tif"
        },
        "schema:license": {
            "@id": "http://rightsstatements.org/vocab/InC-NC/1.0/"
        },
        "schema:name": metadata_row.get('title', '').strip(),
        "schema:publisher": metadata_row.get('creator', '').strip(),
        "schema:sdDatePublished": {
            "@type": "http://www.w3.org/2001/XMLSchema#gYear",
            "@value": "2025"
        },
        "schema:sdLicense": {
            "@id": "http://rightsstatements.org/vocab/InC-NC/1.0/"
        },
        "schema:sdPublisher": "UC Davis Library, Archives and Special Collections"
    }
    
    # Only add schema:about if we have FAST subjects
    if fast_subjects:
        item_data["schema:about"] = fast_subjects
    
    return item_data

def create_page_jsonld_files(collection_id):
    """Create JSON-LD files for each individual page/image"""
    
    images_dir = f"items/{collection_id}/media/images"
    
    if not os.path.exists(images_dir):
        print(f"Warning: Images directory {images_dir} not found")
        return
    
    # Get all TIFF files and sort them
    tiff_files = [f for f in os.listdir(images_dir) if f.lower().endswith('.tif')]
    tiff_files.sort()
    
    if not tiff_files:
        print(f"Warning: No TIFF files found in {images_dir}")
        return
    
    print(f"Creating JSON-LD files for {len(tiff_files)} images...")
    
    for tiff_file in tiff_files:
        # Extract position from filename (e.g., MC-001_0001.tif -> 0001)
        if '_' in tiff_file and '.' in tiff_file:
            position = tiff_file.split('_')[1].split('.')[0]
        else:
            position = "0001"  # fallback
        
        page_data = {
            "@context": create_jsonld_context(),
            "@id": "",
            "@type": [
                "schema:ImageObject",
                "schema:MediaObject",
                "schema:CreativeWork"
            ],
            "schema:position": position,
            "ebucore:filename": tiff_file,
            "ebucore:hasMimeType": "image/tiff"
        }
        
        json_filename = f"{tiff_file}.jsonld.json"
        json_path = os.path.join(images_dir, json_filename)
        
        with open(json_path, 'w') as f:
            json.dump(page_data, f, indent=2)
        
        print(f"  Created {json_filename}")
    
    print(f"All {len(tiff_files)} page JSON-LD files created")

def create_pdf_jsonld_files(collection_id):
    """Create JSON-LD files for PDF files"""
    
    media_dir = f"items/{collection_id}/media"
    
    if not os.path.exists(media_dir):
        print(f"Warning: Media directory {media_dir} not found")
        return
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(media_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found to create JSON-LD for")
        return
    
    print(f"Creating JSON-LD files for {len(pdf_files)} PDFs...")
    
    for pdf_file in pdf_files:
        pdf_data = {
            "@context": create_jsonld_context(),
            "@id": "",
            "@type": [
                "schema:ImageObject",
                "schema:CreativeWork",
                "schema:MediaObject"
            ],
            "schema:associatedMedia": {
                "@id": "@base:../images"
            },
            "ebucore:filename": pdf_file,
            "ebucore:hasMimeType": "application/pdf"
        }
        
        json_filename = f"{pdf_file}.jsonld.json"
        json_path = os.path.join(media_dir, json_filename)
        
        with open(json_path, 'w') as f:
            json.dump(pdf_data, f, indent=2)
        
        print(f"  Created {json_filename}")
    
    print(f"All {len(pdf_files)} PDF JSON-LD files created")

def main():
    """Main function to create all metadata files"""
    print("Creating photo album collection metadata...")
    print("=" * 60)
    
    # Read collection metadata
    try:
        with open('metadata.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                metadata_row = row
                break
    except FileNotFoundError:
        print("Error: metadata.csv not found. Please create this file first.")
        return
    except Exception as e:
        print(f"Error reading metadata.csv: {e}")
        return
    
    collection_id = metadata_row.get('collection_id', '').strip()
    if not collection_id:
        print("Error: collection_id not found in metadata.csv")
        return
    
    print(f"Collection ID: {collection_id}")
    print(f"Title: {metadata_row.get('title', 'N/A')}")
    print()
    
    # Create collection JSON-LD
    collection_data = create_collection_jsonld(metadata_row, collection_id)
    collection_path = f"collection/{collection_id}.jsonld.json"
    
    with open(collection_path, 'w') as f:
        json.dump(collection_data, f, indent=2)
    
    print(f"Created {collection_path}")
    
    # Create labels JSON-LD
    labels_data = create_labels_jsonld(metadata_row)
    labels_path = f"collection/{collection_id}/labels.jsonld.json"
    
    # Ensure the directory exists
    os.makedirs(f"collection/{collection_id}", exist_ok=True)
    
    with open(labels_path, 'w') as f:
        json.dump(labels_data, f, indent=2)
    
    print(f"Created {labels_path}")
    
    # Create item JSON-LD
    item_data = create_item_jsonld(metadata_row, collection_id)
    item_path = f"items/{collection_id}.jsonld.json"
    
    with open(item_path, 'w') as f:
        json.dump(item_data, f, indent=2)
    
    print(f"Created {item_path}")
    
    # Create page JSON-LD files
    create_page_jsonld_files(collection_id)
    
    # Create PDF JSON-LD files
    create_pdf_jsonld_files(collection_id)
    
    print()
    print("Metadata creation complete!")
    print("Next steps:")
    print("1. Run mint_collection_ark.py to mint collection ARK")
    print("2. Run mint_single_ark.py to mint item ARK")

if __name__ == "__main__":
    main()
