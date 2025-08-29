# 📱 SoodAva Mobile Apps - GitHub Actions

## 🎯 **چطور کار می‌کنه:**

### **1. اتوماتیک Build:**
- **هر بار** که کد رو push کنید
- **هر دوشنبه** ساعت 2 صبح
- **دستی** از GitHub Actions

### **2. چه چیزی ساخته میشه:**
- ✅ **Android APK** (آماده نصب)
- ✅ **Android Project** (برای Android Studio)
- ✅ **iOS Project** (برای Xcode)

---

## 🚀 **مراحل استفاده:**

### **مرحله 1: Push کد**
```bash
git add .
git commit -m "Update for mobile apps build"
git push origin main
```

### **مرحله 2: GitHub Actions شروع میشه**
- **Android** build می‌شه (Ubuntu)
- **iOS** build می‌شه (macOS)
- **زمان:** 10-15 دقیقه

### **مرحله 3: دانلود**
- **GitHub Actions** → **Actions** tab
- **Artifacts** رو دانلود کنید
- **APK** برای Android
- **Project** برای iOS

---

## 📱 **نتیجه نهایی:**

### **Android:**
- **APK file** آماده نصب
- **Android Studio project** برای توسعه

### **iOS:**
- **Xcode project** آماده
- **App Store** ready

---

## ⚠️ **نکات مهم:**

### **1. هیچ کد Django تغییر نمی‌کنه:**
- ✅ **سایت** همچنان کار می‌کنه
- ✅ **PWA** همچنان کار می‌کنه
- ✅ **همه چیز** به حالت اول

### **2. فقط فایل‌های جدید:**
- `.github/workflows/build-mobile-apps.yml`
- `MOBILE_APPS_README.md`

### **3. هزینه:**
- **GitHub Actions:** رایگان (2000 دقیقه/ماه)
- **Build time:** حدود 15 دقیقه

---

## 🎉 **مزایا:**

1. **اتوماتیک** - هیچ کاری نمی‌کنید
2. **بدون نصب** - همه چیز روی GitHub
3. **هر دو platform** - iOS + Android
4. **بدون تغییر** کدهای Django
5. **رایگان** - GitHub Actions

---

## 📋 **مرحله بعدی:**

**فقط کد رو push کنید و منتظر باشید!**

**GitHub Actions** همه چیز رو انجام می‌ده! 🚀
