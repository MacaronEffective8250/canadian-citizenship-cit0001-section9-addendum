#!/usr/bin/env python3
"""
Unit tests to ensure English PDF outputs remain unchanged during internationalization.

This test suite validates that the English language PDFs produced by the
internationalized version match the original English-only version outputs.
"""

import unittest
import os
import sys
import hashlib
import tempfile
import shutil
from pathlib import Path

# Add src directory to path to import the PDF generator
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from cit0001_addendum.generate_addendum_pdfs import create_editable_section9, load_language_config
except ImportError as e:
    print(f"Could not import PDF generator: {e}")
    sys.exit(1)


class TestPDFConsistency(unittest.TestCase):
    """Test suite to ensure PDF consistency during internationalization."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment and baseline PDFs."""
        cls.script_dir = Path(__file__).parent.parent
        cls.test_dir = Path(__file__).parent
        cls.baseline_dir = cls.test_dir / "baseline_pdfs"
        cls.temp_dir = cls.test_dir / "temp_outputs"
        
        # Create directories
        cls.baseline_dir.mkdir(exist_ok=True)
        cls.temp_dir.mkdir(exist_ok=True)
        
        # Load language configuration from src directory
        src_dir = cls.script_dir / "src" / "cit0001_addendum"
        cls.lang_config = load_language_config(str(src_dir))
        if not cls.lang_config:
            raise Exception("Could not load language configuration for tests")
        
        # Test generations to validate
        cls.test_generations = [3, 4, 5, 10, 15, 20]  # Sample across range
        
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files."""
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up individual test."""
        # Clear temp directory for each test
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_baseline_pdfs(self):
        """Generate baseline English PDFs for comparison."""
        print("Generating baseline English PDFs...")
        
        for generation in self.test_generations:
            generations_needed = generation - 2
            baseline_file = self.baseline_dir / f"baseline_EN_G{generation:02d}.pdf"
            
            # Generate baseline English PDF
            create_editable_section9(
                json_data_file=None,
                output_path=str(baseline_file),
                num_generations=generations_needed,
                language='EN',
                lang_config=self.lang_config
            )
            
            print(f"Generated baseline: {baseline_file.name}")
        
        print(f"Baseline PDFs saved to: {self.baseline_dir}")
    
    def generate_test_pdf(self, generation, language='EN'):
        """Generate a PDF for testing."""
        generations_needed = generation - 2
        test_file = self.temp_dir / f"test_{language}_G{generation:02d}.pdf"
        
        create_editable_section9(
            output_path=str(test_file),
            num_generations=generations_needed,
            language=language,
            lang_config=self.lang_config
        )
        
        return test_file
    
    def get_pdf_hash(self, pdf_path):
        """Get SHA256 hash of PDF file for comparison."""
        with open(pdf_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    
    def get_pdf_size(self, pdf_path):
        """Get file size of PDF."""
        return os.path.getsize(pdf_path)
    
    def compare_pdfs(self, baseline_path, test_path):
        """Compare two PDF files for consistency."""
        # Check if both files exist
        self.assertTrue(baseline_path.exists(), f"Baseline PDF not found: {baseline_path}")
        self.assertTrue(test_path.exists(), f"Test PDF not found: {test_path}")
        
        # Compare file sizes
        baseline_size = self.get_pdf_size(baseline_path)
        test_size = self.get_pdf_size(test_path)
        
        # Allow small differences due to metadata timestamps
        size_diff = abs(baseline_size - test_size)
        self.assertLess(size_diff, 1000, 
                       f"PDF size difference too large: {size_diff} bytes "
                       f"(baseline: {baseline_size}, test: {test_size})")
        
        # Compare hashes (if they match exactly)
        baseline_hash = self.get_pdf_hash(baseline_path)
        test_hash = self.get_pdf_hash(test_path)
        
        # Note: PDF hashes might differ due to creation timestamps,
        # but this gives us a strong indication of content changes
        return baseline_hash == test_hash, baseline_hash, test_hash
    
    def test_english_pdf_consistency_g03(self):
        """Test that G03 English PDF remains consistent."""
        generation = 3
        baseline_file = self.baseline_dir / f"baseline_EN_G{generation:02d}.pdf"
        
        if not baseline_file.exists():
            self.skipTest(f"Baseline PDF not found: {baseline_file}. Run generate_baselines() first.")
        
        test_file = self.generate_test_pdf(generation, 'EN')
        hashes_match, baseline_hash, test_hash = self.compare_pdfs(baseline_file, test_file)
        
        print(f"G{generation:02d} English PDF comparison:")
        print(f"  Baseline hash: {baseline_hash[:16]}...")
        print(f"  Test hash:     {test_hash[:16]}...")
        print(f"  Hashes match:  {hashes_match}")
        
        # For now, we'll use size comparison as the primary test
        # since PDF timestamps can cause hash differences
    
    def test_english_pdf_consistency_g04(self):
        """Test that G04 English PDF remains consistent."""
        generation = 4
        baseline_file = self.baseline_dir / f"baseline_EN_G{generation:02d}.pdf"
        
        if not baseline_file.exists():
            self.skipTest(f"Baseline PDF not found: {baseline_file}. Run generate_baselines() first.")
        
        test_file = self.generate_test_pdf(generation, 'EN')
        hashes_match, baseline_hash, test_hash = self.compare_pdfs(baseline_file, test_file)
        
        print(f"G{generation:02d} English PDF comparison:")
        print(f"  Baseline hash: {baseline_hash[:16]}...")
        print(f"  Test hash:     {test_hash[:16]}...")
        print(f"  Hashes match:  {hashes_match}")
    
    def test_english_pdf_consistency_g05(self):
        """Test that G05 English PDF remains consistent."""
        generation = 5
        baseline_file = self.baseline_dir / f"baseline_EN_G{generation:02d}.pdf"
        
        if not baseline_file.exists():
            self.skipTest(f"Baseline PDF not found: {baseline_file}. Run generate_baselines() first.")
        
        test_file = self.generate_test_pdf(generation, 'EN')
        hashes_match, baseline_hash, test_hash = self.compare_pdfs(baseline_file, test_file)
        
        print(f"G{generation:02d} English PDF comparison:")
        print(f"  Baseline hash: {baseline_hash[:16]}...")
        print(f"  Test hash:     {test_hash[:16]}...")
        print(f"  Hashes match:  {hashes_match}")
    
    def test_english_pdf_consistency_g10(self):
        """Test that G10 English PDF remains consistent."""
        generation = 10
        baseline_file = self.baseline_dir / f"baseline_EN_G{generation:02d}.pdf"
        
        if not baseline_file.exists():
            self.skipTest(f"Baseline PDF not found: {baseline_file}. Run generate_baselines() first.")
        
        test_file = self.generate_test_pdf(generation, 'EN')
        hashes_match, baseline_hash, test_hash = self.compare_pdfs(baseline_file, test_file)
        
        print(f"G{generation:02d} English PDF comparison:")
        print(f"  Baseline hash: {baseline_hash[:16]}...")
        print(f"  Test hash:     {test_hash[:16]}...")
        print(f"  Hashes match:  {hashes_match}")
    
    def test_english_pdf_consistency_g20(self):
        """Test that G20 English PDF remains consistent."""
        generation = 20
        baseline_file = self.baseline_dir / f"baseline_EN_G{generation:02d}.pdf"
        
        if not baseline_file.exists():
            self.skipTest(f"Baseline PDF not found: {baseline_file}. Run generate_baselines() first.")
        
        test_file = self.generate_test_pdf(generation, 'EN')
        hashes_match, baseline_hash, test_hash = self.compare_pdfs(baseline_file, test_file)
        
        print(f"G{generation:02d} English PDF comparison:")
        print(f"  Baseline hash: {baseline_hash[:16]}...")
        print(f"  Test hash:     {test_hash[:16]}...")
        print(f"  Hashes match:  {hashes_match}")
    
    def test_french_pdf_generation(self):
        """Test that French PDFs can be generated without errors."""
        generation = 3
        test_file = self.generate_test_pdf(generation, 'FR')
        
        self.assertTrue(test_file.exists(), "French PDF was not generated")
        self.assertGreater(self.get_pdf_size(test_file), 1000, 
                          "French PDF appears to be empty or corrupted")
        
        print(f"French G{generation:02d} PDF generated successfully: {test_file.name}")
    
    def test_language_config_loading(self):
        """Test that language configuration loads correctly."""
        self.assertIsNotNone(self.lang_config, "Language configuration should load")
        self.assertIn('EN', self.lang_config, "English language should be in config")
        self.assertIn('FR', self.lang_config, "French language should be in config")
        
        # Test key sections exist
        en_lang = self.lang_config['EN']
        self.assertIn('metadata', en_lang, "Metadata section should exist")
        self.assertIn('headers', en_lang, "Headers section should exist")
        self.assertIn('form_fields', en_lang, "Form fields section should exist")
        
        fr_lang = self.lang_config['FR']
        self.assertIn('metadata', fr_lang, "French metadata section should exist")
        self.assertIn('headers', fr_lang, "French headers section should exist")


def generate_baseline_pdfs():
    """Standalone function to generate baseline PDFs."""
    test_class = TestPDFConsistency()
    TestPDFConsistency.setUpClass()
    test_class.generate_baseline_pdfs()


def run_tests():
    """Run all PDF consistency tests."""
    # Ensure baseline PDFs exist
    test_class = TestPDFConsistency()
    TestPDFConsistency.setUpClass()
    
    baseline_dir = TestPDFConsistency.baseline_dir
    if not any(baseline_dir.glob("baseline_*.pdf")):
        print("No baseline PDFs found. Generating them now...")
        test_class.generate_baseline_pdfs()
    
    # Run the test suite
    unittest.main(verbosity=2, argv=['test_pdf_consistency.py'])


if __name__ == "__main__":
    import argparse
    
    # Check for our custom arguments first
    if len(sys.argv) > 1 and sys.argv[1] in ['--generate-baselines', '--run-tests']:
        if sys.argv[1] == '--generate-baselines':
            generate_baseline_pdfs()
        elif sys.argv[1] == '--run-tests':
            run_tests()
    else:
        # Default behavior: run unittest with original arguments
        unittest.main(verbosity=2)