# CIT 0001 Section 9 Great Grandparent Addendum Templates

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC0](https://img.shields.io/badge/License-CC0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

Provides editable PDF addendum templates based on Section 9 for great-grandparent citizenship information in Canadian citizenship certificate applications (CIT 0001).

Instructions and links to files are at https://macaroneffective8250.github.io/canadian-citizenship-cit0001-section9-addendum/

**Community**: Created for the https://www.reddit.com/r/Canadiancitizenship community.

## ⚠️ Disclaimer

**These are NOT official government documents.** They are volunteer-created templates to assist with Canadian citizenship certificate applications. This material is provided "as is" without warranties of any kind, either express or implied. The creators assume no responsibility for errors, omissions, or damages arising from use of these documents. 

**Use at your own risk and always verify requirements with official IRCC sources before submitting your application.**

## Quick Start

1. **Visit the website**: See `index.html` (or GitHub Pages) for which PDF to use
2. **Download your document**: Select the appropriate generation template
3. **Fill and submit**: Complete your chosen PDF and submit with your CIT 0001 certificate application

**For developers:** Install dependencies with `pip install reportlab` and run `python generate_addendum.py` to regenerate templates.

## Usage

### Basic Usage

```bash
# Generate all G3-G20 templates (default) creates 36 PDFs
python generate_addendum.py

# Generate specific generation template
python generate_addendum.py -g 4

# Generate specific generation (both EN/FR)
python generate_addendum.py -g 5

# Show help
python generate_addendum.py --help
```

### Regenerating Templates

The `documents/` folder contains pre-generated template PDFs (G03-G20 in both languages). To regenerate them:

1. **Full regeneration** (all 36 templates):
   ```bash
   python generate_addendum.py
   ```

2. **Specific generation** (2 templates - EN/FR):
   ```bash
   python generate_addendum.py -g 5
   ```

3. **Custom range** (modify script parameters):
   ```python
   # Edit src/cit0001_addendum/generate_addendum_pdfs.py
   # Change: generations = range(3, 21)  # G03-G20
   # To:     generations = range(3, 8)   # G03-G07 only
   ```

4. **Custom output filename**:
   ```bash
   python generate_addendum.py -g 4 -o my_form.pdf
   ```
   Note: Custom output generates English version only. For both languages, omit -o flag.

## Testing

Validate PDF generation consistency:

```bash
# Run all tests
python run_tests.py

# Test specific generation
python -m pytest tests/test_pdf_consistency.py::test_specific_generation -v
```

## Files

- `generate_addendum.py` - Main entry point script
- `src/cit0001_addendum/` - Core application package
  - `generate_addendum_pdfs.py` - PDF generator implementation  
  - `language_config.json` - Bilingual text configuration (EN/FR)
  - `generation_mapper.py` - Generation configuration utilities
- `documents/` - Generated template PDFs (36 total documents)
  - `CIT0001_Section9_Grandparent_Addendum_G03_EN.pdf` through `G20_EN.pdf` - English templates
  - `CIT0001_Section9_Grandparent_Addendum_G03_FR.pdf` through `G20_FR.pdf` - French templates
- `index.html` - **Start here** - website explaining which PDF template to use
- `tests/` - Unit testing framework for PDF consistency validation

**Note**: Templates based on [official CIT-0001 guidance](https://www.canada.ca/en/immigration-refugees-citizenship/services/application/application-forms-guides/cit0001.html) and [generation definitions from r/CanadianCitizenship Wiki](https://www.reddit.com/r/Canadiancitizenship/wiki/index/).
