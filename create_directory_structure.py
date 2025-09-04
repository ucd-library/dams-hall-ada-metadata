#!/usr/bin/env python3
"""
Script to create directory structure for photo album collections.
This creates the structure needed for book-style collections with sequential pages.
"""

import os
import csv
import shutil
from pathlib import Path

def read_collection_metadata():
    """Read collection metadata from CSV file"""
    try:
        with open('metadata.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                return row
    except FileNotFoundError:
        print("Error: metadata.csv not found. Please create this file first.")
        return None
    except Exception as e:
        print(f"Error reading metadata.csv: {e}")
        return None

def create_photo_album_structure(collection_id):
    """Create the directory structure for a photo album collection"""
    
    # Create main directories
    os.makedirs(f"collection/{collection_id}", exist_ok=True)
    os.makedirs(f"items/{collection_id}/media/images", exist_ok=True)
    
    print(f"Created directory structure for collection {collection_id}")
    print(f"  - collection/{collection_id}/")
    print(f"  - items/{collection_id}/media/images/")

def move_files_to_structure(collection_id):
    """Move TIFF images and PDFs from images/ folder to the proper structure"""
    
    source_dir = "images"
    images_target_dir = f"items/{collection_id}/media/images"
    media_target_dir = f"items/{collection_id}/media"
    
    if not os.path.exists(source_dir):
        print(f"Warning: {source_dir} directory not found. Please create it and add your files.")
        return
    
    # Get all TIFF files and sort them
    tiff_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.tif')]
    tiff_files.sort()
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')]
    
    if not tiff_files and not pdf_files:
        print(f"Warning: No TIFF or PDF files found in {source_dir}")
        return
    
    # Copy TIFF files to images subdirectory
    if tiff_files:
        print(f"Found {len(tiff_files)} TIFF files")
        for tiff_file in tiff_files:
            source_path = os.path.join(source_dir, tiff_file)
            target_path = os.path.join(images_target_dir, tiff_file)
            
            # Copy file (don't move to preserve original)
            shutil.copy2(source_path, target_path)
            print(f"  Copied {tiff_file} to {images_target_dir}")
        
        print(f"All {len(tiff_files)} TIFF images copied to {images_target_dir}")
    
    # Copy PDF files to media directory (same level as images)
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF files")
        for pdf_file in pdf_files:
            source_path = os.path.join(source_dir, pdf_file)
            target_path = os.path.join(media_target_dir, pdf_file)
            
            # Copy file (don't move to preserve original)
            shutil.copy2(source_path, target_path)
            print(f"  Copied {pdf_file} to {media_target_dir}")
        
        print(f"All {len(pdf_files)} PDF files copied to {media_target_dir}")

def create_media_container_files(collection_id):
    """Create the media container JSON-LD files"""
    
    # Create media.jsonld.json
    media_data = {
        "@context": {
            "ldp": "http://www.w3.org/ns/ldp#",
            "schema": "http://schema.org/",
            "fedora": "http://fedora.info/definitions/v4/repository#",
            "webac": "http://fedora.info/definitions/v4/webac#",
            "acl": "http://www.w3.org/ns/auth/acl#",
            "ucdlib": "http://digital.ucdavis.edu/schema#",
            "ebucore": "http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#"
        },
        "@id": "",
        "@type": [
            "ldp:DirectContainer"
        ],
        "ldp:hasMemberRelation": {
            "@id": "schema:associatedMedia"
        },
        "ldp:isMemberOfRelation": {
            "@id": "schema:encodesCreativeWork"
        },
        "ldp:membershipResource": {
            "@id": "@base:.."
        }
    }
    
    media_path = f"items/{collection_id}/media.jsonld.json"
    with open(media_path, 'w') as f:
        import json
        json.dump(media_data, f, indent=2)
    
    print(f"Created {media_path}")
    
    # Create images.jsonld.json
    images_data = {
        "@context": {
            "ldp": "http://www.w3.org/ns/ldp#",
            "schema": "http://schema.org/",
            "fedora": "http://fedora.info/definitions/v4/repository#",
            "webac": "http://fedora.info/definitions/v4/webac#",
            "acl": "http://www.w3.org/ns/auth/acl#",
            "ucdlib": "http://digital.ucdavis.edu/schema#",
            "ebucore": "http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#"
        },
        "@id": "",
        "@type": [
            "ucdlib:ImageList",
            "ldp:DirectContainer",
            "schema:MediaObject"
        ],
        "schema:name": "Image List",
        "ldp:hasMemberRelation": {
            "@id": "schema:hasPart"
        },
        "ldp:isMemberOfRelation": {
            "@id": "schema:partOf"
        },
        "ldp:membershipResource": {
            "@id": ""
        }
    }
    
    images_path = f"items/{collection_id}/media/images.jsonld.json"
    with open(images_path, 'w') as f:
        json.dump(images_data, f, indent=2)
    
    print(f"Created {images_path}")

def main():
    """Main function to create the photo album directory structure"""
    print("Creating photo album collection directory structure...")
    print("=" * 60)
    
    # Read collection metadata
    metadata = read_collection_metadata()
    if not metadata:
        return
    
    collection_id = metadata.get('collection_id', '').strip()
    if not collection_id:
        print("Error: collection_id not found in metadata.csv")
        return
    
    print(f"Collection ID: {collection_id}")
    print(f"Title: {metadata.get('title', 'N/A')}")
    print()
    
    # Create directory structure
    create_photo_album_structure(collection_id)
    
    # Move images and PDFs to structure
    move_files_to_structure(collection_id)
    
    # Create media container files
    create_media_container_files(collection_id)
    
    print()
    print("Directory structure creation complete!")
    print("Next steps:")
    print("1. Run create_metadata.py to generate JSON-LD files")
    print("2. Run mint_collection_ark.py to mint collection ARK")
    print("3. Run mint_single_ark.py to mint item ARK")

if __name__ == "__main__":
    main()
