import re
import json

def parse_warehouses(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    warehouses = []
    current_state = None
    
    # Regex to find codes like (BHM1) or (PHX3, PHX6)
    # Also handles cases like [102] which are citations, we should ignore citations for codes.
    # Codes are usually 3-4 uppercase letters followed by a digit, e.g., BHM1, PHX3, PHXZ, KORD.
    # Sometimes they are comma separated inside parentheses.
    
    code_pattern = re.compile(r'\b([A-Z]{3,4}\d?)\b')
    
    # List of states to identify state headers (simplified, or just assume lines without parens/codes are states?)
    # But some cities might not have codes.
    # Let's assume if a line doesn't match the "City (Codes)" pattern, it might be a state.
    # Actually, the user input has "Alabama", "Arizona" on separate lines.
    
    # Let's use a known list of states to be safe, or just heuristics.
    # Heuristic: If line has no parentheses and no brackets (except maybe citations), it's a state?
    # Or if it matches a state name.
    
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
        "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
        "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
        "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
        "West Virginia", "Wisconsin", "Wyoming"
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a state
        # Remove citations like [102] for checking
        clean_line = re.sub(r'\[\d+\]', '', line).strip()
        clean_line = re.sub(r'\[note \d+\]', '', clean_line).strip()
        
        if clean_line in states:
            current_state = clean_line
            continue
            
        # It's a city/warehouse line
        # Extract city and codes
        # Format: "City (Code1, Code2)" or "City (Code1)" or "City[citation] (Code1)"
        
        # Find content in parentheses
        parens_match = re.search(r'\((.*?)\)', line)
        
        codes = []
        if parens_match:
            content = parens_match.group(1)
            # Find all codes in the content
            found_codes = code_pattern.findall(content)
            # Filter out things that look like codes but might be notes? 
            # The regex \b([A-Z]{3,4}\d?)\b matches BHM1, PHX3, PHXZ, KORD.
            # It might match "opening" or "TBD" if they were uppercase, but they are usually lowercase.
            # "opening 2026" -> "opening" is not matched by A-Z.
            # "TBD" -> Matches [A-Z]{3}.
            
            for code in found_codes:
                if code in ["TBD", "TBA"]:
                    continue
                codes.append(code)
        
        # Extract city name (everything before the first parenthesis or bracket)
        city_match = re.split(r'[\(\[]', line)[0].strip()
        city = city_match
        
        if codes:
            for code in codes:
                warehouses.append({
                    "State": current_state,
                    "City": city,
                    "Code": code,
                    "Name": f"Amazon_{code}"
                })
        else:
            # No codes found?
            # e.g. "Montgomery[102]"
            # Maybe we skip or just log it.
            # The user asked for "Amazon_BHM1" style. If no code, we can't name it like that easily.
            # But maybe we can try to find the code later?
            # For now, let's just log it as "Unknown" code.
            pass
            # print(f"Skipping line with no codes: {line}")

    return warehouses

if __name__ == "__main__":
    data = parse_warehouses("warehouses.txt")
    print(json.dumps(data, indent=2))
    print(f"Found {len(data)} warehouses.")
