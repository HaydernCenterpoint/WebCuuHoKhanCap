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

def is_duplicate(case1, case2):
    """Kiểm tra trùng lặp"""
    # Check phones
    phones1 = set([normalize_phone(p) for p in case1['phones']])
    phones2 = set([normalize_phone(p) for p in case2['phones']])
    if phones1 and phones2 and phones1.intersection(phones2):
        return True
    
    # Check address similarity
    addr1 = case1['content'] # Đã là strict address
    addr2 = case2['content']
    if len(addr1) > 5 and len(addr2) > 5:
        if similarity(addr1, addr2) > 0.85: # Tăng ngưỡng lên cao hơn vì address đã sạch
            return True
    return False

def extract_location_strict(text):
    """
    Trích xuất địa điểm theo quy tắc nghiêm ngặt (V2 - Enhanced).
    """
    # 0. Pre-clean: Tách số dính liền với chữ (VD: Thọ13Hẻm -> Thọ 13 Hẻm)
    # Nhưng cẩn thận với địa chỉ số (VD: 23/10, 14 đường)
    # Logic: Nếu số nằm giữa 2 ký tự thường/hoa -> khả năng cao là lỗi dính
    text = re.sub(r'([a-zA-Z])(\d+)([a-zA-Z])', r'\1 \2 \3', text)
    
    # 1. Loại bỏ tiền tố Priority
    text = re.sub(r'^(Khẩn cấp|Ưu tiên cao|Thường)\s*[-:]?\s*', '', text, flags=re.IGNORECASE)
    
    # 2. Cắt tại dấu phân cách MẠNH
    for sep in ['.', '(', ':']:
        if sep in text: text = text.split(sep)[0]
        
    # 3. Xử lý dấu gạch ngang (-) và phẩy (,)
    # Tách thành các phần, chỉ giữ lại phần KHÔNG PHẢI là mô tả
    parts = re.split(r'\s*[-–,]\s*', text)
    valid_parts = []
    
    desc_keywords = [
        'nhà', 'có', 'nước', 'bị', 'kẹt', 'ngập', 'cần', 'người', 'bé', 'trẻ', 
        'ông', 'bà', 'mẹ', 'bố', 'gia đình', 'khu', 'dãy', 'hẻm trọ', 'phòng trọ',
        'tình trạng', 'sđt', 'liên hệ', 'gấp', 'khẩn', 'mất', 'không', 'từ', 'sau',
        'cạnh', 'kế', 'đối diện', 'gần', 'tại', 'ngay', 'chỗ'
    ]
    
    for i, part in enumerate(parts):
        part = part.strip()
        if not part: continue
        
        # Nếu part bắt đầu bằng số lượng (VD: 13 người, 3 trẻ em) -> Dừng
        if re.match(r'^\d+\s+(người|bé|trẻ|em|con|bà|ông|gia đình)', part.lower()):
            break
            
        # Nếu part chứa từ khóa mô tả ở đầu -> Dừng
        # Trừ trường hợp là chỉ dẫn địa lý hợp lệ (VD: Gần cầu...)
        is_desc = False
        part_lower = part.lower()
        
        # Check keywords
        for k in desc_keywords:
            if part_lower.startswith(k):
                # Exception: "Gần" + Tên riêng (Viết hoa) -> Có thể là địa chỉ
                if k == 'gần' and i == 0: 
                    is_desc = False
                else:
                    is_desc = True
                break
        
        if is_desc: break
        valid_parts.append(part)
        
    text = ', '.join(valid_parts)
    
    # 4. Xử lý lặp từ (VD: 398/15 Lê Đại Cương398/15 LĐC)
    # Tìm chuỗi lặp lại dài nhất
    n = len(text)
    for length in range(10, n // 2 + 1):
        substr = text[:length]
        rest = text[length:]
        if substr in rest:
            # Nếu phần lặp lại nằm ngay sau -> Cắt
            if rest.startswith(substr):
                text = substr
                break
            # Nếu lặp lại nhưng có chút rác ở giữa -> Cắt
            elif rest.strip().startswith(substr):
                text = substr
                break

    # 5. Cleanup cuối cùng
    text = re.sub(r'\d{9,11}', '', text) # Xóa SĐT
    text = text.strip()
    text = text.strip('-,.')
    
    # 6. Validation: Địa chỉ quá ngắn hoặc chỉ toàn số -> Bỏ
    if len(text) < 4 or text.isdigit():
        return ""
        
    return text

def parse_strict():
    print("🚀 BẮT ĐẦU TRÍCH XUẤT ĐỊA CHỈ NGHIÊM NGẶT...")
    
    with open('pdf_content.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    raw_cases = []
    current_id = 1
    phone_pattern = r'0[\d\s\.]{8,}'
    
    # Area mapping (như cũ)
    area_keywords = {
        'Vĩnh Thạnh': 'Vĩnh Thạnh', 'Chợ Ga': 'Vĩnh Thạnh', 'Phú Bình': 'Vĩnh Thạnh',
        'Vĩnh Ngọc': 'Vĩnh Ngọc', 'Lương Định Của': 'Vĩnh Ngọc', 'Xuân Lạc': 'Vĩnh Ngọc',
        'Vĩnh Hiệp': 'Vĩnh Hiệp', 'Vĩnh Thái': 'Vĩnh Thái', 'Thái Thông': 'Vĩnh Thái',
        'Vĩnh Trung': 'Vĩnh Trung', 'Vĩnh Phương': 'Vĩnh Phương', 'Vĩnh Hải': 'Vĩnh Hải',
        'Bắc Nha Trang': 'Bắc Nha Trang', 'Đường 23/10': 'Đường 23/10', 'Cầu Bè': 'Cầu Bè',
        'Cầu Dứa': 'Cầu Dứa', 'Cầu Ké': 'Cầu Ké', 'Cầu Gỗ': 'Cầu Gỗ', 'Cây Dầu Đôi': 'Cây Dầu Đôi',
        'Gò Cây Sung': 'Gò Cây Sung', 'Phú Nông': 'Phú Nông', 'Bệnh Viện Đường Sắt': 'BV Đường Sắt',
        'BV Đường Sắt': 'BV Đường Sắt', 'Ngọc Hiệp': 'Ngọc Hiệp', 'Phước Đồng': 'Phước Đồng',
        'Đồng Muối': 'Phước Long', 'Diên An': 'Diên An', 'Phú Ân Nam': 'Diên An',
        'Diên Toàn': 'Diên Toàn', 'Diên Thọ': 'Diên Thọ', 'Diên Phước': 'Diên Phước',
        'Diên Lạc': 'Diên Lạc', 'Diên Sơn': 'Diên Sơn', 'Diên Lâm': 'Diên Lâm',
        'Diên Tân': 'Diên Tân', 'Diên Điền': 'Diên Điền', 'Diên Phú': 'Diên Phú',
        'Diên Hòa': 'Diên Hòa', 'Bình Khánh': 'Diên Hòa', 'Diên Khánh': 'Diên Khánh',
        'Suối Hiệp': 'Suối Hiệp', 'Bàn Thạch': 'Bàn Thạch', 'Võ Cạnh': 'Võ Cạnh',
        'Võ Dõng': 'Võ Dõng', 'Xuân Sơn': 'Xuân Sơn',
    }
    sorted_areas = sorted(area_keywords.keys(), key=len, reverse=True)

    for line in lines:
        line = line.strip()
        if not line or 'Mức độ ưu tiên' in line or 'CHỖ NÀO' in line: continue
        
        # 1. Parse Priority
        priority = 'MEDIUM'
        line_lower = line.lower()
        if any(k in line_lower for k in ['khẩn cấp', 'nguy kịch', 'sắp đẻ', 'vỡ ối', 'tai biến']): priority = 'CRITICAL'
        elif any(k in line_lower for k in ['ưu tiên cao', 'người già', 'trẻ em', 'bà bầu']): priority = 'HIGH'
        
        # 2. Extract Phones
        phones = []
        matches = re.findall(phone_pattern, line)
        for p in matches:
            clean = re.sub(r'[^\d]', '', p)
            if 9 <= len(clean) <= 11:
                if len(clean) == 10: phones.append(f"{clean[:4]} {clean[4:7]} {clean[7:]}")
                else: phones.append(clean)
                
        # 3. STRICT LOCATION EXTRACTION
        # Lấy content gốc, bỏ số điện thoại
        content_for_extract = line
        for p in matches:
            content_for_extract = content_for_extract.replace(p, '')
            
        # Áp dụng hàm trích xuất
        strict_address = extract_location_strict(content_for_extract)
        
        if len(strict_address) < 3: continue # Quá ngắn -> Bỏ
        
        # 4. Determine Area
        area = 'Khác'
        for k in sorted_areas:
            if k.lower() in strict_address.lower(): # Check trên địa chỉ đã clean
                area = area_keywords[k]
                break
        
        # Fallback area check
        if area == 'Khác':
            match = re.search(r'(xã|thôn|phường)\s+([A-ZĐ][a-zà-ỹ]+)', strict_address)
            if match:
                # Logic map thêm nếu cần
                pass

        raw_cases.append({
            "id": current_id,
            "content": strict_address, # LƯU ĐỊA CHỈ ĐÃ CLEAN
            "original_content": content_for_extract.strip(), # Lưu lại gốc để tham khảo nếu cần
            "phones": phones,
            "area": area,
            "priority": priority,
            "isRescued": False
        })
        current_id += 1
        
    # Deduplicate (Blocking by Area)
    print(f"📝 Parsed {len(raw_cases)} cases. Deduplicating...")
    cases_by_area = {}
    for c in raw_cases:
        if c['area'] not in cases_by_area: cases_by_area[c['area']] = []
        cases_by_area[c['area']].append(c)
        
    unique_cases = []
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    
    for area, group in cases_by_area.items():
        group.sort(key=lambda x: x['content']) # Sort by content
        skip = set()
        for i in range(len(group)):
            if i in skip: continue
            curr = group[i]
            dups = [curr]
            # Check neighbors
            for j in range(i+1, min(i+15, len(group))):
                if j in skip: continue
                if is_duplicate(curr, group[j]):
                    dups.append(group[j])
                    skip.add(j)
            
            # Merge: Keep highest priority, merge phones
            best = min(dups, key=lambda x: priority_order[x['priority']])
            all_phones = set()
            for d in dups: all_phones.update(d['phones'])
            best['phones'] = sorted(list(all_phones))[:5]
            unique_cases.append(best)
            
    # Re-index
    for i, c in enumerate(unique_cases, 1): c['id'] = i
    
    # Save
    with open('rescue-app/src/data.json', 'w', encoding='utf-8') as f:
        json.dump(unique_cases, f, ensure_ascii=False, indent=2)
        
    print(f"✅ DONE! Saved {len(unique_cases)} clean locations.")
    
    # Preview
    print("\n🔍 PREVIEW (Input -> Output):")
    for c in unique_cases[:10]:
        print(f"📍 {c['content']}")

if __name__ == "__main__":
    parse_strict()
