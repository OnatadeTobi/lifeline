# Lifeline - Blood Donation Management System

A comprehensive Django-based blood donation platform that connects hospitals with blood donors to facilitate urgent blood requests.

## 🚀 Features

### Core Functionality
- **Multi-User System**: Support for Donors, Hospital Staff, and System Administrators
- **Blood Request Management**: Hospitals can create and manage urgent blood requests
- **Donor Matching**: Automatic matching of compatible blood types and locations
- **Real-time Notifications**: Email-based communication system
- **Location-based Services**: State and Local Government area management
- **Admin Portal**: Role-based admin interface with django-unfold

### Admin Features
- **Dynamic Admin Interface**: Adapts based on user role (Superuser vs Hospital User)
- **Comprehensive Data Management**: Full CRUD operations with advanced filtering
- **Export Functionality**: CSV export for all data types
- **Bulk Operations**: Mass actions for common tasks
- **Statistics Dashboard**: Real-time metrics and counts
- **Permission-based Access**: Granular control over user capabilities

## 🏗️ Architecture

### Models
- **User**: Extended Django user with roles and hospital association
- **Hospital**: Hospital profiles with location and service areas
- **Donor**: Donor profiles with blood type and availability
- **BloodRequest**: Urgent blood requests from hospitals
- **DonorResponse**: Tracking donor responses to requests
- **Location Models**: State and Local Government management

### Admin System
- **Base Admin Classes**: Common functionality for all admin interfaces
- **Superuser Admin**: Full system access with all features
- **Hospital Admin**: Restricted access to hospital-specific data
- **Dynamic Registration**: Admin classes adapt based on user type

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lifeline
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   # On Windows
   .\env\Scripts\Activate.ps1
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   EMAIL_HOST=your-smtp-host
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email
   EMAIL_HOST_PASSWORD=your-password
   DEFAULT_FROM_EMAIL=noreply@lifeline.com
   FRONTEND_URL=http://localhost:3000
   ```

5. **Database Setup**
   ```bash
python manage.py migrate
   ```

6. **Load Location Data**
   ```bash
python manage.py loaddata fixtures/lagos_locations.json
   ```

7. **Setup Admin Permissions**
   ```bash
   python manage.py setup_admin_permissions
   ```

8. **Create Superuser**
   ```bash
python manage.py createsuperuser
   ```

9. **Run Development Server**
   ```bash
python manage.py runserver
   ```

## 👥 User Types & Access

### Superuser (System Administrator)
**Full system access with ability to:**
- View and manage ALL hospitals, blood requests, donor responses, and accounts
- Access system settings and configurations
- Manage all user accounts and permissions
- Full CRUD operations on all models
- Export data across entire system
- Access comprehensive statistics and analytics

**Features:**
- Complete model management with advanced filtering
- Bulk operations (activate/deactivate, verify/unverify, etc.)
- CSV export functionality
- Inline editing for related models
- Date hierarchies and advanced search
- Custom admin actions for common operations

### Hospital User (Hospital Staff)
**Restricted access to own hospital only:**
- **Can access:**
  - Own hospital's blood requests and donor responses
  - All donor information (to find compatible donors)
  - Own hospital profile (limited editing)
  - Location data (view only)
  - User management for hospital staff

- **Cannot access:**
  - Other hospitals' data
  - System-wide settings
  - User management for other hospitals
  - Administrative functions

- **Permissions:**
  - View/Add/Edit own hospital's blood requests
  - View/Add/Edit donor information
  - View/Edit own hospital profile (limited fields)
  - Automatic filtering ensures data isolation

## 🎛️ Admin Interface Features

### General Features (Both User Types)
- **Search & Filtering**: Advanced search across all text fields
- **Date Filtering**: Filter by creation/update dates
- **Status Indicators**: Color-coded status displays
- **Statistics**: Real-time counts and metrics
- **Responsive Design**: Works on all device sizes

### Superuser-Specific Features
- **Export to CSV**: Download data for analysis
- **Bulk Actions**: Mass operations on selected records
- **Advanced Permissions**: Full control over user capabilities
- **System Monitoring**: Track all activities across hospitals
- **Data Analytics**: Comprehensive statistics and reports

### Hospital User-Specific Features
- **Data Isolation**: Automatic filtering to hospital data only
- **Limited Actions**: Appropriate permissions for hospital staff
- **Focus on Operations**: Streamlined interface for daily tasks
- **Quick Actions**: Common operations easily accessible

## 📊 Admin Models & Features

### User Management
- **List Display**: Email, role, verification status, activity status
- **Filters**: Role, verification status, activity, creation date
- **Search**: Email, username, first/last name
- **Actions**: Activate/Deactivate, Verify users
- **Fieldsets**: Personal info, account status, permissions, timestamps

### Hospital Management
- **List Display**: Name, email, phone, location, verification status
- **Filters**: Verification status, location, creation date
- **Search**: Name, email, phone, address, location
- **Actions**: Verify/Unverify hospitals
- **Inline**: Related hospital staff
- **Statistics**: Request count, donor count

### Donor Management
- **List Display**: Email, phone, blood type, availability, eligibility
- **Filters**: Blood type, availability, location, creation date
- **Search**: Email, name, phone, blood type
- **Actions**: Activate/Deactivate, Mark available, Update donation date
- **Color Coding**: Eligibility status with visual indicators

### Blood Request Management
- **List Display**: ID, hospital, blood type, status, responses count
- **Filters**: Status, blood type, hospital, creation date
- **Search**: Hospital name, contact phone, notes, blood type
- **Actions**: Mark fulfilled/cancelled/open
- **Inline**: Donor responses
- **Status Tracking**: Color-coded status indicators

### Donor Response Management
- **List Display**: Request, donor email, blood type, fulfillment status
- **Filters**: Fulfillment status, acceptance date, blood type
- **Search**: Donor email, request details
- **Actions**: Mark fulfilled/pending
- **Tracking**: Response timeline and status

### Location Management
- **States**: Name, code, statistics (hospitals, donors, LGs)
- **Local Governments**: Name, state, statistics (hospitals, donors)
- **Export**: CSV export for location data
- **Statistics**: Real-time counts and relationships

## 🔧 Configuration

### Django Settings
The application uses django-unfold for the admin interface with the following configuration:

```python
UNFOLD = {
    "SITE_TITLE": "Lifeline Admin Portal",
    "SITE_HEADER": "Lifeline Admin",
    "SITE_SUBHEADER": "Welcome to Lifeline Admin Portal",
    "SITE_URL": "/admin/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
}
```

### Permissions Setup
Run the setup command to create permission groups:
```bash
python manage.py setup_admin_permissions
```

This creates:
- **Hospital Admin Group**: Limited permissions for hospital staff
- **Super Admin Group**: Full system permissions

## 🚀 Usage Examples

### Creating a Hospital Admin User
```python
from apps.accounts.models import User
from django.contrib.auth.models import Group

# Create hospital user
user = User.objects.create_user(
    email="admin@hospital.com",
    username="hospital_admin",
    role="HOSPITAL",
    is_verified=True
)

# Assign to hospital admin group
hospital_group = Group.objects.get(name="Hospital Admin")
user.groups.add(hospital_group)
```

### Creating a Superuser
```bash
python manage.py createsuperuser
```

### Accessing Admin Interface
1. Navigate to `http://localhost:8000/admin/`
2. Login with your credentials
3. The interface will automatically adapt based on your user type

### Managing Blood Requests (Hospital Users)
1. Go to "Blood Requests" section
2. Click "Add Blood Request"
3. Fill in blood type, contact phone, and notes
4. Save to create the request
5. Monitor donor responses in the inline section

### Managing Donors (Hospital Users)
1. Go to "Donors" section
2. Search for compatible blood types
3. Filter by location and availability
4. Use bulk actions to update donor status

### System Administration (Superusers)
1. Access all models and data
2. Use export functionality for reports
3. Monitor system-wide statistics
4. Manage user permissions and groups

## 🔒 Security Features

- **Role-based Access Control**: Users only see data they're authorized to access
- **Automatic Filtering**: Hospital users automatically filtered to their hospital's data
- **Permission Validation**: All operations checked against user permissions
- **Secure Admin Interface**: Built on Django's secure admin framework
- **CSRF Protection**: Built-in protection against cross-site request forgery

## 📈 Monitoring & Analytics

### Available Statistics
- **Hospital Metrics**: Request count, response rate, fulfillment rate
- **Donor Metrics**: Availability, eligibility, response rate
- **System Metrics**: Total users, active hospitals, successful matches
- **Location Analytics**: Coverage by state/LGA, service distribution

### Export Capabilities
- **CSV Export**: All models support CSV export
- **Filtered Export**: Export only filtered/searched data
- **Bulk Operations**: Mass updates and actions

## 🛠️ Development

### Adding New Features
1. Create model in appropriate app
2. Create admin class inheriting from base admin classes
3. Add permissions to setup command
4. Update documentation

### Customizing Admin Interface
1. Extend base admin mixins
2. Override methods for custom behavior
3. Add custom actions and filters
4. Test with different user types

## 📝 API Integration

The admin interface works alongside the REST API:
- Admin for data management
- API for mobile/web applications
- Shared models and permissions
- Consistent data validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the admin interface help sections
- Contact the development team
- Create an issue on the repository

---

**Lifeline** - Connecting lives through blood donation management.