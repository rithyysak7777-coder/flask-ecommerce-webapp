# ឯកសារបច្ចេកទេស និងសេចក្តីសង្ខេបគម្រោង Flask E-Commerce Web Application

## ១. សេចក្តីផ្តើម និងគោលបំណងនៃគម្រោង (Project Overview)
កម្មវិធីវេបសាយនេះ គឺជាប្រព័ន្ធ **E-Commerce** និងប្រព័ន្ធគ្រប់គ្រងអ្នកប្រើប្រាស់ (**User Management System**) ដែលត្រូវបានបង្កើតឡើងដោយប្រើប្រាស់ **Python Flask Framework**, **Flask-SQLAlchemy**, **Flask-Migrate** និង **Jinja2 Template Engine**។ គម្រោងនេះបង្កើតឡើងសម្រាប់មុខវិជ្ជា Python ឆ្នាំទី៣ ឆមាសទី២ ឆ្នាំ២០២៦ នៅវិទ្យាស្ថាន SETEC។

កម្មវិធីនេះចែកចេញជា២ផ្នែកធំៗ៖
១. **Storefront (ផ្នែកខាងមុខសម្រាប់អតិថិជន)**៖ ស្វែងរកទំនិញ, ទិញទំនិញចូល Cart, បង្កើត Order, ការទូទាត់ប្រាក់ (Payment), ប្រព័ន្ធ Login/Register, និងការផ្ញើដំណឹង Order ភ្លាមៗទៅកាន់ **Telegram Channel**។
២. **Back-Office Admin (ផ្នែកខាងក្រោយសម្រាប់ Admin)**៖ គ្រប់គ្រងអ្នកប្រើប្រាស់ (User CRUD - Create, Read, Update, Delete), ពិនិត្យមើល Profile, និងផ្ទៀងផ្ទាត់សិទ្ធិ (Role)។

---

## ២. រចនាសម្ព័ន្ធ Folder និងឯកសារនៃគម្រោង (Directory & Project Structure)

```text
flask/
├── app.py                     # កូដមេ Flask (Routes, Models, Cart, Telegram Order Logic)
├── product.py                 # ទិន្នន័យទំនិញ (Product List) និង Function ស្វែងរកទំនិញ
├── memory_store.py            # Utility Read/Write ព័ត៌មានអតិថិជនទៅ JSON (load_users, save_users)
├── README.md                  # ឯកសារណែនាំទូទៅអំពីគម្រោង និងរបៀបដំណើរការ
│
├── data/                      # Folder រក្សាទុកទិន្នន័យ JSON
│   └── users.json             # ឯកសារ JSON ផ្ទុកព័ត៌មានគណនីអតិថិជន
│
├── douc/                      # Folder ផ្ទុកឯកសារបច្ចេកទេស
│   ├── DOCUMENTATION.md       # ឯកសារបច្ចេកទេសជាភាសាអង់គ្លេស
│   └── DOCUMENTATION_KH.md    # ឯកសារបច្ចេកទេសជាភាសាខ្មែរ (ភាសាខ្មែរ)
│
├── instance/                  # Folder ផ្ទុក Database Instance
│   └── mydb.sqlite3           # SQLite Database បង្កើតឡើងដោយ SQLAlchemy
│
├── migrations/                # Script Migration សម្រាប់ Update Database (Flask-Migrate)
│
├── static/                    # Static Web Assets (CSS, Images, JS)
│   ├── css/                   # ឯកសារ CSS សម្រាប់ Storefront
│   ├── admin css/             # Style ពិសេសសម្រាប់ Admin Dashboard និង Login
│   ├── images/                # រូបភាព Profile User និង រូបភាពទំនិញ
│   └── js/                    # Client-side JavaScript (AJAX Cart script)
│
└── templates/                 # Jinja2 HTML Templates
    ├── front/                 # ទំព័រ HTML សម្រាប់ Storefront (អតិថិជន)
    │   ├── share/             # Components រួម (Header, Footer, Navbar)
    │   ├── home.html          # ទំព័រដើម (Homepage)
    │   ├── products.html      # ទំព័របង្ហាញបញ្ជីទំនិញ
    │   ├── product_detail.html# ទំព័របង្ហាញព័ត៌មានលម្អិតនៃទំនិញ
    │   ├── cart.html          # ទំព័រកន្ត្រកទំនិញ (Shopping Cart)
    │   ├── checkout.html      # ទំព័របំពេញព័ត៌មានទិញទំនិញ
    │   ├── payment.html       # ទំព័របញ្ជាក់ការទូទាត់ប្រាក់
    │   ├── account.html       # ទំព័រ Profile របស់អតិថិជន
    │   ├── login.html         # ទំព័រចូលប្រើប្រាស់ (Login)
    │   ├── register.html      # ទំព័រចុះឈ្មោះ (Register)
    │   ├── reset_password.html# ទំព័រផ្លាស់ប្តូរពាក្យសម្ងាត់
    │   └── search.html        # ទំព័របង្ហាញលទ្ធផលស្វែងរក
    │
    └── admin/                 # ទំព័រ Back-office សម្រាប់ Admin
        ├── master.html        # Master Admin Layout Template
        ├── login.html         # ទំព័រ Admin Login (/admin/login)
        ├── dashboard/         # ទំព័រ Dashboard Overview
        ├── user/              # ផ្នែកគ្រប់គ្រង User (CRUD Operations)
        │   ├── user.html      # បញ្ជីបង្ហាញ User (Read)
        │   ├── add.html       # ទម្រង់បន្ថែម User ថ្មី (Create)
        │   ├── edit.html      # ទម្រង់កែប្រែទិន្នន័យ User (Update)
        │   ├── comfirm_delete.html # បង្អួចផ្ទៀងផ្ទាត់មុនលុប User (Delete)
        │   └── profile.html   # ទំព័របង្ហាញ Profile លម្អិតរបស់ User
        └── share/             # Components រួមសម្រាប់ Admin (Header, Footer, Sidebar, Navbar)
```

---

## ៣. បច្ចេកវិទ្យា និង Library ដែលបានប្រើប្រាស់ (Tech Stack)

- **Backend Framework**: Python Flask (v3.x)
- **Database Systems**: 
  - **SQLite Database** (`mydb.sqlite3`) ប្រើជាមួយ **Flask-SQLAlchemy ORM** សម្រាប់គ្រប់គ្រងព័ត៌មាន Admin/User។
  - **JSON Storage** (`data/users.json`) ប្រើជាមួយ `memory_store.py` សម្រាប់រក្សាទុកព័ត៌មានគណនីអតិថិជន។
- **Database Migration**: `Flask-Migrate` (Alembic integration សម្រាប់ Update គ្រោងឆ្អឹង DB)
- **State Management**:
  - **HTTP Cookies (`cart_list`)**: ប្រើប្រាស់សម្រាប់រក្សាទុកបញ្ជីទំនិញក្នុង Shopping Cart លើ Browser។
  - **Flask Session**: រក្សាទុក Session Login របស់ User និងទិន្នន័យបណ្តោះអាសន្នពេល Checkout/Payment។
- **External API Integration**: Telegram Bot API (`requests` package) សម្រាប់ផ្ញើសារដំណឹង Order ទៅ Telegram Channel `@RACTZ_STORE` ដោយស្វ័យប្រវត្តិ។
- **Frontend & Styling**: HTML5, CSS3, JavaScript (AJAX/XMLHttpRequest), Jinja2 Template Inheritance (`master.html`, header, footer, navbar)។

---

## ៤. រចនាសម្ព័ន្ធ Folder និងតួនាទីលម្អិតនៃសមាសភាគនីមួយៗ (Detailed Components Guide)

### 🛠️ ឯកសារកូដមេ (Core Application Files)
- 📄 **`app.py`**: **បេះដូងនៃកម្មវិធី (Main Entry Point)** — ផ្ទុកការកំណត់ Flask Server, ការតភ្ជាប់ SQLite Database, SQLAlchemy Models (`User`), Routes Storefront ទាំងអស់, ក្បួនគណនា Cart, Telegram Order Broadcast, ការផ្ទៀងផ្ទាត់សិទ្ធិ Admin (`@login_required`), Admin Login/Logout, និង Admin User CRUD Routes។
- 📄 **`product.py`**: **អ្នកគ្រប់គ្រងទិន្នន័យទំនិញ (Catalog Manager)** — ផ្ទុក Array បញ្ជីទំនិញ និង Function ជំនួយស្វែងរក (`get_product_by_id()`, `get_product_by_category()`)។
- 📄 **`memory_store.py`**: **អ្នកគ្រប់គ្រង JSON Storage** — ផ្ទុក Function Read/Write (`load_users()`, `save_users()`) សម្រាប់គ្រប់គ្រងគណនីអតិថិជនក្នុង `data/users.json`។

### 📁 Folder ទិន្នន័យ និង Database (Data & Database Directories)
- 📁 **`data/`**: រក្សាទុកឯកសារ JSON Local (`users.json` សម្រាប់គណនីអតិថិជន និងប្រវត្តិទិញ)។
- 📁 **`instance/`**: ផ្ទុកឯកសារ `mydb.sqlite3` ដែលជា SQLite Database គ្រប់គ្រងដោយ SQLAlchemy។
- 📁 **`migrations/`**: បង្កើតដោយ `Flask-Migrate` សម្រាប់កត់ត្រាប្រវត្តិ Migration នៃ Database Schema។

### 🎨 ឯកសារ Static Assets (`static/`)
- 📁 **`static/css/`**: ឯកសារ CSS Style (`style.css`) សម្រាប់ដេគ័រ Storefront អតិថិជន។
- 📁 **`static/admin css/`**: ឯកសារ CSS (`logincss.css`, `adminstyle.css`) សម្រាប់ Admin Dashboard និង Login Page។
- 📁 **`static/images/`**: Folder សម្រាប់ Upload រូបភាព Profile User និងរូបភាពទំនិញ/Icon។
- 📁 **`static/js/`**: ឯកសារ Client-side JavaScript សម្រាប់រៀបចំ Interactivity និង Update Cart តាម AJAX។

### 🖼️ Jinja2 HTML Templates (`templates/`)
- 📁 **`templates/front/`**: **ទំព័រ HTML សម្រាប់ Storefront (អតិថិជន)**
  - **ទំព័រទូទៅ**: `home.html`, `products.html`, `product_detail.html`, `cart.html`, `checkout.html`, `payment.html`, `account.html`, `search.html`។
  - **ទំព័រ Login/Register**: `login.html`, `register.html`, `reset_password.html`។
  - **Component រួម (`templates/front/share/`)**: `header.html`, `footer.html`, `navbar.html`។
- 📁 **`templates/admin/`**: **ទំព័រ HTML សម្រាប់ Admin Panel**
  - **Layout មេ**: `master.html` (Master wrapper template), `login.html` (ទំព័រ Admin Login)។
  - **គ្រប់គ្រង User CRUD (`templates/admin/user/`)**: `user.html` (Read), `add.html` (Create), `edit.html` (Update), `comfirm_delete.html` (Delete), `profile.html` (View profile)។
  - **Component រួម (`templates/admin/share/`)**: `header.html`, `footer.html`, `navbar.html`, `sidebar.html`, `script.html`។

---

## ៥. ការពន្យល់លម្អិតអំពី Feature និង Logic នីមួយៗ (Core Features & Implementation Logic)

### ក. ប្រព័ន្ធគ្រប់គ្រង Cart និង Cookie Management (`cart`)
- កម្មវិធីប្រើប្រាស់ Cookie ឈ្មោះ `cart_list` ដើម្បីរក្សាទុកទំនិញដែលអតិថិជនបានជ្រើសរើសក្នុងទម្រង់ JSON array: `[{"id": "1", "qty": 2}]`។
- **Logic រៀបចំ Cart**:
  - បើមានទំនិញជាន់គ្នា វានឹងធ្វើការបូកបញ្ចូលចំនួន Quantity (Merge duplication)។
  - គណនា **Subtotal**, **Discount (10%)**, **Shipping Fee** ($0 ប្រសិនបើទិញលើសពី $150 បើមិនដូច្នេះទេ $12), និង **Tax (7%)**។
  - ទ្រទ្រង់ការ Update ទិន្នន័យតាមរយៈ **AJAX (XMLHttpRequest)** ដោយមិនបាច់ Reload ទំព័រ។

### ខ. ប្រព័ន្ធទូទាត់ប្រាក់ និង Telegram Notification (`checkout` & `payment`)
- នៅពេលអតិថិជនពេញបំពេញព័ត៌មាន Checkout (ឈ្មោះ, អាសយដ្ឋាន, លេខទូរស័ព្ទ, វិធីសាស្ត្រទូទាត់)៖
  1. កម្មវិធីបង្កើត **Order ID** ផ្អែកលើកាលបរិច្ឆេទ និងពេលវេលា (ឧទាហរណ៍៖ `20260820220649`)។
  2. រៀបចំទម្រង់សារជា HTML Format ដែលមានលម្អិតពីអតិថិជន និងបញ្ជីមុខទំនិញ។
  3. ផ្ញើសារនោះទៅកាន់ Telegram Channel `@RACTZ_STORE` តាមរយៈ Telegram Bot API: `https://api.telegram.org/bot<TOKEN>/sendMessage`។
  4. រក្សាទុកព័ត៌មាន Order ចូល Session ស្របពេលលុប Cookie `cart_list` ចោល រួច Redirect ទៅកាន់ទំព័រ Payment។

### គ. ប្រព័ន្ធគ្រប់គ្រងអ្នកប្រើប្រាស់ និងការផ្ទៀងផ្ទាត់សិទ្ធិ Admin (Admin User CRUD & Security System)
- **ប្រព័ន្ធផ្ទៀងផ្ទាត់សិទ្ធិ Admin & Session Lifetime**:
  - **ការពារ Route ជាមួយ Decorator (`@login_required`)**៖ រាល់ Route របស់ Admin (`/admin/dashboard`, `/admin/user`, `/admin/order`, `/admin/product`...) ត្រូវបានការពារដោយ `@login_required` ដើម្បីពិនិត្យមើល `session.get('is_login')`។ ប្រសិនបើពុំទាន់ Login ទេ កម្មវិធីនឹង Redirect ទៅទំព័រ `/admin/login` ដោយស្វ័យប្រវត្តិ។
  - **Admin Login (`POST /admin/login`)**៖ ស្វែងរកគណនីក្នុង Database រួចទាញយកទិន្នន័យតាមរយៈ `dict(result._mapping)` យ៉ាងមានសុវត្ថិភាព ព្រមទាំងផ្ទៀងផ្ទាត់ Password តាម `check_password_hash`។
  - **រក្សាទុក Session រយៈពេល ១ថ្ងៃ (1-Day Persistent Session)**៖ កំណត់ `session.permanent = True` នៅពេល Login ជោគជ័យ ដែលធ្វើឲ្យ Session រក្សាទុកបាន 24 ម៉ោង (`PERMANENT_SESSION_LIFETIME = timedelta(days=1)`) ទោះបីជាបិទ Browser ក៏ដោយ។
  - **Admin Logout (`GET /admin/logout`)**៖ លុបទិន្នន័យ Session ចោល (`session.clear()`) រួច បញ្ជូនត្រឡប់ទៅទំព័រ `/admin/login`។

- **Database Model `User`** (ក្នុង SQLite via SQLAlchemy):
  - `id`: Primary Key Auto-increment
  - `username`: ឈ្មោះអ្នកប្រើប្រាស់
  - `email`: អ៊ីមែល (Unique)
  - `password`: ពាក្យសម្ងាត់ (Hashed String)
  - `role`: សិទ្ធិប្រើប្រាស់ (Admin / User)
  - `profile`: រូបភាព Profile (Default: `/static/images/default.png`)
  - `status`: ស្ថានភាព (Active / Inactive)
- **ប្រព័ន្ធគ្រប់គ្រងរូបភាព Profile និងសុវត្ថិភាព Path (Dual-Image & Path Security)**:
  - **កំណត់ទំហំ Upload អតិបរមា 5MB**៖ ពិនិត្យមើលទំហំរូបភាព Upload មិនឲ្យលើសពី 5MB។
  - **ការបង្កើតរូបភាពជា ២ Version ស្វ័យប្រវត្តិ**៖
    - **Version 1 (Original 100% Quality)**៖ រក្សាទុកជា `static/images/{user_id}_org_{username}.{ext}` (គុណភាពដើម 100% សម្រាប់បង្ហាញក្នុងទំព័រ Detail `profile.html` និង Edit `edit.html`)។
    - **Version 2 (Thumbnail -80% Quality Reduction)**៖ បង្រួមទំហំមកត្រឹម 150x150px និងបន្ថយគុណភាពមកត្រឹម 20% (កាត់បន្ថយ 80%) រក្សាទុកជា `static/images/{user_id}_thum_{username}.jpg` ដោយប្រើប្រាស់ Pillow (សម្រាប់បង្ហាញក្នុងបញ្ជី User Directory `user.html`)។
  - **Route បិទបាំង Path រូបភាព (`user_photo`)**៖ ប្រើប្រាស់ Route `@app.get('/admin/user/photo/<int:user_id>/<string:photo_type>')` ដើម្បីទាញយករូបភាពដោយមិនបង្ហាញ Path ផ្ទាល់ក្នុង Browser HTML Source Code។

- **មុខងារ CRUD**:
  - **Read/List Users** (`GET /admin/user`)៖ បាញ់ SQL Query រកមើល User ទាំងអស់តាមរយៈ `text("SELECT * FROM user")` រួច Mapping ទៅកាន់ Template ដោយបង្ហាញរូបភាព Thumbnail (`thum`)។
  - **Create/Add User** (`POST /admin/user/add`)៖ ទទួល Form data បង្កើត Instance នៃ `User` Model បង្កើតរូបភាព ២ version (Original & Thumbnail) រួច Save ចូល SQLite តាម `db.session.add()` និង `db.session.commit()`។
  - **Update/Edit User** (`POST /admin/user/edit`)៖ ស្វែងរក User តាម ID រួច Update ព័ត៌មាន និងរូបភាព Profile ថ្មី។
  - **Delete User** (`POST /admin/user/delete`)៖ មានទំព័រ Confirm Delete (`comfirm_delete.html`) មុននឹងលុបចេញពី Database តាម `db.session.delete()` ព្រមទាំងលុបរូបភាព Profile ទាំងអស់ (Original & Thumbnail) ចេញពី Directory `static/images` ដោយស្វ័យប្រវត្តិ។

---

## ៦. របៀប Run កម្មវិធី (How to Run Project)

១. **ដំឡើង Packages ដែលចាំបាច់**:
   ```bash
   pip install flask flask-sqlalchemy flask-migrate requests
   ```

២. **រៀបចំ Database Migration (ប្រសិនបើ DB មិនទាន់មាន)**:
   ```bash
   flask db init
   flask db migrate -m "Initial Migration"
   flask db upgrade
   ```

៣. **ដំណើរការ Server**:
   ```bash
   python app.py
   ```
   កម្មវិធីនឹងដំណើរការលើ `http://127.0.0.1:5000/`។
