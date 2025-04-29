import re

def extract_division(contest_name):
    """
    Extracts the division from contest name.
    - If multiple divisions (Div. 1 + Div. 2), pick the lower (larger number, e.g., Div 2).
    - If no division found, return Div 0.
    """
    matches = re.findall(r'Div\.\s*([1-4])', contest_name)
    
    if matches:
        lowest_div = max(map(int, matches))
        return f"Div {lowest_div}"
    else:
        return "Div 0"