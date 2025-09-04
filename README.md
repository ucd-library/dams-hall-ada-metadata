# Photo Album Collection Template

Template for building photo album collections for UC Davis DAMS.

## Quick Start

1. **Update `metadata.csv`** with your collection information
2. **Place TIFF files** in `images/` folder (named MC-001_0001.tif, MC-001_0002.tif, etc.)
3. **Create and add PDF** - Combine your TIFFs into a single PDF and place it in the `images/` folder
4. **Run the scripts** in order:

```bash
python3 create_directory_structure.py
python3 create_metadata.py
python3 mint_collection_ark.py
python3 mint_single_ark.py
```

## Required Files

- `metadata.csv` - Your collection metadata
- `images/` folder - Your TIFF files and PDFs

## File Naming

### Images
Use format: `MC-001_0001.tif`, `MC-001_0002.tif`, etc.
- Must be sequential starting from 0001
- Same collection ID prefix for all images

### PDFs
**Important**: You need to create a PDF from your TIFF images and include it in the `images/` folder.
- **Create PDF**: Combine all your TIFF images into a single PDF (e.g., using Adobe Acrobat, Preview, or other tools)
- **Naming**: Use your collection ID (e.g., `MC-001.pdf`)
- **Placement**: Put the PDF in the `images/` folder alongside your TIFF files
- **Result**: Scripts will automatically copy it to the correct location and generate JSON-LD metadata

## CSV Format

```csv
collection_id,title,description,creator,date_range,fast_id_1,fast_id_2,fast_id_3
MC-001,"Your Title","Description","Creator","1937-1941","http://id.worldcat.org/fast/1204928","",""
```

## Next Steps

After running the scripts, import to DAMS:
```bash
fin io import .
```

## 💡 PDF Creation Tips

**Tools to create PDFs from TIFF images:**
- **macOS**: Preview app (File → New from Clipboard, then drag images)
- **Windows**: Adobe Acrobat, or online tools like SmallPDF
- **Linux**: ImageMagick (`convert *.tif output.pdf`)
- **Online**: CombinePDF, ILovePDF, or similar services

**Best practices:**
- Ensure images are in correct order before creating PDF
- Use consistent naming (MC-001.pdf matches your collection ID)
- Test PDF opens correctly before adding to images folder

For detailed workflow, see `WORKFLOW.md`.
