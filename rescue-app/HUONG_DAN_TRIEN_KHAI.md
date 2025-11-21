# 🚀 HƯỚNG DẪN TRIỂN KHAI VÀ CHIA SẺ WEB

## 📍 Hiện tại: Chỉ chạy trên máy của bạn

Web đang chạy ở chế độ phát triển (development) trên máy của bạn tại `http://localhost:5173/`

---

## 🌐 CÁCH 1: Đưa lên Internet (Khuyến nghị ⭐)

### Dùng Netlify (MIỄN PHÍ & Dễ nhất)

#### Bước 1: Build ứng dụng
```bash
cd c:\Users\ADMIN\Desktop\Tét2222\rescue-app
npm run build
```
→ Tạo thư mục `dist` chứa web đã đóng gói

#### Bước 2: Đưa lên Netlify
1. Truy cập: https://app.netlify.com/drop
2. Kéo thả thư mục **`dist`** vào
3. Đợi vài giây → Nhận link (VD: `https://rescue-xyz.netlify.app`)
4. Chia sẻ link cho mọi người

✅ **Ưu điểm**: 
- Ai cũng truy cập được qua Internet
- Miễn phí mãi mãi
- Có link đẹp
- Không cần máy bạn mở

❌ **Lưu ý**: 
- Dữ liệu vẫn lưu riêng trên từng máy (chưa đồng bộ)

---

## 📡 CÁCH 2: Chia sẻ trong mạng nội bộ (WiFi)

### Nếu máy bạn đang chạy web (npm run dev -- --host)

**Người khác cùng mạng WiFi** có thể truy cập bằng:

```
http://192.168.1.4:5173/
```

> Thay `192.168.1.4` bằng **IP máy bạn** (xem trong terminal khi chạy `npm run dev -- --host`)

✅ **Ưu điểm**: 
- Nhanh, không cần setup gì thêm
- Tốt cho văn phòng/nhà có cùng WiFi

❌ **Nhược điểm**: 
- Máy bạn phải luôn bật và chạy web
- Chỉ dùng được trong mạng nội bộ
- Nếu tắt máy = web tắt

---

## 💾 CÁCH 3: Chia sẻ Source Code

### Cho người khác tự chạy trên máy của họ

#### Bước 1: Nén thư mục
Nén thư mục `c:\Users\ADMIN\Desktop\Tét2222\rescue-app` thành file ZIP

#### Bước 2: Gửi cho người khác

#### Bước 3: Họ giải nén và chạy:
```bash
# Cài đặt dependencies
npm install

# Chạy web
npm run dev
```

✅ **Ưu điểm**: 
- Họ có toàn quyền chỉnh sửa
- Không phụ thuộc vào máy bạn

❌ **Nhược điểm**: 
- Họ cần biết cài Node.js
- Dữ liệu riêng biệt giữa các máy

---

## 🔄 Giải pháp đồng bộ dữ liệu (Cho nhiều người cùng dùng)

**Vấn đề**: Hiện tại mỗi máy lưu dữ liệu riêng

**Giải pháp**: Tích hợp Supabase hoặc Firebase

### Cần làm:
1. Tạo tài khoản Supabase (miễn phí): https://supabase.com
2. Tạo project mới
3. Lấy API Key
4. Gửi cho mình → Mình tích hợp vào code

→ Sau đó: Ai cũng thấy dữ liệu chung, cập nhật real-time!

---

## 📝 Tóm tắt các tình huống

| Tình huống | Giải pháp phù hợp |
|------------|-------------------|
| Chia sẻ cho mọi người (cả ngoài mạng) | **CÁCH 1: Netlify** ⭐ |
| Chỉ dùng trong văn phòng/nhà | **CÁCH 2: WiFi nội bộ** |
| Gửi cho dev khác phát triển tiếp | **CÁCH 3: Source code** |
| Nhiều người cùng cập nhật dữ liệu | Cần **Supabase** |

---

## 🆘 Cần hỗ trợ?

- **Deploy lên Netlify**: Chỉ cần chạy `npm run build` rồi kéo thả thư mục `dist`
- **Tích hợp Supabase**: Liên hệ để được setup

---

**Cập nhật**: 21/11/2025
