# 🚨 Emergency Rescue Management App

Ứng dụng web hỗ trợ **quản lý và điều phối cứu hộ khẩn cấp** trong các tình huống thiên tai như lũ lụt, bão, sạt lở…  
Tập trung vào việc **tổng hợp, phân loại, ưu tiên và xử lý** các ca cần cứu hộ một cách nhanh chóng, rõ ràng và dễ sử dụng.

---

## ✨ Tính năng chính

- 🔍 **Tìm kiếm & Lọc**
  - Tìm kiếm theo **địa chỉ**, **số điện thoại**, **khu vực**
  - Hỗ trợ lọc nhanh để tìm đúng ca cần xử lý

- 📋 **Quản lý danh sách cứu hộ**
  - Tab **"Cần cứu hộ"**: Hiển thị các ca đang chờ xử lý
  - Tab **"Đã cứu"**: Lưu lại các ca đã xử lý xong để theo dõi và thống kê

- 📞 **Gọi điện trực tiếp**
  - Click vào **số điện thoại** để mở ngay ứng dụng gọi điện trên thiết bị (mobile/desktop có hỗ trợ)

- 🗺️ **Xem vị trí trên bản đồ**
  - Mở trực tiếp vị trí ca cứu hộ trên **Google Maps** (nếu có địa chỉ/khu vực phù hợp)

- ➕ **Thêm ca cứu hộ mới**
  - Nhập **thủ công** từng ca
  - Hoặc **nhập hàng loạt từ file Excel** để tiết kiệm thời gian

- 🔄 **Phát hiện & loại bỏ trùng lặp**
  - Khi nhập từ Excel, hệ thống sẽ **tự động phát hiện và loại bỏ** các ca trùng lặp dựa trên thông tin (nội dung/địa chỉ + số điện thoại)

---

## 🛠️ Công nghệ sử dụng

- ⚛ **React** – Xây dựng giao diện người dùng
- ⚡ **Vite** – Công cụ build & dev server tốc độ cao
- 🎨 **Tailwind CSS** – Styling nhanh, linh hoạt
- 🔣 **Lucide React** – Bộ icon hiện đại
- 📊 **XLSX** – Đọc/ghi file Excel (import/export dữ liệu)

---

## 🚀 Cài đặt & Chạy dự án

### 1. Yêu cầu môi trường

- **Node.js** phiên bản **18+**
- **npm** hoặc **yarn**

### 2. Các bước cài đặt

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/rescue-app.git

# Di chuyển vào thư mục dự án
cd rescue-app

# Cài đặt dependencies
npm install

# Chạy ở chế độ development
npm run dev
