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

- **Backend:** Python, Flask (framework)
- **Frontend:** Jinja2 templates, Bootstrap
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

### Quick Start

This application is designed to deploy easily on **Render** (render.com), which provides reliable web hosting with PostgreSQL database support.

#### Step 1: Create Render Account
1. Go to Render website (render.com) and create an account
2. Connect your GitHub account to Render (create GitHub account if you do not already have one)

#### Step 2: Prepare Your Repository
- **If using GitHub:** Fork this repository to your account
- **If using zip file:** Follow "Zip File Setup" instructions below first

#### Extract ZIP File and Upload to GitHub
1. **Extract the zip file** to your computer
2. **Create a new repository** on [GitHub](https://github.com)
3. **Upload all files** to your new GitHub repository:
4. **Refer to step 2 under Quick Start**

#### Step 3: Create PostgreSQL Database FIRST
1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure the database:
   - **Name:** `opts-database` (or your preferred name)
   - **Plan:** Choose **Free** for testing
   - **Region:** Choose closest to your location (Ohio is used for Eastern US)
3. Click **"Create Database"**
4. **IMPORTANT:** Copy the **Internal Database URL** from the database info page
   - It will look like: `postgresql://username:password@hostname/database_name/...`
   - **Save this URL!** - you'll need it in the next step

#### Step 4: Deploy the Web Application
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name:** `opts-lousso-designs` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Choose **Free** for testing

#### Step 5: Configure Environment Variables (BEFORE FIRST DEPLOY)
**CRITICAL:** Add these environment variables BEFORE your first deployment:

**Required (Must have these or app won't start):**
- `DATABASE_URL` = **The Internal Database URL from Step 3**
- `SECRET_KEY` = Generate a random 32+ character string

**Your App URL (add after first deploy):**
- `BASE_URL` = Your app's URL (Render will show this after deployment)

**Email Configuration:**
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_PORT` = `587`
- `EMAIL_USE_TLS` = `true`
- `EMAIL_USERNAME` = Business Gmail Address
- `EMAIL_PASSWORD` = Gmail App Password (not regular password, find in your Google Workspace account settings)
- `EMAIL_DEFAULT_SENDER` = "Add Name <add_name@addemail.com>"

#### Step 6: Deploy and Initialize
1. Click **"Create Web Service"**
2. Wait for deployment to complete (5-10 minutes)
3. **The database schema will automatically initialize on first startup**
4. **Copy your app's URL** from the Render dashboard
5. **Update the BASE_URL environment variable** with this URL
6. **Redeploy** the service (click "Manual Deploy" → "Deploy latest commit")

#### Step 7: Create First Admin Account
1. Visit your app URL + `/admin_setup` (e.g., `https://your-app-name.onrender.com/admin_setup`)
2. Fill out the form to create your first admin account
3. Log in and start creating orders!

#### Step 7: Create First Admin Account

1. Visit your deployed app URL + `/admin_setup` (e.g., `https://your-app.onrender.com/admin_setup`)
2. Fill out the form to create your first admin account credentials
3. Log in with your new admin credentials
4. This route automatically disables itself after the first admin is created.

**After Initial Setup:**
- Use the staff registration feature to add additional staff members

### Notes for Professors

**Render Free Tier**
- **Database:** 90 day limit, then deletes.
- **Web Service:** Sleeps after 15 minutes of inactivity. **You may need to wait up to 2 minutes for the service to reload.**
- **Storage:** Static PDF and QR files get deleted after every redeploy. Please only deploy once.
- **Grading:** The free tier is perfect for evaluation. You can create test orders and view them in the dashboard. 


