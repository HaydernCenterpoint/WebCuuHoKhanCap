# 🚀 HƯỚNG DẪN ĐƯA CODE LÊN GITHUB

## 📋 Chuẩn bị

### 1. Cài đặt Git (nếu chưa có)
- Download: https://git-scm.com/download/win
- Cài đặt với các tùy chọn mặc định
- Khởi động lại terminal/Command Prompt

### 2. Tạo tài khoản GitHub (nếu chưa có)
- Truy cập: https://github.com
- Bấm "Sign up" và làm theo hướng dẫn

---

## 🎯 BƯỚC 1: Khởi tạo Git trong dự án

Mở Command Prompt/PowerShell tại thư mục dự án:

```bash
cd c:\Users\ADMIN\Desktop\Tét2222\rescue-app
```

Khởi tạo Git repository:

```bash
git init
git add .
git commit -m "Initial commit - Rescue App"
```

---

## 🌐 BƯỚC 2: Tạo Repository trên GitHub

### Cách 1: Qua giao diện web (Dễ nhất)

1. Đăng nhập GitHub
2. Bấm nút **"+"** góc trên bên phải → Chọn **"New repository"**
3. Điền thông tin:
   - **Repository name**: `rescue-app` (hoặc tên bạn muốn)
   - **Description**: "Emergency Rescue Management App"
   - Chọn **Public** (công khai) hoặc **Private** (riêng tư)
   - **KHÔNG** tick "Add a README file" (vì đã có code rồi)
4. Bấm **"Create repository"**

---

## 📤 BƯỚC 3: Push code lên GitHub

Sau khi tạo repository, GitHub sẽ hiển thị các lệnh. Chạy:

```bash
# Thay YOUR_USERNAME bằng tên GitHub của bạn
# Thay rescue-app bằng tên repository bạn vừa tạo

git remote add origin https://github.com/YOUR_USERNAME/rescue-app.git
git branch -M main
git push -u origin main
```

**Ví dụ**: Nếu username là `nguyenvana` và repo là `rescue-app`:

```bash
git remote add origin https://github.com/nguyenvana/rescue-app.git
git branch -M main
git push -u origin main
```

Hệ thống sẽ yêu cầu đăng nhập → Nhập username và password GitHub

---

## ✅ BƯỚC 4: Xác nhận thành công

1. Truy cập: `https://github.com/YOUR_USERNAME/rescue-app`
2. Bạn sẽ thấy tất cả code đã được upload

---

## 🔄 Cập nhật code sau này

Khi có thay đổi, chạy:

```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

---

## 🌐 BONUS: Deploy từ GitHub lên Netlify

### Cách deploy tự động (mỗi khi push code mới):

1. Truy cập: https://app.netlify.com
2. Bấm **"Add new site"** → **"Import an existing project"**
3. Chọn **GitHub** → Chọn repository `rescue-app`
4. Build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
5. Bấm **"Deploy"**

➡️ Netlify sẽ tự động deploy và cập nhật mỗi khi bạn push code mới!

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. File đã được loại bỏ (trong .gitignore):
- ✅ `node_modules/` (thư mục cài đặt, rất nặng)
- ✅ `dist/` (file build, sẽ tự động tạo khi deploy)
- ✅ `.env` (thông tin bảo mật)

### 2. File sensitive data:
Nếu bạn có:
- API keys
- Passwords
- Thông tin nhạy cảm

→ **TUYỆT ĐỐI KHÔNG** push lên GitHub public!

### 3. File data.json:
File `src/data.json` chứa dữ liệu cứu hộ sẽ được push lên. Nếu đây là dữ liệu nhạy cảm:
- Tạo repo **Private**
- Hoặc thêm `src/data.json` vào `.gitignore`

---

## 📝 Tóm tắt các lệnh

```bash
# Lần đầu
cd c:\Users\ADMIN\Desktop\Tét2222\rescue-app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/rescue-app.git
git branch -M main
git push -u origin main

# Các lần sau (khi có thay đổi)
git add .
git commit -m "Mô tả thay đổi"
git push
```

---

## 🆘 Xử lý lỗi thường gặp

### Lỗi: "git command not found"
→ Chưa cài Git, tải tại: https://git-scm.com

### Lỗi: Authentication failed
→ Dùng Personal Access Token thay vì password:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Tạo token mới
3. Dùng token này thay cho password

### Lỗi: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/rescue-app.git
```

---

## 🎓 Sau khi lên GitHub

Bạn có thể:
1. ✅ Chia sẻ link GitHub cho người khác xem code
2. ✅ Cho người khác clone về: `git clone https://github.com/YOUR_USERNAME/rescue-app.git`
3. ✅ Deploy lên Netlify/Vercel
4. ✅ Làm việc nhóm (tạo branches, pull requests...)

---

**Cập nhật**: 21/11/2025
