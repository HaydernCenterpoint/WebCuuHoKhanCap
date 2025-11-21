import re
import json
from difflib import SequenceMatcher

def normalize_text(text):
    """Chuẩn hóa text để so sánh"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def normalize_phone(phone):
    """Chuẩn hóa số điện thoại"""
    return re.sub(r'\D', '', phone)

def similarity(a, b):
    """Tính độ tương đồng giữa 2 chuỗi"""
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()

def extract_address_core(content):
    """Trích xuất phần địa chỉ cốt lõi từ content"""
    # Loại bỏ phần mô tả tình trạng thường gặp
    clean_content = re.sub(r'\(.*?\)', '', content) # Bỏ ngoặc
    clean_content = re.sub(r'\d+\s*(người|em|bé|cháu|đứa|con|lớn|nhỏ)', '', clean_content, flags=re.IGNORECASE)
    
    # Lấy phần đầu (thường là địa chỉ)
    words = clean_content.split()
    if len(words) > 15:
        address = ' '.join(words[:15])
    else:
        address = clean_content
    return normalize_text(address)

def is_duplicate(case1, case2, phone_threshold=0.5, address_threshold=0.8):
    """Kiểm tra 2 case có trùng lặp không"""
    # Check phone numbers
    phones1 = set([normalize_phone(p) for p in case1['phones']])
    phones2 = set([normalize_phone(p) for p in case2['phones']])
    
    if phones1 and phones2:
        common_phones = phones1.intersection(phones2)
        if len(common_phones) > 0:
            return True
    
    # Check address similarity
    addr1 = extract_address_core(case1['content'])
    addr2 = extract_address_core(case2['content'])
    
    if addr1 and addr2 and len(addr1) > 8 and len(addr2) > 8:
        sim = similarity(addr1, addr2)
        if sim >= address_threshold:
            return True
    
    return False

def merge_duplicates(cases):
    """Gộp các case trùng lặp, giữ lại case có priority cao nhất (Phiên bản tối ưu)"""
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    
    # 1. Nhóm các case theo Area để giảm phạm vi so sánh
    cases_by_area = {}
    for case in cases:
        area = case['area']
        if area not in cases_by_area:
            cases_by_area[area] = []
        cases_by_area[area].append(case)
        
    unique_cases = []
    
    # 2. Xử lý từng nhóm Area
    for area, area_cases in cases_by_area.items():
        # Sort theo content để các case giống nhau nằm gần nhau
        area_cases.sort(key=lambda x: x['content'])
        
        skip_indices = set()
        
        for i in range(len(area_cases)):
            if i in skip_indices:
                continue
                
            current_case = area_cases[i]
            duplicates = [current_case]
            
            # Chỉ so sánh với 20 case tiếp theo (vì đã sort)
            # Điều này giảm độ phức tạp từ O(N^2) xuống O(N*K)
            for j in range(i + 1, min(i + 20, len(area_cases))):
                if j in skip_indices:
                    continue
                    
                if is_duplicate(current_case, area_cases[j]):
                    duplicates.append(area_cases[j])
                    skip_indices.add(j)
            
            # Merge logic
            # Chọn case có priority cao nhất
            best_case = min(duplicates, key=lambda c: priority_order.get(c['priority'], 99))
            
            # Merge phones
            all_phones = set()
            for dup in duplicates:
                all_phones.update(dup['phones'])
            best_case['phones'] = sorted(list(all_phones))[:5]
            
            # Merge content (lấy cái dài nhất)
            longest_content = max(duplicates, key=lambda x: len(x['content']))['content']
            best_case['content'] = longest_content
            
            unique_cases.append(best_case)
            
    return unique_cases

def parse_rescue_data_final(input_file):
    """Parse dữ liệu cứu hộ hoàn thiện"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    raw_cases = []
    current_id = 1
    phone_pattern = r'0[\d\s\.]{8,}'
    
    # Danh sách khu vực MỞ RỘNG
    area_keywords = {
        # Nha Trang & Vùng ven
        'Vĩnh Thạnh': 'Vĩnh Thạnh',
        'Chợ Ga': 'Vĩnh Thạnh',
        'Phú Bình': 'Vĩnh Thạnh',
        'Vĩnh Ngọc': 'Vĩnh Ngọc',
        'Lương Định Của': 'Vĩnh Ngọc',
        'Xuân Lạc': 'Vĩnh Ngọc',
        'Vĩnh Hiệp': 'Vĩnh Hiệp',
        'Vĩnh Thái': 'Vĩnh Thái',
        'Thái Thông': 'Vĩnh Thái',
        'Vĩnh Trung': 'Vĩnh Trung',
        'Vĩnh Phương': 'Vĩnh Phương',
        'Vĩnh Hải': 'Vĩnh Hải',
        'Bắc Nha Trang': 'Bắc Nha Trang',
        'Đường 23/10': 'Đường 23/10',
        'Cầu Bè': 'Cầu Bè',
        'Cầu Dứa': 'Cầu Dứa',
        'Cầu Ké': 'Cầu Ké',
        'Cầu Gỗ': 'Cầu Gỗ',
        'Cây Dầu Đôi': 'Cây Dầu Đôi',
        'Gò Cây Sung': 'Gò Cây Sung',
        'Phú Nông': 'Phú Nông',
        'Bệnh Viện Đường Sắt': 'BV Đường Sắt',
        'BV Đường Sắt': 'BV Đường Sắt',
        'Ngọc Hiệp': 'Ngọc Hiệp',
        'Phước Đồng': 'Phước Đồng',
        'Đồng Muối': 'Phước Long',
        
        # Diên Khánh (Chi tiết)
        'Diên An': 'Diên An',
        'Phú Ân Nam': 'Diên An',
        'Diên Toàn': 'Diên Toàn',
        'Diên Thọ': 'Diên Thọ',
        'Diên Phước': 'Diên Phước',
        'Diên Lạc': 'Diên Lạc',
        'Diên Sơn': 'Diên Sơn',
        'Diên Lâm': 'Diên Lâm',
        'Diên Tân': 'Diên Tân',
        'Diên Điền': 'Diên Điền',
        'Diên Phú': 'Diên Phú',
        'Diên Hòa': 'Diên Hòa',
        'Bình Khánh': 'Diên Hòa',
        'Diên Khánh': 'Diên Khánh',
        'Suối Hiệp': 'Suối Hiệp',
        
        # Khác
        'Bàn Thạch': 'Bàn Thạch',
        'Võ Cạnh': 'Võ Cạnh',
        'Võ Dõng': 'Võ Dõng',
        'Xuân Sơn': 'Xuân Sơn',
    }
    
    # Ưu tiên check từ khóa dài trước (VD: "Diên An" trước "Diên")
    sorted_area_keywords = sorted(area_keywords.keys(), key=len, reverse=True)
    
    for line in lines:
        line = line.strip()
        if not line or 'Mức độ ưu tiên' in line or 'CHỖ NÀO' in line:
            continue
            
        # 1. Parse Priority (Cột 1 hoặc từ khóa trong câu)
        priority = 'MEDIUM' # Default
        line_lower = line.lower()
        
        if line_lower.startswith('khẩn cấp') or 'khẩn cấp' in line_lower or 'nguy kịch' in line_lower or 'sắp đẻ' in line_lower or 'vỡ ối' in line_lower or 'tai biến' in line_lower:
            priority = 'CRITICAL'
        elif line_lower.startswith('ưu tiên cao') or 'ưu tiên cao' in line_lower or 'người già' in line_lower or 'trẻ em' in line_lower or 'trẻ nhỏ' in line_lower or 'bà bầu' in line_lower or 'mang thai' in line_lower:
            priority = 'HIGH'
        elif line_lower.startswith('thường') or 'thường' in line_lower:
            priority = 'MEDIUM'
            
        # 2. Extract Phones
        phones = []
        phone_matches = re.findall(phone_pattern, line)
        for phone in phone_matches:
            clean_phone = re.sub(r'[^\d]', '', phone)
            if 9 <= len(clean_phone) <= 11:
                if len(clean_phone) == 10:
                    formatted = f"{clean_phone[:4]} {clean_phone[4:7]} {clean_phone[7:]}"
                else:
                    formatted = clean_phone
                phones.append(formatted)
        
        # 3. Clean Content
        content = line
        # Remove phones
        for p in phone_matches:
            content = content.replace(p, '')
        # Remove priority prefixes at start
        content = re.sub(r'^(Khẩn cấp|Ưu tiên cao|Thường)\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) < 5: continue

        # 4. Determine Area
        area = 'Khác'
        content_lower = content.lower()
        
        # Check area keywords
        for keyword in sorted_area_keywords:
            if keyword.lower() in content_lower:
                area = area_keywords[keyword]
                break
        
        # Fallback: Nếu vẫn là Khác, thử tìm "Thôn X", "Xã Y"
        if area == 'Khác':
            match = re.search(r'(xã|thôn|phường)\s+([A-ZĐ][a-zà-ỹ]+(\s+[A-ZĐ][a-zà-ỹ]+)+)', content)
            if match:
                potential_area = match.group(2)
                # Map lại nếu có trong DB
                for keyword in sorted_area_keywords:
                     if keyword.lower() in potential_area.lower():
                        area = area_keywords[keyword]
                        break
        
        raw_cases.append({
            "id": current_id,
            "content": content,
            "phones": phones,
            "area": area,
            "priority": priority,
            "isRescued": False
        })
        current_id += 1

    print(f"📝 Raw cases: {len(raw_cases)}")
    
    # Deduplicate
    print("🔍 Deduplicating...")
    unique_cases = merge_duplicates(raw_cases)
    print(f"✅ Unique cases: {len(unique_cases)} (Removed {len(raw_cases) - len(unique_cases)})")
    
    # Re-index
    for i, case in enumerate(unique_cases, 1):
        case['id'] = i
        
    return unique_cases

# Run
print("🚀 STARTING FINAL PARSE...")
data = parse_rescue_data_final('pdf_content.txt')

# Stats
area_counts = {}
priority_counts = {}
for c in data:
    area_counts[c['area']] = area_counts.get(c['area'], 0) + 1
    priority_counts[c['priority']] = priority_counts.get(c['priority'], 0) + 1

print("\n📊 PRIORITY STATS:")
for p, c in priority_counts.items():
    print(f"  {p}: {c}")

print("\n🗺️ AREA STATS (Top 20):")
for a, c in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {a}: {c}")

# Save
with open('rescue-app/src/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("\n💾 Saved to rescue-app/src/data.json")
