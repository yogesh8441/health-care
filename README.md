# 🏥 Hospital Management Dashboard

A modern, responsive hospital management dashboard built with Flask, TailwindCSS, and Chart.js. Features role-based access control for administrators and staff to manage beds, patients, and oxygen supplies in real-time.

## ✨ Features

### 🔐 Authentication & Authorization
- **Role-based login system** (Admin & Staff)
- **Secure session management**
- **Password hashing** with Werkzeug

### 🩺 Admin Panel
- **Dashboard overview** with real-time statistics
- **Bed management** with color-coded status indicators
- **Patient admission/discharge** tracking
- **Oxygen inventory** management
- **Staff activity logs**
- **Interactive charts** showing occupancy rates
- **Export functionality** (CSV/PDF ready)

### 👩‍⚕️ Staff Panel
- **Real-time bed status** updates
- **Quick patient admission/discharge**
- **Bed status changes** (Empty → Occupied → Cleaning → Maintenance)
- **Oxygen usage tracking**
- **Activity logging**
- **Mobile-responsive interface**

### 🎨 Modern UI/UX
- **Clean, hospital-grade design**
- **TailwindCSS** for responsive styling
- **Font Awesome icons**
- **Interactive charts** with Chart.js
- **Toast notifications**
- **Modal dialogs**
- **Mobile-first responsive design**

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hospital-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database with sample data**
   ```bash
   python seed_data.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔑 Demo Accounts

### Admin Account
- **Email:** `admin@hospital.com`
- **Password:** `admin123`
- **Access:** Full dashboard, bed management, staff management, reports

### Staff Account
- **Email:** `nurse@hospital.com`
- **Password:** `nurse123`
- **Access:** Ward management, patient care, bed status updates

## 📊 Database Schema

### Core Tables
- **Users** - Admin and staff accounts
- **Wards** - Hospital ward organization
- **Beds** - Individual bed tracking
- **Patients** - Patient information
- **Oxygen** - Oxygen cylinder inventory
- **ActivityLog** - User action tracking

### Bed Status Types
| Status | Color | Meaning |
|--------|-------|---------|
| Empty | 🟢 Green | Available for admission |
| Occupied | 🔴 Red | Patient admitted |
| Reserved | 🟡 Yellow | Booked for incoming patient |
| Cleaning | 🟠 Orange | Under cleaning/sanitization |
| Maintenance | ⚫ Gray | Under repair/maintenance |

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (easily replaceable with PostgreSQL/MySQL)
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5/CSS3** - Structure and styling
- **TailwindCSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Interactive functionality
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **Google Fonts (Inter)** - Typography

## 📱 Responsive Design

The dashboard is fully responsive and works seamlessly across:
- **Desktop** (1024px+)
- **Tablet** (768px - 1023px)
- **Mobile** (320px - 767px)

## 🔧 API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /admin/dashboard` - Admin dashboard
- `GET /staff/dashboard` - Staff dashboard
- `GET /api/dashboard_stats` - Real-time statistics

### Bed Management
- `POST /api/update_bed_status` - Update bed status
- `POST /api/admit_patient` - Admit new patient

## 🎯 Key Features Implemented

### ✅ Completed Features
- [x] **Role-based authentication system**
- [x] **Admin dashboard with statistics**
- [x] **Staff dashboard with bed management**
- [x] **Real-time bed status updates**
- [x] **Patient admission/discharge**
- [x] **Oxygen inventory tracking**
- [x] **Activity logging**
- [x] **Responsive design**
- [x] **Interactive charts**
- [x] **Modern UI with TailwindCSS**

### 🚧 Future Enhancements
- [ ] **WebSocket integration** for real-time updates
- [ ] **Advanced reporting** with PDF export
- [ ] **Staff scheduling** management
- [ ] **Patient medical records**
- [ ] **Notification system**
- [ ] **Multi-hospital support**
- [ ] **API documentation** with Swagger

## 🔒 Security Features

- **Password hashing** with Werkzeug
- **Session-based authentication**
- **Role-based access control**
- **CSRF protection ready**
- **SQL injection prevention** with SQLAlchemy ORM

## 📈 Sample Data

The seed script creates:
- **3 users** (1 admin, 2 staff)
- **6 wards** (General, ICU, Emergency, Pediatric, Maternity)
- **70+ beds** with various statuses
- **6 sample patients**
- **Oxygen inventory data**
- **Activity logs**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@hospital-dashboard.com or create an issue in the repository.

---

**Built with ❤️ for healthcare professionals**
