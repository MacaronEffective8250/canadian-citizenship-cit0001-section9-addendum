#!/usr/bin/env python3
"""
Centralized generation mapping service to prevent scattered generation calculations.

This module provides the single source of truth for all generation-related text
in both English and French, eliminating the architectural problems that caused
repeated bugs with mixed generation content.
"""

class GenerationMapper:
    """
    Central authority for all generation text mapping.
    
    Eliminates scattered generation calculations by providing context-aware
    generation text lookup for any combination of:
    - Applicant generation (G3, G4, G5, etc.)  
    - Content context (person being described vs generation being documented)
    - Language (EN/FR)
    """
    
    def __init__(self, lang_config):
        self.lang_config = lang_config
    
    def _english_title_case(self, text):
        """
        Custom title case for English generation text that preserves lowercase 'x' in multipliers.
        
        Converts "2x great-grandparent" to "2x Great-Grandparent" instead of "2X Great-Grandparent"
        """
        if 'x great-' in text:
            # Split on 'x great-' to preserve the 'x'
            parts = text.split('x great-')
            if len(parts) == 2:
                return f"{parts[0]}x Great-{parts[1].title()}"
        return text.title()
        
    def get_french_generation_text(self, generation_number, plural=True):
        """
        Get French generation text for a specific generation number.
        
        Args:
            generation_number (int): The generation number (1, 2, 3, 4, etc.)
            plural (bool): Whether to return plural form
            
        Returns:
            str: French generation text following Canadian convention
        """
        if generation_number == 1:
            return "grands-parents" if plural else "grand-parent"
        elif generation_number == 2:
            return "arrière-grands-parents" if plural else "arrière-grand-parent"
        elif generation_number >= 3:
            base = f"grands-parents de {generation_number}e génération"
            if not plural:
                base = base.replace("grands-parents", "grand-parent")
            return base
        else:
            # Fallback for invalid generations
            return "arrière-grands-parents" if plural else "arrière-grand-parent"
    
    def get_english_generation_text(self, generation_number, plural=True):
        """
        Get English generation text for a specific generation number.
        
        Args:
            generation_number (int): The generation number (1, 2, 3, 4, etc.)
            plural (bool): Whether to return plural form
            
        Returns:
            str: English generation text
        """
        if generation_number == 1:
            return "grandparents" if plural else "grandparent"
        elif generation_number == 2:
            return "great-grandparents" if plural else "great-grandparent"
        elif generation_number >= 3:
            multiplier = generation_number - 1
            base = f"{multiplier}x great-grandparents" if plural else f"{multiplier}x great-grandparent"
            return base
        else:
            return "great-grandparents" if plural else "great-grandparent"
    
    def get_person_being_described(self, applicant_generation, lang_code='EN'):
        """
        Get the text for the person being described in the main section.
        
        For G4 applicant (pages 3-4), this is the person from the PREVIOUS generation
        that we're asking questions about.
        
        Args:
            applicant_generation (int): G3, G4, G5, etc.
            lang_code (str): 'EN' or 'FR'
            
        Returns:
            str: Text for the person being described (e.g., "Grand-parent", "Great Grandparent")
        """
        # The person being described is from the generation that was documented
        # in the PREVIOUS applicant's document
        person_generation = applicant_generation - 2
        
        if lang_code == 'FR':
            return self.get_french_generation_text(person_generation, plural=False)
        else:
            return self._english_title_case(self.get_english_generation_text(person_generation, plural=False))
    
    def get_generation_being_documented(self, applicant_generation, lang_code='EN'):
        """
        Get the text for the generation being documented in this applicant's form.
        
        For G4 applicant (pages 3-4), this is the generation we're collecting info about.
        
        Args:
            applicant_generation (int): G3, G4, G5, etc.
            lang_code (str): 'EN' or 'FR'
            
        Returns:
            str: Text for the generation being documented
        """
        # The generation being documented is always applicant_generation - 1
        documented_generation = applicant_generation - 1
        
        if lang_code == 'FR':
            return self.get_french_generation_text(documented_generation, plural=False)
        else:
            return self._english_title_case(self.get_english_generation_text(documented_generation, plural=False))
    
    def get_next_generation_text(self, applicant_generation, lang_code='EN'):
        """
        Get the text for the next generation (used in radio button text).
        
        Args:
            applicant_generation (int): G3, G4, G5, etc.
            lang_code (str): 'EN' or 'FR'
            
        Returns:
            str: Text for the next generation (plural form)
        """
        documented_generation = applicant_generation - 1
        
        if lang_code == 'FR':
            return self.get_french_generation_text(documented_generation, plural=True)
        else:
            return self.get_english_generation_text(documented_generation, plural=True)
    
    def get_next_generation_singular_text(self, applicant_generation, lang_code='EN'):
        """
        Get the singular text for the next generation (used when referring to one specific person).
        
        For individual grandparent labels like "Grand-parent 1 (vos arrière-grand-parent)" 
        instead of "Grand-parent 1 (vos arrière-grands-parents)".
        
        Args:
            applicant_generation (int): G3, G4, G5, etc.
            lang_code (str): 'EN' or 'FR'
            
        Returns:
            str: Text for the next generation (singular form)
        """
        documented_generation = applicant_generation - 1
        
        if lang_code == 'FR':
            return self.get_french_generation_text(documented_generation, plural=False)
        else:
            return self.get_english_generation_text(documented_generation, plural=False)
    
    def get_page_header_text(self, applicant_generation, lang_code='EN'):
        """
        Get the header text for this applicant's pages.
        
        Args:
            applicant_generation (int): G3, G4, G5, etc.
            lang_code (str): 'EN' or 'FR'
            
        Returns:
            str: Header text for the page
        """
        documented_generation = applicant_generation - 1
        
        if lang_code == 'FR':
            lang = self.lang_config['FR']
            if documented_generation == 2:
                return lang['headers']['main_section_title']
            else:
                generation_text = self.get_french_generation_text(documented_generation, plural=True)
                return lang['headers']['generation_section_title'].format(multiplier=generation_text)
        else:
            lang = self.lang_config['EN']
            if documented_generation == 2:
                return lang['headers']['main_section_title']
            else:
                multiplier = f"{documented_generation - 1}x"
                return lang['headers']['generation_section_title'].format(multiplier=multiplier)
    
    def get_parent_section_text(self, applicant_generation, lang_code='EN'):
        """
        Get the text for Parent A/B sections - these are the PARENTS of the person being described.
        
        For G4 applicant, the main section asks about "arrière-grand-parent", so the Parent A/B 
        sections ask about parents of that same "arrière-grand-parent".
        
        Args:
            applicant_generation (int): G3, G4, G5, etc.
            lang_code (str): 'EN' or 'FR'
            
        Returns:
            str: Text for the parent section (same as person being described)
        """
        # Parent A/B sections ask about parents of the SAME person being described
        # So they use the same generation text as person_being_described
        return self.get_person_being_described(applicant_generation, lang_code)