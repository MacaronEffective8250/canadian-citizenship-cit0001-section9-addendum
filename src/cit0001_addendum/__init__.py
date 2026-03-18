"""CIT 0001 Section 9 Grandparent Addendum Generator

This package generates professional, editable PDF addendums for documenting 
great-grandparent citizenship information in Canadian citizenship applications.
"""

__version__ = "1.0.0"
__author__ = "MacaronEffective"

from .generate_addendum_pdfs import main, create_editable_section9, generate_all_generation_documents

__all__ = ["main", "create_editable_section9", "generate_all_generation_documents"]