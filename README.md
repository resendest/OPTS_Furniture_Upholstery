# Order Processing and Tracking System (OPTS)

Created by Wentworth students Tyler Resendes and Samuel Gjencaj for their Summer 2025 MGMT 5510 - CIS Senior Capstone course.

The OPTS is a web-based platform for Lousso Designs, a custom upholstery business in the Greater Boston area, to manage custom upholstery orders from creation to delivery.  
The OPTS enables staff to create orders with project-specific milestones, track production progress, and generate work order PDFs.  
Clients can log in to view their order status and download documentation.  
The system supports role-based access, milestone customization, QR code scanning for workflow updates, and automated email notifications.

**Disclaimer:** This project is currently intended and optimized for use by Lousso Designs. Customization or deployment for other businesses may require additional configuration or development. 

## Features

- **Order Creation:** Staff can create new orders, enter customer info, and select only the milestones needed for each project.
- **Custom Milestones:** Each order has its own set of milestones that are chosen at order creation for project customization.
- **Scan & Update:** Staff can update milestone status via a QR-supported scan page.
- **My Orders:** Clients can view order details, milestone history, and download client-facing PDFs that exclude QR codes.
- **Master Dashboard:** Staff can view order details for all projects, their milestone historys, and download PDFs that include QR codes for staff use.
- **Email Notifications:** Sends registration and status emails to clients.
- **PDF Generation:** Generates internal and client-facing work order PDFs.
- **User Roles:** Staff and client logins, with role-based access.

## Tech Stack

- **Backend:** Python, Flask (framework)
- **Frontend:** HTML/CSS (Jinja2, Bootstrap), JavaScript
- **Database:** PostgreSQL
- **Application Server:** Gunicorn (production)
- **Hosting Platform** Render (render.com)
- **PDF Generation:** ReportLab (python library)
- **QR Code Generation:** qrcode (python library)
- **Email Processing:** Flask-Mail, Gmail SMTP

## Key Files

- `app.py` — Main Flask app
- `backend/shop_routes.py` — Order, scan, and dashboard routes
- `backend/order_processing.py` — Order and PDF logic and creation.
- `backend/db.py` — Database connection and helpers
- `templates/` — Folder for all HTML/CSS templates
- `sql/v3_lousso_opts_schema.sql` — Database schema

## User Privileges

- **Staff:** Log in, create orders, select milestones, and manage progress.
- **Clients:** Log in to view their orders and download PDFs.
- **Scan Page:** Use QR code or direct link to update milestone status as work progresses.

## Customizing Milestones

- Edit the master milestone list in `app.py` (or move to DB for dynamic management).
- Only selected milestones are saved per order and shown on scan/detail pages.

---

## Instructions

This README provides two sets of instructions:
- **For Professors/Academic Evaluation** - Quick assessment and optional testing
- **For Production Deployment** - Complete live deployment on Render

---

## For Professors/Academic Evaluation


### Option 1: Code Review Only (Recommended)
**For evaluating code structure, logic, and design:**
- All source files included in this submission
- Database schema available in `sql/v3_lousso_opts_schema.sql`
- Architecture and business logic documented throughout codebase
- **No setup required** - just review the files

**Demo video can be found in submission**

### Option 2: Local Testing Setup (Optional)
**If you want to run the application locally for hands-on evaluation:**

#### Prerequisites:
- Python 3.8+ installed
- PostgreSQL installed and running locally

#### Quick Setup (10 minutes):
1. **Create local database:**
   ```sql
   -- Connect to PostgreSQL as admin user
   psql -U postgres
   
   -- Create database and user
   CREATE DATABASE opts;
   CREATE USER opts_user WITH PASSWORD 'test_password';
   GRANT ALL PRIVILEGES ON DATABASE opts TO opts_user;
   \q
   ```

2. **Configure environment:**
   ```bash
   # Copy template
   cp .env.example .env
   ```
   
   **Edit `.env` with these test values:**
   ```bash
   DATABASE_URL=postgresql://opts_user:test_password@localhost:5432/opts
   SECRET_KEY=test_key_for_academic_evaluation_32chars
   BASE_URL=http://localhost:5000
   
   # Email settings (optional - app works without these)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_USERNAME=test@example.com
   EMAIL_PASSWORD=dummy_password
   EMAIL_DEFAULT_SENDER="Test <test@example.com>"
   ```

3. **Install and run:**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

4. **Access application:**
   - Visit: http://localhost:5000/admin_setup
   - Create test admin account
   - Explore all features

#### What Works Locally:
- Complete order management system
- User authentication and role-based access
- Database operations and milestone tracking
- PDF generation and QR code creation
- All web interfaces and forms
- Email notifications (requires Gmail App Password setup - see production instructions)

---

## For Production Deployment

**Complete instructions for deploying a live version on Render hosting platform:**

### Prerequisites:
- GitHub account
- Gmail account (for email notifications)
- Render account (free tier available at render.com)

### Deployment Options:

**Option 1: GitHub Repository (Recommended)**
- Fork this repository to your GitHub account
- Best for version control and automatic updates

**Option 2: Zip File Upload**
1. Create new repository on [GitHub](https://github.com)
2. Upload all project files from the zip submission
3. Commit changes to your new repository

### Step 1: Set Up Gmail for Email Notifications
**The application sends registration emails to clients. Choose one option:**

#### Option A: Use Existing Gmail Account
1. **Enable 2-Factor Authentication** (required for App Passwords)
2. **Generate App Password:**
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Search for **App Passwords** under Security
   - Generate password for "Mail" application
   - **Save the 16-character password** (format: `abcd efgh ijkl mnop`)

#### Option B: Create Business Gmail Account
1. Create new Gmail account (e.g., `yourbusiness.orders@gmail.com`)
2. Enable 2-Factor Authentication
3. Generate App Password (follow Option A steps)

**Required Information to Collect:**
- Gmail address for `EMAIL_USERNAME`
- 16-character App Password for `EMAIL_PASSWORD`
- Display name for `EMAIL_DEFAULT_SENDER` (e.g., `"Your Business <email@gmail.com>"`)

**Important:** Regular Gmail passwords will NOT work - you must use App Passwords

### Step 2: Deploy to Render

#### 2.1: Create Database
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database:
   - **Name:** `opts-database`
   - **Plan:** Free (for testing) or paid (for production)
   - **Region:** Choose closest to your users
4. Click **"Create Database"**
5. **Copy the Internal Database URL** - save this for the web service setup

#### 2.2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure service:
   - **Name:** `opts-your-business-name`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (for testing) or paid (for production)

#### 2.3: Configure Environment Variables
**Add these environment variables BEFORE deploying:**

**Database & Security:**
- `DATABASE_URL` = Internal Database URL from Step 2.1
- `SECRET_KEY` = Generate 32+ character random string

**Email Configuration:**
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_PORT` = `587`
- `EMAIL_USE_TLS` = `true`
- `EMAIL_USERNAME` = Your Gmail address
- `EMAIL_PASSWORD` = Your Gmail App Password (16 characters)
- `EMAIL_DEFAULT_SENDER` = `"Your Business <youremail@gmail.com>"`

**How to Add Variables:**
1. Scroll to "Environment Variables" section on the web service setup page
2. Click "Add Environment Variable" for each one
3. Enter exact variable name and corresponding value
4. Verify `DATABASE_URL` starts with `postgresql://`

#### 2.4: Deploy and Configure URL
1. Click **"Create Web Service"**
2. Wait for initial deployment (5-10 minutes)
3. **Copy your app URL** from Render dashboard
4. **Add `BASE_URL` environment variable** with your app URL (no trailing slash)
5. **Manual Deploy** to apply BASE_URL changes
6. Wait for redeploy (3-5 minutes)

### Step 3: Initialize Application
1. Visit `https://your-app-name.onrender.com/admin_setup`
2. Create your admin account
3. Test order creation and email functionality
4. Verify QR codes point to your Render URL (not localhost)

### Production Considerations:

#### Free Tier Limitations:
- Database: 90-day limit, then deleted
- Web service: Goes to sleep after 15 minutes of inactivity
- Storage: Temporary file storage only

#### For Business Use:
- Upgrade to paid plans for persistent data
- Set up automated database backups
- Configure custom domain name
- Monitor application logs regularly

### Troubleshooting:

#### "Application failed to respond"
- Verify `DATABASE_URL` is complete and correct
- Check all required environment variables are set
- Review build logs for dependency errors

#### "SMTP Authentication Error"
- Confirm Gmail App Password is correct (16 characters)
- Ensure 2-Factor Authentication is enabled on Gmail
- Verify `EMAIL_USERNAME` matches Gmail account

#### QR Codes Point to "localhost"
- Add/update `BASE_URL` environment variable
- Redeploy application after adding `BASE_URL`
- Ensure format: `https://your-app.onrender.com` (no trailing slash)

---

## Support

**For Academic Evaluation:**
- All code and documentation included in submission

**For Production Deployment:**
- Render documentation: [docs.render.com](https://docs.render.com)
- Gmail App Passwords help: [support.google.com/accounts/answer/185833](https://support.google.com/accounts/answer/185833)
- Flask documentation: [flask.palletsprojects.com](https://flask.palletsprojects.com/)



