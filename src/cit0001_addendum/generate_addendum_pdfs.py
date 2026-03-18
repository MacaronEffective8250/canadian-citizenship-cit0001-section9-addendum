#!/usr/bin/env python3

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import json
import os
from .generation_mapper import GenerationMapper

# Language Configuration Loading
def load_language_config(script_dir=None):
    """Load language configuration from JSON file."""
    if script_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "language_config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading language config: {e}")
        return None

def get_french_generation_text(applicant_generation):
    """Map applicant generation to correct French grandparent terminology.
    
    Based on Canadian French convention with intentional off-by-one mapping:
    Generation 1: Grands-parents
    Generation 2: Arrière-grands-parents  
    Generation 3: Grands-parents de 3e génération (= English 2× great-grandparents)
    Generation 4: Grands-parents de 4e génération (= English 3× great-grandparents)
    
    G3 applicant documents generation 2 → "arrière-grands-parents"
    G4 applicant documents generation 3 → "grands-parents de 3e génération"  
    G5 applicant documents generation 4 → "grands-parents de 4e génération"
    
    Note: "1e génération" and "2e génération" are INVALID in Canadian French.
    """
    generation_being_documented = applicant_generation - 1
    
    if generation_being_documented == 2:
        return "arrière-grands-parents"
    elif generation_being_documented >= 3:
        return f"grands-parents de {generation_being_documented}e génération"
    else:
        return "arrière-grands-parents"  # fallback

# Layout Configuration Constants
RADIO_BUTTON_CONFIG = {
    'button_width_percent': 0.05,
    'no_text_width_percent': 0.75,
    'yes_text_width_percent': 0.15,
    'shift_right_points': 24,
    'text_margin_points': 14  # Increased from 10 to 14 for better spacing
}

# Font Configuration Constants - Global to prevent re-registration
HEADER_FONT = "Helvetica-Bold"
HEADER_FONT_SIZE = 12
SECTION_FONT = "Helvetica-Bold"
SUBSECTION_FONT = "Helvetica-Bold"
BODY_FONT = "Helvetica"
BODY_FONT_SIZE = 10
LABEL_FONT = "Helvetica"
LABEL_FONT_SIZE = 8

# Document Formatting Constants
BORDER_STYLE = 'solid'
BORDER_WIDTH = 0.5
FILL_COLOR = colors.white
TEXT_COLOR = colors.black
CHECKBOX_SIZE = 16

FORM_FIELD_SCHEMA = {
    'linear_fields': [
        'Surname/Last name',
        'Given name(s)', 
        'Other names used'
    ],
    'grid_fields': [
        ['Country or territory of birth', 'Date of birth (YYYY-MM-DD)'],
        ['Canadian birth certificate number\n(if applicable/known)', 'Canadian citizenship certificate\nnumber (if applicable/known)']
    ]
}




def draw_wrapped_radio_text(c, text, x, y, max_width, font, font_size):
    """Draw word-wrapped text for radio button labels"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, font, font_size) <= max_width - RADIO_BUTTON_CONFIG['text_margin_points']:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped text lines
    for i, line in enumerate(lines):
        c.drawString(x, y - (i * 12), line)

def calculate_wrapped_line_count(c, text, max_width, font, font_size):
    """Calculate line count for wrapped text without drawing"""
    # Replace \n with spaces and let word wrapping handle line breaks
    text = text.replace('\\n', ' ')
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, font, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:  # Only append if we have something
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return len(lines)

def draw_wrapped_grid_label(c, text, x, y, max_width, font, font_size):
    """Draw text with word wrapping for grid field labels, returns line count"""
    # Replace \n with spaces and let word wrapping handle line breaks
    text = text.replace('\\n', ' ')
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, font, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:  # Only append if we have something
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped lines
    c.setFont(font, font_size)
    for i, line in enumerate(lines):
        c.drawString(x, y - (i * 10), line)
    
    return len(lines)

def create_form_textfield(c, name, tooltip, x, y, width, height, value="", font_style='solid', multiline=False):
    """Create standardized text field with proper alignment and multiline support"""
    # Determine if this is a multiline field based on height or field name
    is_multiline = multiline or height > 20 or 'other_names' in name.lower() or 'citizenship_details' in name.lower()
    
    if is_multiline:
        # Use multiline text field for larger fields with top-left alignment
        c.acroForm.textfield(
            name=name,
            tooltip=tooltip,
            x=x, y=y,
            borderStyle=font_style,
            borderWidth=BORDER_WIDTH,
            fillColor=FILL_COLOR,
            width=width, 
            height=height,
            fontName=BODY_FONT,
            fontSize=LABEL_FONT_SIZE,
            fieldFlags='multiline',
            maxlen=1000,  # Allow plenty of characters
            forceBorder=True,
            textColor=TEXT_COLOR,
            value=value
        )
    else:
        # Standard single-line text field
        c.acroForm.textfield(
            name=name,
            tooltip=tooltip,
            x=x, y=y,
            borderStyle=font_style,
            borderWidth=BORDER_WIDTH,
            fillColor=FILL_COLOR,
            width=width, 
            height=height,
            fontName=BODY_FONT,
            fontSize=LABEL_FONT_SIZE,
            textColor=TEXT_COLOR,
            forceBorder=True,
            value=value
        )

def create_radio_button_pair(c, name_base, tooltip_no, tooltip_yes, positions, y_pos, size, no_text, yes_text, font, font_size):
    """Create a pair of radio buttons with text labels"""
    # Common radio button properties
    button_y = y_pos - 5
    button_style = 'circle'
    border_style = BORDER_STYLE
    border_width = BORDER_WIDTH
    fill_color = FILL_COLOR
    selected = False
    
    # No radio button
    c.acroForm.radio(
        name=name_base,
        tooltip=tooltip_no,
        value='no',
        x=positions['no_button_col'], 
        y=button_y,
        buttonStyle=button_style,
        borderStyle=border_style,
        borderWidth=border_width,
        fillColor=fill_color,
        size=size,
        selected=selected
    )
    
    # Yes radio button  
    c.acroForm.radio(
        name=name_base,
        tooltip=tooltip_yes,
        value='yes',
        x=positions['yes_button_col'],
        y=button_y,
        buttonStyle=button_style,
        borderStyle=border_style,
        borderWidth=border_width,
        fillColor=fill_color,
        size=size,
        selected=selected
    )
    
    # Draw text labels with wrapping
    draw_wrapped_radio_text(c, no_text, positions['no_text_col'], y_pos, positions['col_75_percent'], font, font_size)
    c.drawString(positions['yes_text_col'], y_pos, yes_text)

def calculate_radio_button_positions(answer_x, answer_width):
    """Calculate standardized radio button positions for consistent layout"""
    radio_shift = RADIO_BUTTON_CONFIG['shift_right_points']  # 24 points
    col_5_percent = answer_width * 0.05   # 5% column width for radio buttons
    col_75_percent = answer_width * 0.75 - radio_shift  # 75% column width for "No" text (reduced by shift)
    
    positions = {
        'no_button_col': answer_x + radio_shift,  # Column 1: No button (5%) - shifted right
        'no_text_col': answer_x + radio_shift + col_5_percent + 4,  # Column 2: No text with spacing
        'yes_button_col': answer_x + radio_shift + col_5_percent + col_75_percent,  # Column 3: Yes button (5%)
        'yes_text_col': answer_x + radio_shift + col_5_percent + col_75_percent + col_5_percent + 12,  # Column 4: Yes text (15%) + 2 chars spacing
        'col_75_percent': col_75_percent
    }
    return positions

def set_font_optimized(c, font_name, font_size, current_font_state=None):
    """Set font only if different from current to reduce PDF font repetition"""
    new_font_state = (font_name, font_size)
    if current_font_state != new_font_state:
        c.setFont(font_name, font_size)
        return new_font_state
    return current_font_state

def create_editable_section9(output_path=None, num_generations=4, language='EN', lang_config=None):
    """Create an editable PDF form for Section 9 with proper form fields
    
    Args:
        output_path (str, optional): Output path for generated PDF. Defaults to script directory.
        num_generations (int): Number of generations to document
        language (str): Language code ('EN' or 'FR')
        lang_config (dict): Language configuration dictionary
    """
    
    # Get language strings
    if not lang_config:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lang_config = load_language_config(script_dir)
        if not lang_config:
            raise Exception("Could not load language configuration")
    
    lang = lang_config[language]
    
    
    # Use provided output path or default to script directory
    if output_path:
        filename = output_path
    else:
        # Get project root directory (two levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        documents_dir = os.path.join(project_root, "documents")
        os.makedirs(documents_dir, exist_ok=True)
        filename = os.path.join(documents_dir, "CIT0001_Section9_Grandparent_Addendum.pdf")
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Set PDF document metadata using language configuration
    c.setTitle(lang['metadata']['title'])
    c.setAuthor(lang['metadata']['author'])
    c.setSubject(lang['metadata']['subject'])
    c.setCreator(lang['metadata']['creator'])
    c.setProducer(lang['metadata']['producer'])
    c.setKeywords(lang['metadata']['keywords'])
    
    # Track current font to reduce redundant setFont calls
    current_font = None
    
    # Use global font and formatting constants
    
    # Spacing constants
    LINE_HEIGHT = 14
    LABEL_TO_BOX_GAP = 4
    BOX_TO_NEXT_LABEL_GAP = 10
    
    # Define proper margins for 8.5x11 paper printing
    # Reduced side margins: 0.5" (36 points) for more content space
    left_margin = 36      # 0.5 inches from left edge
    right_margin = width - 36   # 0.5 inches from right edge  
    top_margin = height - 54    # 0.75 inches from top (keep for header)
    bottom_margin = 54          # 0.75 inches from bottom (keep for safety)
    content_width = right_margin - left_margin
    line_height = LINE_HEIGHT
    checkbox_size = CHECKBOX_SIZE
    
    # Generation configurations - easily extensible
    # Generate dynamic generations configuration
    def generate_generations_config(max_generations=4, lang=None):
        """Generate configuration for any number of generations dynamically"""
        generations = []
        
        # First generation (special case)
        # Translate terms to French if needed
        if lang and lang.get('metadata', {}).get('title', '').startswith('CIT 0001 Section 9 - Addendum'):
            title = 'Arrière-grands-parents'
            person_described = 'Grand-parent'
            generation_documented = 'Arrière-grand-parent'
            next_gen = 'arrière-grands-parents'
        else:
            title = 'Great Grandparents'
            person_described = 'Grandparent'
            generation_documented = 'Great Grandparent'
            next_gen = 'great-grandparents'
            
        generations.append({
            'title': title,
            'person_being_described': person_described,
            'generation_being_documented': generation_documented,
            'field_prefix': 'gp',
            'next_generation': next_gen,
            'header_subtitle': lang['headers']['main_section_title'] if lang else 'Tell us about your great-grandparents',
            'applicant_generation': 3  # G3 applicant documents great-grandparents
        })
        
        # Generate subsequent generations dynamically
        for i in range(2, max_generations + 1):
            multiplier = f"{i}x" if i > 1 else ""
            prev_multiplier = f"{i-1}x" if i > 2 else ""
            next_multiplier = f"{i+1}x" if i < max_generations else f"{i+1}x"
            
            # Person being described (previous generation) - translate to French if needed
            if lang and lang.get('metadata', {}).get('title', '').startswith('CIT 0001 Section 9 - Addendum'):
                # For French, the person being described should be the previous generation
                applicant_gen = i + 1
                previous_gen_applicant = applicant_gen - 1
                generation_being_described = previous_gen_applicant - 1
                if generation_being_described == 1:
                    person_described = 'Grand-parent'  # Generation 1 = grand-parent
                elif generation_being_described == 2:
                    person_described = 'Arrière-grand-parent'  # Generation 2 = arrière-grand-parent
                else:
                    # Generation 3+ = grands-parents de Xe génération
                    person_described = f'Grand-parent de {generation_being_described}e génération'
                
                # For generation being documented, use French generation text
                generation_documented = get_french_generation_text(applicant_gen).replace('grands-parents', 'grand-parent')
                next_gen = get_french_generation_text(applicant_gen)
            else:
                # English terms
                if i == 2:
                    person_described = 'Great Grandparent'
                else:
                    person_described = f'{prev_multiplier} Great Grandparent'
                generation_documented = f'{multiplier} Great Grandparent'
                next_gen = f'{multiplier} great-grandparents'
            
            # Use language-specific generation section title
            if lang:
                # For empty multiplier, use main section title, otherwise use generation section title
                if not multiplier:
                    header_subtitle = lang['headers']['main_section_title']
                else:
                    # Use French generation format for French language, English multipliers for English
                    if lang == lang_config.get('FR', {}):  # Check if this is French language config
                        # Calculate applicant generation: G4 for i=2, G5 for i=3, etc.
                        applicant_gen = i + 2
                        french_generation = get_french_generation_text(applicant_gen)
                        header_subtitle = lang['headers']['generation_section_title'].format(multiplier=french_generation)
                    else:
                        header_subtitle = lang['headers']['generation_section_title'].format(multiplier=f'{multiplier.lower()}')
            else:
                header_subtitle = f'Tell us about your {multiplier.lower()} great-grandparents'
            
            # Set title based on language
            if lang and lang.get('metadata', {}).get('title', '').startswith('CIT 0001 Section 9 - Addendum'):
                title = next_gen  # Use the French generation text
            else:
                title = f'{multiplier} Great Grandparents'
                
            generations.append({
                'title': title,
                'person_being_described': person_described,
                'generation_being_documented': generation_documented,
                'field_prefix': f'{multiplier.lower()}_great_grandparents',
                'next_generation': next_gen,
                'header_subtitle': header_subtitle,
                'applicant_generation': i + 2  # G4 applicant (i=2) documents 2x great-grandparents, etc.
            })
        
        return generations
    
    GENERATIONS_CONFIG = generate_generations_config(num_generations, lang)  # Generate specified number of generations
    
    # Calculate total pages dynamically
    total_pages = len(GENERATIONS_CONFIG) * 2  # 2 pages each for all generations
    
    page_number = 1
    
    def add_header(page_num, total_pages=total_pages):
        """Add header with form reference and page number"""
        nonlocal current_font
        current_font = set_font_optimized(c, BODY_FONT, BODY_FONT_SIZE, current_font)
        header_text = lang['headers']['main_header'].format(page_num=page_num, total_pages=total_pages)
        c.drawString(left_margin, top_margin, header_text)
        return top_margin - 30  # Return starting y position for content
    
    y_pos = add_header(page_number)
    
    # Header section (matching original style)
    current_font = set_font_optimized(c, HEADER_FONT, HEADER_FONT_SIZE, current_font)
    c.drawString(left_margin, y_pos, lang['headers']['main_section_title'])
    y_pos -= 20
    
    # Wrap the instruction text properly
    current_font = set_font_optimized(c, BODY_FONT, BODY_FONT_SIZE, current_font)
    instruction_text = lang['headers']['instructions']
    
    # Break the instruction text into multiple lines
    max_width = right_margin - left_margin
    words = instruction_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for line in lines:
        c.drawString(left_margin, y_pos, line)
        y_pos -= 10
    
    y_pos -= 15
    
    # Grandparent 1 section header - use label font size for consistency
    current_font = set_font_optimized(c, SECTION_FONT, LABEL_FONT_SIZE, current_font)
    c.drawString(left_margin, y_pos, lang['person_labels']['grandparent_1'])
    y_pos -= 12
    
    # Text field for Grandparent 1 name
    create_form_textfield(c, 'grandparent1_name',
                        lang['person_labels']['grandparent_1'],
                        left_margin, y_pos-15, 400, 15)
    y_pos -= 25
    
    # Question text - use label font size for consistency
    current_font = set_font_optimized(c, BODY_FONT, LABEL_FONT_SIZE, current_font)
    question_text = lang['questions']['main_question_gp1']
    
    # Wrap text manually
    words = question_text.split()
    lines = []
    current_line = ""
    max_width = right_margin - left_margin - 20
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for line in lines:
        c.drawString(left_margin, y_pos, line)
        y_pos -= line_height
    
    y_pos -= 10
    
    # Create 2x2 grid for questions and answers - left 1/2 for text, right 1/2 for answers
    question_width = content_width // 2  # Left 1/2 for questions
    answer_width = content_width // 2  # Right 1/2 for answers
    question_x = left_margin
    answer_x = left_margin + question_width + 10  # Small gap between sections
    
    # First question in grid - use full question width for wrapping
    q1_y = y_pos
    question1_text = lang['radio_buttons']['birth_outside_canada_gp1']
    
    # Wrap text to fit the full question width
    words = question1_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= question_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped lines
    for i, line in enumerate(lines):
        c.drawString(question_x, q1_y - (i * 12), line)
    
    # Radio buttons for first question using reusable function
    positions = calculate_radio_button_positions(answer_x, answer_width)
    create_radio_button_pair(c, 'grandparent1_born_outside',
                           lang['radio_buttons']['no_skip_to_gp2'], lang['radio_buttons']['yes'],
                           positions, q1_y, checkbox_size,
                           lang['radio_buttons']['no_skip_to_gp2'], lang['radio_buttons']['yes'],
                           BODY_FONT, BODY_FONT_SIZE)
    
    # Second question in grid - use full question width for wrapping
    q2_y = q1_y - 30  # Space for second question
    question2_text = lang['radio_buttons']['parents_canadian_gp1']
    
    # Wrap text to fit the full question width
    words = question2_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= question_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped lines
    for i, line in enumerate(lines):
        c.drawString(question_x, q2_y - (i * 12), line)
    
    # Radio buttons for second question using reusable function
    create_radio_button_pair(c, 'grandparent1_parents_canadian',
                           lang['radio_buttons']['no_skip_to_gp2'], lang['radio_buttons']['yes'],
                           positions, q2_y, checkbox_size,
                           lang['radio_buttons']['no_skip_to_gp2'], lang['radio_buttons']['yes'],
                           BODY_FONT, BODY_FONT_SIZE)
    
    y_pos = q2_y - 30  # Position after both questions
    y_pos -= 5
    
    # Add notes section for Grandparent 1
    c.setFont(LABEL_FONT, LABEL_FONT_SIZE)
    c.drawString(left_margin, y_pos, lang['notes']['notes_gp1'])
    y_pos -= 4
    
    create_form_textfield(c, 'grandparent1_notes',
                        lang['notes']['notes_gp1'],
                        left_margin, y_pos-40, content_width, 40)
    y_pos -= 55
    
    c.setFont(BODY_FONT, BODY_FONT_SIZE)
    c.drawString(left_margin, y_pos, lang['details']['detail_request'])
    y_pos -= 5
    
    # Add horizontal line within safe print area
    c.line(left_margin, y_pos, right_margin, y_pos)
    y_pos -= 10
    
    # Two-column layout for Parent A and Parent B
    # Calculate column widths with proper gap for vertical line
    column_gap = 30  # Space for vertical line plus padding
    col_width = (content_width - column_gap) // 2  # Equal columns
    col1_x = left_margin
    col2_x = left_margin + col_width + column_gap
    
    # Center the vertical line between columns
    column_divider_x = left_margin + col_width + (column_gap // 2)
    
    # Headers for both columns - use label font size for consistency
    c.setFont(SUBSECTION_FONT, LABEL_FONT_SIZE)
    c.drawString(col1_x, y_pos, lang['parent_headers']['parent_a_gp1'])
    c.drawString(col2_x, y_pos, lang['parent_headers']['parent_b_gp1'])
    
    # Mark section start for vertical line (divider_x already calculated)
    section_start_y = y_pos + 5
    y_pos -= 20
    
    # Define fields in order for linear layout
    # Build complete linear fields array from language configuration (without citizenship details - that's handled separately)
    linear_fields = lang['form_fields']['linear_fields']
    
    # Build grid fields from language configuration (maintaining pair structure)
    grid_fields = [
        [lang['form_fields']['grid_fields'][0], lang['form_fields']['grid_fields'][1]],
        [lang['form_fields']['grid_fields'][2], lang['form_fields']['grid_fields'][3]]
    ]
    
    # Create fields in parallel columns
    c.setFont(LABEL_FONT, LABEL_FONT_SIZE)
    start_y = y_pos
    
    # Create linear fields with consistent spacing system
    current_y = start_y
    label_to_box_gap = LABEL_TO_BOX_GAP      # Consistent gap between label and text box
    box_to_next_label_gap = BOX_TO_NEXT_LABEL_GAP  # Consistent gap between text box and next label
    
    for i, label in enumerate(linear_fields):
        # Determine box height based on field type
        if "Other names used" in label:
            box_height = 40     # Optimized box for 3-4 lines
        else:
            box_height = 16     # Standard box height
        
        # Calculate positions consistently
        label_y = current_y
        text_y = label_y - label_to_box_gap - box_height  # Position text box below label
        next_y = text_y - box_to_next_label_gap          # Next field starts below this box
        
        # Column 1 - Parent A
        c.drawString(col1_x, label_y, label)
        field_name = label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        create_form_textfield(c, f'gp1_parentA_{field_name}',
                            f'{lang["parent_headers"]["parent_a_gp1"]}: {label}',
                            col1_x, text_y, col_width, box_height)
        
        # Column 2 - Parent B of Grandparent 1
        c.drawString(col2_x, label_y, label)
        create_form_textfield(c, f'gp1_parentB_{field_name}',
                            f'{lang["parent_headers"]["parent_b_gp1"]}: {label}',
                            col2_x, text_y, col_width, box_height)
        
        # Move to next field position
        current_y = next_y
    
    # Position grid section with buffer space
    grid_start_y = current_y - 15  # Optimized buffer space before grid
    
    # Create 2x2 grid fields within each column (like original PDF)
    grid_field_width = (col_width - 10) // 2  # Half width minus smaller gap for better French text fit
    grid_field_height = 16
    grid_spacing_y = 36  # Vertical spacing for grid labels with proper clearance
    
    c.setFont(LABEL_FONT, LABEL_FONT_SIZE)  # Use normal font size for grid
    
    for row_idx, row in enumerate(grid_fields):
        grid_row_y = grid_start_y - (row_idx * grid_spacing_y)
        
        # First pass: calculate line counts for the entire row without drawing
        row_line_counts = []
        for col_idx, label in enumerate(row):
            # Calculate line counts for both columns to determine max
            line_count_a = calculate_wrapped_line_count(c, label, grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            line_count_b = calculate_wrapped_line_count(c, label, grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            
            # Store the maximum line count for this field
            row_line_counts.append(max(line_count_a, line_count_b))
        
        # Calculate the maximum line count for the entire row
        max_row_line_count = max(row_line_counts)
        text_field_y = grid_row_y - (max_row_line_count * 10) - 10
        
        # Second pass: draw labels and create text fields
        for col_idx, label in enumerate(row):
            grid_x_offset = col_idx * (grid_field_width + 15)
            
            # Draw labels only once for each position
            draw_wrapped_grid_label(c, label, col1_x + grid_x_offset, grid_row_y, 
                                   grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            draw_wrapped_grid_label(c, label, col2_x + grid_x_offset, grid_row_y, 
                                   grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            
            create_form_textfield(c, f'gp1_parentA_{label.replace(chr(10), "").lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                 f'{lang["parent_headers"]["parent_a_gp1"]}: {label.replace(chr(10), " ")}',
                                 col1_x + grid_x_offset, text_field_y, grid_field_width, grid_field_height)
            
            create_form_textfield(c, f'gp1_parentB_{label.replace(chr(10), "").lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                 f'{lang["parent_headers"]["parent_b_gp1"]}: {label.replace(chr(10), " ")}',
                                 col2_x + grid_x_offset, text_field_y, grid_field_width, grid_field_height)
    
    y_pos = grid_start_y - (len(grid_fields) * grid_spacing_y) - 15  # Adjusted for grid spacing
    
    # Details sections in two columns with text wrapping for French
    # Handle generation ordinal for French vs English
    if language == 'FR':
        # Use French template with singular form for individual grandparents
        citizenship_text = lang['form_fields']['citizenship_details'].format(generation_type='arrière-grand-parent')
    else:
        citizenship_text = lang['form_fields']['citizenship_details'].format(generation_type='great-grandparent')
    line_count_1 = draw_wrapped_grid_label(c, citizenship_text, col1_x, y_pos, col_width, LABEL_FONT, LABEL_FONT_SIZE)
    line_count_2 = draw_wrapped_grid_label(c, citizenship_text, col2_x, y_pos, col_width, LABEL_FONT, LABEL_FONT_SIZE)
    
    # Use the maximum line count for consistent spacing
    max_lines = max(line_count_1, line_count_2)
    y_pos -= (max_lines * 10) + 4  # Space for wrapped text plus minimal gap
    
    create_form_textfield(c, 'gp1_parentA_citizenship_details',
                        'Details on how Parent A of Grandparent 1 obtained citizenship',
                        col1_x, y_pos-40, col_width, 40)
    
    create_form_textfield(c, 'gp1_parentB_citizenship_details',
                        'Details on how Parent B of Grandparent 1 obtained citizenship',
                        col2_x, y_pos-40, col_width, 40)
    
    y_pos -= 50  # Space after optimized text area
    
    # Date of death in two columns
    c.drawString(col1_x, y_pos, lang['form_fields']['date_of_death'])
    c.drawString(col2_x, y_pos, lang['form_fields']['date_of_death'])
    y_pos -= 4  # Minimal space between label and box
    
    create_form_textfield(c, 'gp1_parentA_date_death',
                        'Parent A of Grandparent 1 date of death',
                        col1_x, y_pos-16, 150, 16)
    
    create_form_textfield(c, 'gp1_parentB_date_death',
                        'Parent B of Grandparent 1 date of death',
                        col2_x, y_pos-16, 150, 16)
    
    y_pos -= 30
    
    # Draw vertical line between Parent A and Parent B columns for Grandparent 1 section
    section_end_y = y_pos
    c.line(column_divider_x, section_start_y, column_divider_x, section_end_y)
    
    # Check if we're getting too close to bottom margin
    if section_end_y < bottom_margin + 5:  # 5 points buffer above bottom margin
        print(f"Warning: Content may be too close to bottom margin on page 1. End position: {section_end_y}")
    
    # New page for Grandparent 2
    c.showPage()
    page_number += 1
    y_pos = add_header(page_number)
    
    # Grandparent 2 section - use label font size for consistency
    c.setFont(SECTION_FONT, LABEL_FONT_SIZE)
    c.drawString(left_margin, y_pos, lang['person_labels']['grandparent_2'])
    y_pos -= 12
    
    # Text field for Grandparent 2 name
    create_form_textfield(c, 'grandparent2_name',
                        lang['person_labels']['grandparent_2'],
                        left_margin, y_pos-15, 400, 15)
    y_pos -= 25
    
    # Repeat similar structure for Grandparent 2 - use label font size
    c.setFont(BODY_FONT, LABEL_FONT_SIZE)
    question_text = lang['questions']['main_question_gp2']
    
    # Wrap text manually again
    words = question_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for line in lines:
        c.drawString(left_margin, y_pos, line)
        y_pos -= line_height
    
    y_pos -= 10
    
    # Create 2x2 grid for Grandparent 2 questions and answers - left 1/2 for text, right 1/2 for answers
    question_width = content_width // 2  # Left 1/2 for questions
    answer_width = content_width // 2  # Right 1/2 for answers
    question_x = left_margin
    answer_x = left_margin + question_width + 10  # Small gap between sections
    
    # First question for Grandparent 2 - use full question width for wrapping
    q1_y = y_pos
    question1_text = lang['radio_buttons']['birth_outside_canada_gp2']
    
    # Wrap text to fit the full question width
    words = question1_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= question_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped lines
    for i, line in enumerate(lines):
        c.drawString(question_x, q1_y - (i * 12), line)
    
    # Radio buttons for first question using reusable function
    positions = calculate_radio_button_positions(answer_x, answer_width)
    
    # Determine appropriate skip text for Grandparent 2
    if page_number == total_pages:
        no_text = lang['radio_buttons']['no_skip_to_end']
    else:
        no_text = lang['radio_buttons']['no_skip_to_next_page']
    
    create_radio_button_pair(c, 'grandparent2_born_outside',
                           no_text, lang['radio_buttons']['yes'],
                           positions, q1_y, checkbox_size,
                           no_text, lang['radio_buttons']['yes'],
                           BODY_FONT, BODY_FONT_SIZE)
    
    # Second question for Grandparent 2 - use full question width for wrapping
    q2_y = q1_y - 30  # Space for second question
    question2_text = lang['radio_buttons']['parents_canadian_gp2']
    
    # Wrap text to fit the full question width
    words = question2_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= question_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped lines
    for i, line in enumerate(lines):
        c.drawString(question_x, q2_y - (i * 12), line)
    
    # Radio buttons for second question using reusable function
    create_radio_button_pair(c, 'grandparent2_parents_canadian',
                           no_text, lang['radio_buttons']['yes'],
                           positions, q2_y, checkbox_size,
                           no_text, lang['radio_buttons']['yes'],
                           BODY_FONT, BODY_FONT_SIZE)
    
    y_pos = q2_y - 30  # Position after both questions
    y_pos -= 5
    
    # Add notes section for Grandparent 2
    c.setFont(LABEL_FONT, LABEL_FONT_SIZE)
    c.drawString(left_margin, y_pos, lang['notes']['notes_gp2'])
    y_pos -= 4
    
    create_form_textfield(c, 'grandparent2_notes',
                        lang['notes']['notes_gp2'],
                        left_margin, y_pos-40, content_width, 40)
    y_pos -= 55
    
    c.setFont(BODY_FONT, BODY_FONT_SIZE)
    c.drawString(left_margin, y_pos, lang['details']['detail_request'])
    y_pos -= 5
    
    # Add horizontal line within safe print area
    c.line(left_margin, y_pos, right_margin, y_pos)
    y_pos -= 10
    
    # Two-column layout for Parent A and Parent B of Grandparent 2
    # Headers for both columns - use label font size for consistency
    c.setFont(SUBSECTION_FONT, LABEL_FONT_SIZE)
    c.drawString(col1_x, y_pos, lang['parent_headers']['parent_a_gp2'])
    c.drawString(col2_x, y_pos, lang['parent_headers']['parent_b_gp2'])
    
    # Mark section start for vertical line
    section2_start_y = y_pos + 5
    y_pos -= 25
    
    # Create fields in parallel columns for Parent B
    c.setFont(LABEL_FONT, LABEL_FONT_SIZE)
    start_y_b = y_pos
    
    # Create linear fields for Grandparent 2 with same consistent spacing system
    current_y_b = start_y_b
    
    for i, label in enumerate(linear_fields):
        # Determine box height based on field type
        if "Other names used" in label:
            box_height = 40     # Optimized box for 3-4 lines
        else:
            box_height = 16     # Standard box height
        
        # Calculate positions consistently (same as Grandparent 1)
        label_y_b = current_y_b
        text_y_b = label_y_b - label_to_box_gap - box_height  # Position text box below label
        next_y_b = text_y_b - box_to_next_label_gap          # Next field starts below this box
        
        # Column 1 - Parent A of Grandparent 2
        c.drawString(col1_x, label_y_b, label)
        create_form_textfield(c, f'gp2_parentA_{label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                             f'{lang["parent_headers"]["parent_a_gp2"]}: {label}',
                             col1_x, text_y_b, col_width, box_height)
        
        # Column 2 - Parent B of Grandparent 2
        c.drawString(col2_x, label_y_b, label)
        create_form_textfield(c, f'gp2_parentB_{label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                             f'{lang["parent_headers"]["parent_b_gp2"]}: {label}',
                             col2_x, text_y_b, col_width, box_height)
        
        # Move to next field position
        current_y_b = next_y_b
    
    # Position grid section with buffer space
    grid_start_y_b = current_y_b - 15  # Optimized buffer space before grid
    
    # Create 2x2 grid fields within each column for Grandparent 2 (like original PDF)
    c.setFont(LABEL_FONT, LABEL_FONT_SIZE)  # Use normal font size for grid
    
    for row_idx, row in enumerate(grid_fields):
        grid_row_y_b = grid_start_y_b - (row_idx * grid_spacing_y)
        
        # First pass: calculate line counts for the entire row without drawing
        row_line_counts = []
        for col_idx, label in enumerate(row):
            # Calculate line counts for both columns to determine max
            line_count_a = calculate_wrapped_line_count(c, label, grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            line_count_b = calculate_wrapped_line_count(c, label, grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            
            # Store the maximum line count for this field
            row_line_counts.append(max(line_count_a, line_count_b))
        
        # Calculate the maximum line count for the entire row
        max_row_line_count = max(row_line_counts)
        text_field_y_b = grid_row_y_b - (max_row_line_count * 10) - 10
        
        # Second pass: draw labels and create text fields
        for col_idx, label in enumerate(row):
            grid_x_offset = col_idx * (grid_field_width + 15)
            
            # Draw labels only once for each position
            draw_wrapped_grid_label(c, label, col1_x + grid_x_offset, grid_row_y_b, 
                                   grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            draw_wrapped_grid_label(c, label, col2_x + grid_x_offset, grid_row_y_b, 
                                   grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
            
            create_form_textfield(c, f'gp2_parentA_{label.replace(chr(10), "").lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                 f'{lang["parent_headers"]["parent_a_gp2"]}: {label.replace(chr(10), " ")}',
                                 col1_x + grid_x_offset, text_field_y_b, grid_field_width, grid_field_height)
            
            create_form_textfield(c, f'gp2_parentB_{label.replace(chr(10), "").lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                 f'{lang["parent_headers"]["parent_b_gp2"]}: {label.replace(chr(10), " ")}',
                                 col2_x + grid_x_offset, text_field_y_b, grid_field_width, grid_field_height)
    
    y_pos = grid_start_y_b - (len(grid_fields) * grid_spacing_y) - 15  # Adjusted for grid spacing
    
    # Details sections in two columns for Grandparent 2 with text wrapping for French
    # Handle generation ordinal for French vs English
    if language == 'FR':
        # Use French template with singular form for individual grandparents
        citizenship_text = lang['form_fields']['citizenship_details'].format(generation_type='arrière-grand-parent')
    else:
        citizenship_text = lang['form_fields']['citizenship_details'].format(generation_type='great-grandparent')
    line_count_1 = draw_wrapped_grid_label(c, citizenship_text, col1_x, y_pos, col_width, LABEL_FONT, LABEL_FONT_SIZE)
    line_count_2 = draw_wrapped_grid_label(c, citizenship_text, col2_x, y_pos, col_width, LABEL_FONT, LABEL_FONT_SIZE)
    
    # Use the maximum line count for consistent spacing
    max_lines = max(line_count_1, line_count_2)
    y_pos -= (max_lines * 10) + 4  # Space for wrapped text plus minimal gap
    
    create_form_textfield(c, 'gp2_parentA_citizenship_details',
                        'Details on how Parent A of Grandparent 2 obtained citizenship',
                        col1_x, y_pos-40, col_width, 40)
    
    create_form_textfield(c, 'gp2_parentB_citizenship_details',
                        'Details on how Parent B of Grandparent 2 obtained citizenship',
                        col2_x, y_pos-40, col_width, 40)
    
    y_pos -= 50  # Optimized space after text area
    
    # Date of death in two columns for Grandparent 2
    c.drawString(col1_x, y_pos, lang['form_fields']['date_of_death'])
    c.drawString(col2_x, y_pos, lang['form_fields']['date_of_death'])
    y_pos -= 4  # Minimal space between label and box
    
    create_form_textfield(c, 'gp2_parentA_date_death',
                        'Parent A of Grandparent 2 date of death',
                        col1_x, y_pos-16, 150, 16)
    
    create_form_textfield(c, 'gp2_parentB_date_death',
                        'Parent B of Grandparent 2 date of death',
                        col2_x, y_pos-16, 150, 16)
    
    # Draw vertical line between Parent A and Parent B columns for Grandparent 2 section
    section2_end_y = y_pos - 20
    c.line(column_divider_x, section2_start_y, column_divider_x, section2_end_y)
    
    # Check if we're getting too close to bottom margin
    if section2_end_y < bottom_margin + 20:  # 20 points buffer above bottom margin
        print(f"Warning: Content may be too close to bottom margin on page 2. End position: {section2_end_y}")
    
    # Add end of addendum indicator if this is the last page (for G3 documents which have only 2 pages)
    if page_number == total_pages:  # Check if this is the final page of the document
        c.setFont(SECTION_FONT, LABEL_FONT_SIZE)
        end_text = lang['headers']['end_indicator']
        text_width = c.stringWidth(end_text, SECTION_FONT, LABEL_FONT_SIZE)
        center_x = left_margin + (content_width - text_width) / 2
        c.drawString(center_x, section2_end_y - 30, end_text)
    
    # Generate pages for all additional generations using config
    for gen_index, generation_config in enumerate(GENERATIONS_CONFIG[1:], 1):  # Skip first generation (already done)
        start_page = page_number + (gen_index * 2) - 1
        create_generation_pages(c, generation_config, start_page, left_margin, right_margin, top_margin, bottom_margin, content_width, col_width, col1_x, col2_x, column_divider_x, linear_fields, grid_fields, grid_spacing_y, LABEL_TO_BOX_GAP, BOX_TO_NEXT_LABEL_GAP, HEADER_FONT, HEADER_FONT_SIZE, SECTION_FONT, SUBSECTION_FONT, BODY_FONT, BODY_FONT_SIZE, LABEL_FONT, LABEL_FONT_SIZE, BORDER_STYLE, BORDER_WIDTH, FILL_COLOR, CHECKBOX_SIZE, total_pages, lang, lang_config)
    
    c.save()
    print(f"Editable PDF created: {filename} ({total_pages} pages total)")

def create_generation_pages(c, generation_config, start_page_num, left_margin, right_margin, top_margin, bottom_margin, content_width, col_width, col1_x, col2_x, column_divider_x, linear_fields, grid_fields, grid_spacing_y, LABEL_TO_BOX_GAP, BOX_TO_NEXT_LABEL_GAP, HEADER_FONT, HEADER_FONT_SIZE, SECTION_FONT, SUBSECTION_FONT, BODY_FONT, BODY_FONT_SIZE, LABEL_FONT, LABEL_FONT_SIZE, BORDER_STYLE, BORDER_WIDTH, FILL_COLOR, CHECKBOX_SIZE, total_pages, lang, lang_config):
    """Create pages for any generation using configuration"""
    
    # Get applicant generation and create mapper for dynamic generation text
    applicant_generation = generation_config['applicant_generation']
    lang_code = 'FR' if lang.get('metadata', {}).get('title', '').startswith('CIT 0001 Section 9 - Addendum') else 'EN'
    mapper = GenerationMapper(lang_config)
    
    # Get dynamic generation text using mapper (eliminates static configuration bugs)
    person_being_described = mapper.get_person_being_described(applicant_generation, lang_code)
    generation_being_documented = mapper.get_generation_being_documented(applicant_generation, lang_code)
    next_gen = mapper.get_next_generation_text(applicant_generation, lang_code)
    next_gen_singular = mapper.get_next_generation_singular_text(applicant_generation, lang_code)
    french_gen_title = mapper.get_page_header_text(applicant_generation, lang_code)
    parent_section_person = mapper.get_parent_section_text(applicant_generation, lang_code)
    
    # Extract multiplier for 2x, 3x, etc. generations if present (for backward compatibility)
    multiplier = None
    if "x" in french_gen_title:
        multiplier = french_gen_title.split("x")[0]
    
    def add_header_gen(page_num, gen_title, total_pages=total_pages):
        """Add header with form reference and page number - always use consistent base generation header"""
        c.setFont(BODY_FONT, BODY_FONT_SIZE)
        header_text = lang['headers']['main_header'].format(page_num=page_num, total_pages=total_pages)
        c.drawString(left_margin, top_margin, header_text)
        return top_margin - 30  # Return starting y position for content
    
    # Create two pages for this generation (same pattern as original)
    for grandparent_num in [1, 2]:
        # New page
        c.showPage()
        page_number = start_page_num + (grandparent_num - 1)
        y_pos = add_header_gen(page_number, french_gen_title)
        
        if grandparent_num == 1:
            # Header section on first page only
            c.setFont(HEADER_FONT, HEADER_FONT_SIZE)
            c.drawString(left_margin, y_pos, generation_config['header_subtitle'])
            y_pos -= 20
            
            # Instruction text
            c.setFont(BODY_FONT, BODY_FONT_SIZE)
            # Use generation-specific title from language config
            if multiplier:
                # Use French ordinals if this is French language, English multipliers if English
                if 'FR' in lang.get('metadata', {}).get('title', ''):  # Check if this is French
                    # Get the applicant generation from config and convert to French ordinal
                    applicant_gen = generation_config.get('applicant_generation', 4)
                    french_generation = get_french_generation_text(applicant_gen)
                    section_title = lang['headers']['generation_section_title'].format(multiplier=french_generation)
                else:
                    section_title = lang['headers']['generation_section_title'].format(multiplier=multiplier)
            else:
                section_title = lang['headers']['main_section_title']
            
            instruction_text = lang['headers']['instructions']
            
            # Break the instruction text into multiple lines
            max_width = right_margin - left_margin
            words = instruction_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                c.drawString(left_margin, y_pos, line)
                y_pos -= 12
            
            y_pos -= 18
        
        # Section header - use label font size for consistency
        c.setFont(SECTION_FONT, LABEL_FONT_SIZE)
        c.drawString(left_margin, y_pos, lang['person_labels']['generation_person'].format(
            person_being_described=person_being_described,
            grandparent_num=grandparent_num
        ))
        y_pos -= 12
        
        # Name field
        field_prefix = generation_config['field_prefix']
        create_form_textfield(c, f'{field_prefix}_{grandparent_num}_name',
                            lang['form_field_labels']['full_name_of'].format(
                                person_being_described=person_being_described,
                                grandparent_num=grandparent_num
                            ),
                            left_margin, y_pos-15, 400, 15)
        y_pos -= 25
        
        # Question text - use label font size for consistency
        c.setFont(BODY_FONT, LABEL_FONT_SIZE)
        question_text = lang['questions']['main_question_generation'].format(
            person_being_described=person_being_described,
            grandparent_num=grandparent_num,
            next_gen=next_gen_singular
        )
        
        # Wrap text manually
        words = question_text.split()
        lines = []
        current_line = ""
        max_width = right_margin - left_margin - 20
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            c.drawString(left_margin, y_pos, line)
            y_pos -= 14
        
        y_pos -= 10
        
        # Create 2x2 grid for questions and answers - left 1/2 for text, right 1/2 for answers
        question_width = content_width // 2  # Left 1/2 for questions
        answer_width = content_width // 2  # Right 1/2 for answers
        question_x = left_margin
        answer_x = left_margin + question_width + 10  # Small gap between sections
        
        checkbox_size = CHECKBOX_SIZE
        
        # Determine appropriate skip text based on position in document
        if grandparent_num == 1:
            # First grandparent - skip to second grandparent on same generation
            next_text = f"{person_being_described} 2"
        elif page_number == total_pages:
            # Last page of document - skip to end of addendum
            next_text = "end of addendum and continue the main application"
        else:
            # Middle pages - skip to next addendum page
            next_text = "next addendum page"
        
        # First question in grid - use full question width for wrapping
        q1_y = y_pos
        question1_text = lang['radio_buttons']['birth_outside_canada_generation'].format(
            person_being_described=person_being_described,
            grandparent_num=grandparent_num
        )
        
        # Wrap text to fit the full question width
        words = question1_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= question_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw wrapped lines
        for i, line in enumerate(lines):
            c.drawString(question_x, q1_y - (i * 12), line)
        
        # Radio buttons for first question using reusable function
        positions = calculate_radio_button_positions(answer_x, answer_width)
        no_text = lang['radio_buttons']['no_skip_to_next'].format(next_text=next_text)
        create_radio_button_pair(c, f'{field_prefix}_{grandparent_num}_born_outside',
                               f'No - skip to {next_text}', 'Yes',
                               positions, q1_y, checkbox_size,
                               no_text, lang['radio_buttons']['yes'],
                               BODY_FONT, BODY_FONT_SIZE)
        
        # Second question in grid - use full question width for wrapping
        q2_y = q1_y - 35  # More space for longer text
        question2_text = lang['radio_buttons']['parents_canadian_generation'].format(
            person_being_described=person_being_described,
            grandparent_num=grandparent_num,
            next_gen=next_gen_singular
        )
        
        # Wrap text to fit the full question width
        words = question2_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, BODY_FONT, BODY_FONT_SIZE) <= question_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw wrapped lines
        for i, line in enumerate(lines):
            c.drawString(question_x, q2_y - (i * 12), line)
        
        # Radio buttons for second question using reusable function
        no_text = lang['radio_buttons']['no_skip_to_next'].format(next_text=next_text)
        create_radio_button_pair(c, f'{field_prefix}_{grandparent_num}_parents_canadian',
                               f'No - skip to {next_text}', 'Yes',
                               positions, q2_y, checkbox_size,
                               no_text, lang['radio_buttons']['yes'],
                               BODY_FONT, BODY_FONT_SIZE)
        
        y_pos = q2_y - 35  # Position after both questions
        y_pos -= 5
        
        # Add notes section for this generation's grandparent
        c.setFont(LABEL_FONT, LABEL_FONT_SIZE)
        notes_label = lang['notes']['notes_generation'].format(
            person_being_described=person_being_described,
            grandparent_num=grandparent_num
        )
        c.drawString(left_margin, y_pos, notes_label)
        y_pos -= 4
        
        create_form_textfield(c, f'{field_prefix}_{grandparent_num}_notes',
                            notes_label,
                            left_margin, y_pos-40, content_width, 40)
        y_pos -= 55
        
        c.setFont(BODY_FONT, BODY_FONT_SIZE)
        c.drawString(left_margin, y_pos, lang['details']['detail_request'])
        y_pos -= 5
        
        # Horizontal line
        c.line(left_margin, y_pos, right_margin, y_pos)
        y_pos -= 10
        
        # Column headers - use label font size for consistency  
        # Use person_being_described to reference who the parents belong to
        c.setFont(SUBSECTION_FONT, LABEL_FONT_SIZE)
        c.drawString(col1_x, y_pos, lang['parent_headers']['parent_a_generation'].format(
            person_being_described=parent_section_person,
            grandparent_num=grandparent_num
        ))
        c.drawString(col2_x, y_pos, lang['parent_headers']['parent_b_generation'].format(
            person_being_described=parent_section_person,
            grandparent_num=grandparent_num
        ))
        
        section_start_y = y_pos + 5
        y_pos -= 25
        
        # Create linear fields
        c.setFont(LABEL_FONT, LABEL_FONT_SIZE)  # Reset to regular font for field labels
        start_y = y_pos
        current_y = start_y
        
        for i, label in enumerate(linear_fields):
            # Determine box height
            if "Other names used" in label:
                box_height = 40
            else:
                box_height = 16
            
            # Calculate positions
            label_y = current_y
            text_y = label_y - LABEL_TO_BOX_GAP - box_height
            next_y = text_y - BOX_TO_NEXT_LABEL_GAP
            
            # Parent A
            c.drawString(col1_x, label_y, label)
            create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentA_{label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                 f'{lang["form_field_labels"]["parent_a_of"].format(person_being_described=person_being_described, grandparent_num=grandparent_num)}: {label}',
                                 col1_x, text_y, col_width, box_height)
            
            # Parent B
            c.drawString(col2_x, label_y, label)
            create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentB_{label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                 f'{lang["form_field_labels"]["parent_b_of"].format(person_being_described=person_being_described, grandparent_num=grandparent_num)}: {label}',
                                 col2_x, text_y, col_width, box_height)
            
            current_y = next_y
        
        # Grid section
        grid_start_y = current_y - 15
        grid_field_width = (col_width - 10) // 2
        grid_field_height = 16
        
        c.setFont(LABEL_FONT, LABEL_FONT_SIZE)
        
        for row_idx, row in enumerate(grid_fields):
            grid_row_y = grid_start_y - (row_idx * grid_spacing_y)
            
            # First pass: calculate line counts for the entire row without drawing
            row_line_counts = []
            for col_idx, label in enumerate(row):
                # Calculate line counts for both columns to determine max
                line_count_a = calculate_wrapped_line_count(c, label, grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
                line_count_b = calculate_wrapped_line_count(c, label, grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
                
                # Store the maximum line count for this field
                row_line_counts.append(max(line_count_a, line_count_b))
            
            # Calculate the maximum line count for the entire row
            max_row_line_count = max(row_line_counts)
            text_field_y = grid_row_y - (max_row_line_count * 10) - 10
            
            # Second pass: draw labels and create text fields
            for col_idx, label in enumerate(row):
                grid_x_offset = col_idx * (grid_field_width + 10)
                
                # Draw labels only once for each position
                draw_wrapped_grid_label(c, label, col1_x + grid_x_offset, grid_row_y, 
                                       grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
                draw_wrapped_grid_label(c, label, col2_x + grid_x_offset, grid_row_y, 
                                       grid_field_width, LABEL_FONT, LABEL_FONT_SIZE)
                
                create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentA_{label.replace(chr(10), "").lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                     f'{lang["parent_headers"][f"parent_a_generation"].format(person_being_described=parent_section_person, grandparent_num=grandparent_num)}: {label.replace(chr(10), " ")}',
                                     col1_x + grid_x_offset, text_field_y, grid_field_width, grid_field_height)
                
                create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentB_{label.replace(chr(10), "").lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}',
                                     f'{lang["parent_headers"][f"parent_b_generation"].format(person_being_described=parent_section_person, grandparent_num=grandparent_num)}: {label.replace(chr(10), " ")}',
                                     col2_x + grid_x_offset, text_field_y, grid_field_width, grid_field_height)
        
        y_pos = grid_start_y - (len(grid_fields) * grid_spacing_y) - 15
        
        # Details sections - use generation_being_documented with singular form for individual person details
        citizenship_text = lang['form_fields']['citizenship_details'].format(generation_type=generation_being_documented)
        line_count_1 = draw_wrapped_grid_label(c, citizenship_text, col1_x, y_pos, col_width, LABEL_FONT, LABEL_FONT_SIZE)
        line_count_2 = draw_wrapped_grid_label(c, citizenship_text, col2_x, y_pos, col_width, LABEL_FONT, LABEL_FONT_SIZE)
        
        # Use the maximum line count for consistent spacing
        max_lines = max(line_count_1, line_count_2)
        y_pos -= (max_lines * 10) + 4  # Space for wrapped text plus minimal gap
        
        create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentA_citizenship_details',
                             lang['form_field_labels']['details_parent_a'].format(
                                 person_being_described=person_being_described,
                                 grandparent_num=grandparent_num
                             ),
                             col1_x, y_pos-40, col_width, 40)
        
        create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentB_citizenship_details',
                             lang['form_field_labels']['details_parent_b'].format(
                                 person_being_described=person_being_described,
                                 grandparent_num=grandparent_num
                             ),
                             col2_x, y_pos-40, col_width, 40)
        
        y_pos -= 50
        
        # Date of death
        c.drawString(col1_x, y_pos, lang['form_fields']['date_of_death'])
        c.drawString(col2_x, y_pos, lang['form_fields']['date_of_death'])
        y_pos -= 4
        
        create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentA_date_death',
                             lang['form_field_labels']['death_date_parent_a'].format(
                                 person_being_described=person_being_described,
                                 grandparent_num=grandparent_num
                             ),
                             col1_x, y_pos-16, 150, 16)
        
        create_form_textfield(c, f'{field_prefix}_{grandparent_num}_parentB_date_death',
                             lang['form_field_labels']['death_date_parent_b'].format(
                                 person_being_described=person_being_described,
                                 grandparent_num=grandparent_num
                             ),
                             col2_x, y_pos-16, 150, 16)
        
        y_pos -= 25
        
        # Vertical line
        section_end_y = y_pos
        c.line(column_divider_x, section_start_y, column_divider_x, section_end_y)
        
        # Add end of addendum indicator on last page
        if page_number == total_pages:
            c.setFont(SECTION_FONT, LABEL_FONT_SIZE)
            end_text = lang['headers']['end_indicator']
            text_width = c.stringWidth(end_text, SECTION_FONT, LABEL_FONT_SIZE)
            center_x = left_margin + (content_width - text_width) / 2
            c.drawString(center_x, section_end_y - 30, end_text)
        
        # Bottom margin check
        if section_end_y < bottom_margin + 5:
            print(f"Warning: Content may be too close to bottom margin on page {page_number}. End position: {section_end_y}")

def generate_all_generation_documents():
    """Generate G3-G20 documents with appropriate generation content for all languages"""
    # Get project root directory (two levels up from this file)
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    documents_dir = os.path.join(script_dir, "documents")
    
    if not os.path.exists(documents_dir):
        os.makedirs(documents_dir)
    
    # Load language configuration
    src_dir = os.path.dirname(os.path.abspath(__file__))
    lang_config = load_language_config(src_dir)
    if not lang_config:
        print("Error: Could not load language configuration")
        return False
    
    generated_files = []
    
    # Generate documents for each language
    for lang_code in ['EN', 'FR']:
        # Generate G3 through G20 documents for this language
        for applicant_gen in range(3, 21):  # G3 to G20
            # Calculate how many generations we need to document
            # G3 needs 1 generation (G0), G4 needs 2 generations (G1+G0), etc.
            generations_needed = applicant_gen - 2
            
            # Create filename with language prefix and generation number
            filename = os.path.join(documents_dir, f"CIT0001_Section9_Grandparent_Addendum_{lang_code}_G{applicant_gen:02d}.pdf")
            
            try:
                create_editable_section9(filename, generations_needed, lang_code, lang_config)
                generated_files.append(filename)
                print(f"Generated {lang_code}_G{applicant_gen}: {filename} ({generations_needed * 2} pages)")
            except Exception as e:
                print(f"Error generating {lang_code}_G{applicant_gen} document: {e}")
                return False
    
    print(f"\nSuccessfully generated {len(generated_files)} generation documents:")
    for filepath in generated_files:
        print(f"  {os.path.basename(filepath)}")
    
    return True

def main():
    """Command line interface for the form generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate CIT 0001 Section 9 Grandparent Addendum PDFs for different applicant generations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Generate all G3-G20 documents (both EN/FR)
  %(prog)s -g 4                               # Generate G4 documents (both EN/FR)
  %(prog)s -g 5 -o custom_form.pdf            # Generate single G5 document (English only)

Generation Guide:
  G3 applicant: 2 pages  (great-grandparents only)
  G4 applicant: 4 pages  (2x + great-grandparents)
  G5 applicant: 6 pages  (3x + 2x + great-grandparents)
  G6 applicant: 8 pages  (4x + 3x + 2x + great-grandparents)
  ...continuing to G10 applicant: 16 pages
        """
    )
    
    
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT_FILE", 
        help="Output PDF filename (default: CIT0001_Section9_Grandparent_Addendum.pdf)"
    )
    
    
    parser.add_argument(
        "-g", "--generation",
        type=int,
        metavar="N",
        help="Generate single document for specific applicant generation (3-10). If not specified, generates all G3-G10 documents."
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="CIT0001 Grandparent Addendum Generator v1.0.0"
    )
    
    args = parser.parse_args()
    
    
    # Validate generation argument if provided
    if args.generation is not None:
        if args.generation < 3 or args.generation > 20:
            print(f"Error: Generation must be between 3 and 20. G1 and G2 applicants don't need addendums.")
            return 1
    
    try:
        # Generate single specific generation document
        if args.generation is not None:
            generations_needed = args.generation - 2
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Load language configuration
            lang_config = load_language_config(script_dir)
            if not lang_config:
                print("Error: Could not load language configuration")
                return 1
            
            # Generate for both languages if no specific output filename
            if args.output:
                # Single file specified - generate English only
                create_editable_section9(args.output, generations_needed, 'EN', lang_config)
                print(f"Generated G{args.generation} document: {args.output} ({generations_needed * 2} pages)")
            else:
                # Generate both languages with standard naming
                project_root = os.path.dirname(os.path.dirname(script_dir))
                documents_dir = os.path.join(project_root, "documents")
                if not os.path.exists(documents_dir):
                    os.makedirs(documents_dir)
                
                for lang_code in ['EN', 'FR']:
                    filename = os.path.join(documents_dir, f"CIT0001_Section9_Grandparent_Addendum_{lang_code}_G{args.generation:02d}.pdf")
                    create_editable_section9(filename, generations_needed, lang_code, lang_config)
                    print(f"Generated {lang_code}_G{args.generation}: {filename} ({generations_needed * 2} pages)")
            return 0
        
        # Generate all G3-G10 documents (default behavior)
        else:
            if args.output:
                print("Error: Cannot specify custom output filename when generating all documents. Use -g to generate a single document.")
                return 1
            
            success = generate_all_generation_documents()
            return 0 if success else 1
        
    except Exception as e:
        print(f"Error generating PDF(s): {e}")
        return 1

if __name__ == "__main__":
    exit(main())