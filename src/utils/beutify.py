import re

def beautify_plan(text: str) -> str:
    """
    Attempt to format the generated plan text by adding structure and cleaning excess whitespace.
    """
    # Ensure that any "Day X:" starts on a new line.
    text = re.sub(r'(Day\s*\d+:)', r'\n\1', text)
    
    # Optionally, insert a newline before common sections, e.g., 'Nutritional Guidelines' and 'Progress Tracking Tips'
    text = re.sub(r'(Nutritional Guidelines:)', r'\n\1', text)
    text = re.sub(r'(Progress Tracking Tips:)', r'\n\1', text)
    
    # Remove any extra blank lines (more than one consecutive newline).
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Trim leading and trailing whitespace
    return text.strip()
