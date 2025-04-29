import json
import re

# Define a reusable separator regex for spaces, hyphens, en-dashes, em-dashes, parentheses, and commas
_sep = r"[\s\-\u2013\u2014\(\),]*"

# Build the canonical map with compiled patterns
_canonical_map = {
    'IITBHU':        re.compile(rf"\b(?:iit){_sep}bhu\b|\b(?:iit){_sep}varanasi\b", re.IGNORECASE),
    'IITBOMBAY':     re.compile(rf"\b(?:iit){_sep}bombay\b|\b(?:iit){_sep}b\b|\biitb(?:ombay)?\b", re.IGNORECASE),
    'IITDELHI':      re.compile(rf"\b(?:iit){_sep}delhi\b|\biitd(?:elhi)?\b", re.IGNORECASE),
    'IITDHANBAD':    re.compile(rf"\b(?:iit){_sep}(?:ism{_sep})?dhanbad\b|\biitd\b", re.IGNORECASE),
    'IITGUWAHATI':   re.compile(rf"\b(?:iit){_sep}guwahati\b|\biitg\b", re.IGNORECASE),
    'IITHYDERABAD':  re.compile(rf"\b(?:iit){_sep}hyderabad\b|\biith\b", re.IGNORECASE),
    'IITINDORE':     re.compile(rf"\b(?:iit){_sep}indore\b|\biiti\b", re.IGNORECASE),
    'IITJAMMU':      re.compile(rf"\b(?:iit){_sep}jammu\b|\biitj\b", re.IGNORECASE),
    'IITJODHPUR':    re.compile(rf"\b(?:iit){_sep}jodhpur\b|\biitjodhpur\b|\biitj\b", re.IGNORECASE),
    'IITKANPUR':     re.compile(rf"\b(?:iit){_sep}kanpur\b|\biitk\b", re.IGNORECASE),
    'IITKHARAGPUR':  re.compile(rf"\b(?:iit){_sep}kharagpur\b|\biitkgp\b", re.IGNORECASE),
    'IITMADRAS':     re.compile(rf"\b(?:iit){_sep}(?:madras|chennai)\b|\biitm\b", re.IGNORECASE),
    'IITMANDI':      re.compile(rf"\b(?:iit){_sep}mandi\b|\biitm(?:andi)?\b", re.IGNORECASE),
    'IITPALAKKAD':   re.compile(rf"\b(?:iit){_sep}palakkad\b", re.IGNORECASE),
    'IITPATNA':      re.compile(rf"\b(?:iit){_sep}patna\b|\biitp\b", re.IGNORECASE),
    'IITROORKEE':    re.compile(rf"\b(?:iit){_sep}roorkee\b|\biitr\b", re.IGNORECASE),
    'IITROPAR':      re.compile(rf"\b(?:iit){_sep}ropar\b", re.IGNORECASE),
    'IITBILAI':      re.compile(rf"\b(?:iit){_sep}bhilai\b", re.IGNORECASE),
    'IITDHARWAD':    re.compile(rf"\b(?:iit){_sep}dharwad\b", re.IGNORECASE),
    'IITGOA':        re.compile(rf"\b(?:iit){_sep}goa\b", re.IGNORECASE),
    'IITBHUBANESHWAR': re.compile(rf"\b(?:iit){_sep}bhubaneswar\b", re.IGNORECASE),
    # BITS Pilani variants
    'BITSPILANI':    re.compile(rf"\bbits{_sep}pilani\b", re.IGNORECASE),
    'BITSGOA':       re.compile(rf"\bbits{_sep}goa\b", re.IGNORECASE),
    'BITSHYDERABAD': re.compile(rf"\bbits{_sep}hyderabad\b", re.IGNORECASE),
    'BITSKKBIRLA':   re.compile(rf"\bbits{_sep}kk{_sep}birla\b", re.IGNORECASE),
}

def map_organizations(raw_list, canonical_map=_canonical_map):
    """
    Given a list of raw organization names, returns a dict mapping each raw name to its canonical key.
    Unmatched names map to 'Unknown'.
    """
    mapped = {}
    for org in raw_list:
        found = next((canon for canon, pat in canonical_map.items() if pat.search(org)), None)
        mapped[org] = found or 'Unknown'
    return mapped

def load_and_map_from_file(filename, canonical_map=_canonical_map):
    """
    Load a JSON array of organization names from `filename` and map them.
    Returns the mapping dict.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        raw_list = json.load(f)
    return map_organizations(raw_list, canonical_map)

def map_single_organization(org_name, canonical_map=_canonical_map):
    """
    Given a single organization name as string, returns the mapped canonical key.
    Returns 'Unknown' if no match is found.
    """
    found = next((canon for canon, pat in canonical_map.items() if pat.search(org_name)), None)
    return found or 'Unknown'

# Example usage:
# if __name__ == '__main__':
#     result = load_and_map_from_file('organization_list.txt')
#     for raw, canon in result.items():
#         print(f"{raw!r:45} -> {canon}")
#
#     single_result = map_single_organization('IIT (BHU)')
#     print(single_result)
