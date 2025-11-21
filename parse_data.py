import re
import json

def parse_line(line):
    # Regex to find phone numbers (simple pattern)
    phone_pattern = r'(\d{3,4}\s?\d{3}\s?\d{3,4})'
    phones = re.findall(phone_pattern, line)
    
    # Remove phones from line to get content
    content = line
    for p in phones:
        content = content.replace(p, '')
    
    # Clean up content
    content = content.strip().strip('-').strip()
    
    # Heuristic to separate address and situation
    # Often separated by (, ., or just space.
    # We'll just keep it as "content" for now, or try to split if possible.
    
    return content, phones

def get_area(text):
    text = text.lower()
    areas = [
        "vĩnh thạnh", "vĩnh ngọc", "vĩnh phương", "vĩnh hiệp", "vĩnh thái", "vĩnh trung", "vĩnh điềm",
        "diên khánh", "diên lạc", "diên điền", "diên phú", "diên an", "diên toàn", "diên sơn", "diên phước", "diên thọ", "diên hòa",
        "nha trang", "ngọc hiệp", "phước hải", "phước long", "vĩnh hải"
    ]
    for area in areas:
        if area in text:
            return area.title()
    return "Khác"

data = []
with open('pdf_content.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_entry = {}
id_counter = 1

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # Skip headers
    if "Địa chỉ" in line or "Số điện thoại" in line:
        continue
        
    content, phones = parse_line(line)
    
    if not content and not phones:
        continue

    # If line starts with a number like "1.", "2.", it might be an item.
    # But the file seems to be line-based items mostly.
    # Some lines are just phones or just text.
    
    # We'll treat each line with a phone number as a primary entry.
    # If a line has no phone but follows one, maybe it's continuation?
    # The file structure is a bit messy.
    # Let's assume each non-empty line is a potential request if it has address-like info.
    
    area = get_area(content)
    
    entry = {
        "id": id_counter,
        "content": content,
        "phones": phones,
        "area": area,
        "status": "Cần cứu hộ"
    }
    data.append(entry)
    id_counter += 1

# Filter out entries that are too short or look like noise
filtered_data = [d for d in data if len(d['content']) > 5 or len(d['phones']) > 0]

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

print(f"Parsed {len(filtered_data)} entries.")
