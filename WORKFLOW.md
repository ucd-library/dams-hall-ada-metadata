# Photo Album Collection Building Workflow

This guide provides step-by-step instructions for building a new photo album collection for the UC Davis DAMS system.

## 📋 Phase 1: Data Preparation

### 1.1 Create Your Metadata CSV

Update `metadata.csv` with your collection data. The format should be:

```csv
collection_id,title,description,creator,date_range,fast_id_1,fast_id_2,fast_id_3
MC-001,"Your Photo Album Title","Description of the album","Creator Name","1937-1941","http://id.worldcat.org/fast/1204928","http://id.worldcat.org/fast/1204929","http://id.worldcat.org/fast/1204927"
```

**Required columns:**
- `collection_id`: Your collection identifier (e.g., MC-001)
- `title`: Collection title
- `description`: Collection description
- `creator`: Creator name(s)
- `date_range`: Date range (e.g., "1937-1941")
- `fast_id_1`, `fast_id_2`, etc.: FAST subject IDs (optional)

### 1.2 Prepare Your Images

Create an `images/` directory and place your TIFF files there:

```
images/
├── MC-001_0001.tif
├── MC-001_0002.tif
├── MC-001_0003.tif
└── ... (all your page images)
```

**Naming conventions:**
- Use consistent naming like `MC-001_0001.tif`, `MC-001_0002.tif`
- Images should be numbered sequentially starting from 0001
- Use the same collection ID prefix for all images

### 1.3 Update Collection Metadata

Edit `collection/collection-name.jsonld.json` with your collection information if needed. The script will generate this automatically from your CSV.

## 🔧 Phase 2: Setup Environment

### 2.1 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Verify Setup

```bash
python3 --version
pip list
```

## 🏗️ Phase 3: Build Collection Structure

### 3.1 Create Directory Structure

```bash
python3 create_directory_structure.py
```

This script will:
- Create `collection/` and `items/` directories with proper structure
- Copy TIFF files from `images/` to the correct location
- Generate JSON-LD templates for media containers
- Set up the photo album folder hierarchy

### 3.2 Generate Collection and Page Metadata

```bash
python3 create_metadata.py
```

This script will:
- Read your `metadata.csv`
- Generate collection-level JSON-LD files
- Generate item-level JSON-LD files
- Create individual page JSON-LD files for each image
- Set up proper relationships between collection, item, and pages

## 🔑 Phase 4: Mint ARKs

### 4.1 Mint Collection ARK

```bash
python3 mint_collection_ark.py
```

This will:
- Call EZID API to mint a unique collection ARK
- Update the collection JSON-LD file with the real ARK
- Register collection metadata with EZID

### 4.2 Mint Item ARK

```bash
python3 mint_single_ark.py
```

This will:
- Process the item JSON-LD file
- Mint a unique ARK for the photo album item
- Update item files with real ARK
- Register item metadata with EZID

## 📤 Phase 5: Import to DAMS

### 5.1 Configure fin

```bash
# For development environment
fin config set host https://dev.dams.library.ucdavis.edu

# For production environment
fin config set host https://digital.ucdavis.edu
```

### 5.2 Authenticate

```bash
fin auth login
```

### 5.3 Import Collection

```bash
fin io import .
```

This will:
- Upload all collection and item metadata
- Create collection and item records in DAMS
- Establish proper relationships between items and collection
- Make your photo album accessible through the DAMS interface

## ✅ Phase 6: Verification

### 6.1 Check Collection

Visit your collection URL to verify:
- Collection metadata is correct
- All pages are present and accessible
- Images display properly
- ARKs resolve correctly

### 6.2 Test ARKs

Test your ARKs by visiting:
- Collection ARK: `https://ezid.cdlib.org/id/your-collection-ark`
- Item ARK: `https://ezid.cdlib.org/id/your-item-ark`

## 🆘 Troubleshooting

### Common Issues

**ARK Conflicts:**
- Check for existing ARKs before minting
- Use ARK comparison scripts if needed
- Ensure collection ARK is unique

**Import Errors:**
- Verify JSON-LD syntax
- Check ARK validity
- Ensure all required fields are present

**Image Issues:**
- Verify TIFF files are valid
- Check file naming consistency
- Ensure images are in the correct directory

**Authentication Issues:**
- Verify fin configuration
- Check login status
- Ensure proper permissions

### Debug Commands

```bash
# Check fin configuration
fin config show

# Check authentication
fin auth status

# Test connection
fin http get /collection

# Check specific collection
fin http get /collection/your-collection-ark
```

## 📚 Additional Resources

- **DAMS Documentation**: [https://digital.ucdavis.edu](https://digital.ucdavis.edu)
- **EZID Documentation**: [https://ezid.cdlib.org](https://ezid.cdlib.org)
- **fin CLI Documentation**: Check fin help commands
- **JSON-LD Schema**: [https://schema.org](https://schema.org)

## 🔄 Key Differences from Individual Item Collections

This photo album template differs from the individual item template in several ways:

1. **Single Item Structure**: Creates one main item (the photo album) instead of multiple individual items
2. **Sequential Page Handling**: Automatically numbers pages based on filename sequence
3. **Book-like Organization**: Treats the collection as a single book with multiple pages
4. **Simplified Metadata**: Focuses on collection-level and page-level metadata rather than item-level
5. **Image Position Tracking**: Automatically assigns position numbers to pages based on filename order
