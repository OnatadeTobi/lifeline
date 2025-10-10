# Lifeline Admin Usage Guide

This guide explains how to use the comprehensive admin system for the Lifeline blood donation platform.

## 🚀 Getting Started

### 1. Access the Admin Interface
- Navigate to `http://localhost:8000/admin/`
- Login with your credentials
- The interface automatically adapts based on your user type

### 2. User Types & Access Levels

#### Superuser (System Administrator)
- **Access**: Full system access to all data and features
- **Features**: Complete CRUD operations, bulk actions, export functionality
- **Use Case**: System management, data analysis, user management

#### Hospital User (Hospital Staff)
- **Access**: Limited to hospital-specific data
- **Features**: Manage own hospital's requests, view all donors, limited editing
- **Use Case**: Daily operations, blood request management

## 📊 Admin Interface Features

### Navigation & Layout
- **Sidebar Navigation**: Organized by app with model groupings
- **Search Bar**: Global search across all models
- **User Menu**: Profile, settings, logout options
- **Responsive Design**: Works on desktop, tablet, and mobile

### List Views
- **Sortable Columns**: Click column headers to sort
- **Search**: Use the search box to find specific records
- **Filters**: Use sidebar filters to narrow down results
- **Bulk Actions**: Select multiple records for batch operations

### Detail Views
- **Organized Fieldsets**: Fields grouped logically
- **Inline Editing**: Related models displayed inline
- **Readonly Fields**: System fields automatically protected
- **Save Options**: Save and continue, save and add another

## 🏥 Hospital Management

### For Superusers
1. **View All Hospitals**
   - Go to "Hospitals" section
   - See all hospitals with verification status
   - Use filters to find specific hospitals

2. **Hospital Verification**
   - Select hospitals to verify/unverify
   - Use bulk actions for multiple hospitals
   - Track verification status changes

3. **Hospital Statistics**
   - View request counts per hospital
   - Monitor donor engagement
   - Export data for analysis

### For Hospital Users
1. **Edit Hospital Profile**
   - Update hospital information
   - Modify service locations
   - Cannot change verification status

2. **View Hospital Statistics**
   - See own hospital's request count
   - Monitor response rates
   - Track fulfillment metrics

## 🩸 Blood Request Management

### Creating Blood Requests
1. **Navigate to Blood Requests**
   - Click "Add Blood Request"
   - Fill in required fields:
     - Blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)
     - Contact phone number
     - Additional notes (optional)

2. **Request Status Tracking**
   - **Open**: New request, waiting for responses
   - **Matched**: Donors have responded
   - **Fulfilled**: Request completed
   - **Cancelled**: Request cancelled

### Managing Responses
1. **View Donor Responses**
   - Responses appear inline on request detail page
   - See donor contact information
   - Track response timeline

2. **Mark as Fulfilled**
   - Select responses to mark as fulfilled
   - Use bulk actions for multiple responses
   - Track completion status

### Bulk Operations
- **Mark as Fulfilled**: Complete multiple requests
- **Mark as Cancelled**: Cancel multiple requests
- **Export to CSV**: Download request data

## 👥 Donor Management

### Donor Information
1. **View Donor Details**
   - Contact information
   - Blood type and availability
   - Service locations
   - Donation history

2. **Eligibility Status**
   - **Eligible**: Can donate (green indicator)
   - **Not Eligible**: On cooldown period (red indicator)
   - Based on 56-day donation interval

### Managing Donors
1. **Update Availability**
   - Mark donors as available/unavailable
   - Update last donation date
   - Modify service locations

2. **Bulk Operations**
   - Activate/Deactivate multiple donors
   - Mark as available
   - Update donation dates

### Search & Filter
- **Search**: By email, name, phone, blood type
- **Filter**: By blood type, availability, location
- **Sort**: By creation date, last donation, etc.

## 👤 User Management

### User Types
- **DONOR**: Blood donors
- **HOSPITAL**: Hospital staff
- **ADMIN**: System administrators

### User Operations
1. **Account Management**
   - Activate/Deactivate accounts
   - Verify email addresses
   - Reset passwords

2. **Role Management**
   - Assign roles to users
   - Manage permissions
   - Group assignments

### Bulk Actions
- **Activate Users**: Enable multiple accounts
- **Deactivate Users**: Disable multiple accounts
- **Verify Users**: Mark emails as verified

## 📍 Location Management

### States & Local Governments
1. **View Locations**
   - Browse by state
   - See local government areas
   - View statistics per location

2. **Location Statistics**
   - Hospital count per area
   - Donor count per area
   - Service coverage metrics

### Export Functionality
- **CSV Export**: Download location data
- **Filtered Export**: Export specific areas
- **Statistics Export**: Include counts and metrics

## 🔧 Advanced Features

### Export Functionality
1. **CSV Export**
   - Select records to export
   - Choose export format
   - Download filtered data

2. **Export Options**
   - All fields or selected fields
   - Include/exclude timestamps
   - Custom date ranges

### Bulk Operations
1. **Selection Methods**
   - Individual record selection
   - Select all on page
   - Select all matching filters

2. **Available Actions**
   - Status updates
   - Bulk edits
   - Mass deletions (superusers only)

### Search & Filtering
1. **Search Fields**
   - Text-based search across multiple fields
   - Case-insensitive matching
   - Partial word matching

2. **Filter Options**
   - Date range filtering
   - Status-based filtering
   - Relationship-based filtering

## 🎯 Best Practices

### For Hospital Users
1. **Daily Operations**
   - Check new blood requests first
   - Monitor donor responses
   - Update request statuses promptly

2. **Data Management**
   - Keep hospital profile updated
   - Verify donor information
   - Track fulfillment rates

### For Superusers
1. **System Monitoring**
   - Regular user management
   - Hospital verification process
   - System-wide analytics

2. **Data Analysis**
   - Export data for reporting
   - Monitor system performance
   - Track usage patterns

## 🚨 Troubleshooting

### Common Issues
1. **Permission Errors**
   - Check user group assignments
   - Verify role permissions
   - Contact system administrator

2. **Data Not Showing**
   - Check user hospital assignment
   - Verify data filters
   - Ensure proper permissions

3. **Export Issues**
   - Check browser download settings
   - Verify data selection
   - Try smaller data sets

### Getting Help
1. **Documentation**
   - Check this guide
   - Review model documentation
   - Check Django admin docs

2. **Support**
   - Contact system administrator
   - Report bugs through proper channels
   - Check system logs for errors

## 📈 Analytics & Reporting

### Key Metrics
1. **Hospital Metrics**
   - Request volume
   - Response rates
   - Fulfillment rates

2. **Donor Metrics**
   - Active donor count
   - Availability rates
   - Response engagement

3. **System Metrics**
   - Total users
   - Active hospitals
   - Successful matches

### Reporting Tools
1. **Built-in Statistics**
   - Real-time counts
   - Status breakdowns
   - Trend indicators

2. **Export for Analysis**
   - CSV data export
   - Custom date ranges
   - Filtered datasets

---

## 🎉 Conclusion

The Lifeline admin system provides comprehensive tools for managing blood donation operations. Whether you're a hospital staff member managing daily requests or a system administrator overseeing the entire platform, the interface adapts to your needs and provides the tools necessary for effective blood donation management.

For additional support or feature requests, please contact the development team or refer to the main project documentation.

