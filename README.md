**Order Processing and Tracking System (OPTS)**

Created by Wentworth students Tyler Resendes and Samuel Gjencaj
for their Summer 2025 MGMT 5510 - CIS Senior Capstone course.

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

- **Backend:** Python, Flask
- **Frontend:** Jinja2 templates, Bootstrap
- **Database:** PostgreSQL
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

## User Priveleges

- **Staff:** Log in, create orders, select milestones, and manage progress.
- **Clients:** Log in to view their orders and download PDFs.
- **Scan Page:** Use QR code or direct link to update milestone status as work progresses.

## Customizing Milestones

- Edit the master milestone list in `app.py` (or move to DB for dynamic management).
- Only selected milestones are saved per order and shown on scan/detail pages.

## Deployment Instructions


**Option 1: GitHub Deployment (Recommended)**
- Best for production use
- Automatic updates and version control
- Direct integration with Render hosting

**Option 2: Zip File Deployment**
- If you received this project as a zip file
- Requires uploading to GitHub first
- See "Zip File Setup" section below

### Quick Start (Render Hosting)

This application is designed to deploy easily on **Render** (render.com), which provides reliable web hosting with PostgreSQL database support.

#### Step 1: Create Render Account
1. Go to [render.com](https://render.com) and create an account
2. Connect your GitHub account to Render

#### Step 2: Prepare Your Repository
- **If using GitHub:** Fork this repository to your account
- **If using zip file:** Follow "Zip File Setup" instructions below first

#### Step 3: Deploy the Application
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name:** `opts-lousso-designs` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Start with **Free** for testing, upgrade to **Pro Standard** for production

#### Step 4: Add PostgreSQL Database
1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Choose **Free** for testing or **Pro Standard** for production
3. Note the **Internal Database URL** (starts with `postgresql://`)

#### Step 5: Configure Environment Variables
In your web service settings, add these environment variables:

**Required:**
- `SECRET_KEY` = Generate a secure random string (32+ characters)
- `DATABASE_URL` = Your PostgreSQL Internal Database URL from Step 4
- `BASE_URL` = Your app URL

**Email Configuration (for notifications):**
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_PORT` = `587`
- `EMAIL_USE_TLS` = `true`
- `EMAIL_USERNAME` = Your business Gmail address
- `EMAIL_PASSWORD` = Gmail App Password (not regular password)
- `EMAIL_DEFAULT_SENDER` = Your business Gmail address

**Note:** The `BASE_URL` should match your deployed app's URL. Render will assign this when you create the service.

#### Step 6: Initialize Database
1. Connect to your PostgreSQL database using the External Database URL
2. Run the SQL schema file: `sql/v3_lousso_opts_schema.sql`
3. Create your first staff account through the registration page

#### Step 7: Create First Admin Account

**Option A: Use Admin Setup Page (Recommended)**
1. Visit your deployed app URL + `/admin_setup` (e.g., `https://your-app.onrender.com/admin_setup`)
2. Fill out the form to create your first admin account
3. Log in with your new admin credentials
4. This route automatically disables itself after the first admin is created

**After Initial Setup:**
- Use the staff registration feature to add additional staff members

### Zip File Setup

If you received this as a zip file and want to deploy:

#### Step 1: Extract and Upload to GitHub
1. **Extract the zip file** to your computer
2. **Create a new repository** on [GitHub](https://github.com)
3. **Upload all files** to your new GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial OPTS deployment"
   git remote add origin https://github.com/yourusername/opts-deployment.git
   git push -u origin main
   ```



