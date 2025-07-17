**Order Processing and Tracking System (OPTS)**

Created by Wentworth students Tyler Resendes and Samuel Gjencaj
for their Summer 2025 MGMT 5510 - CIS Senior Capstone course.

OPTS is a web-based platform for Lousso Designs,a custom upholstery business in the Greater Boston area, to manage custom upholstery orders from creation to delivery.  
OPTS enables staff to create orders with project-specific milestones, track production progress, and generate work order PDFs.  
Clients can log in to view their order status and download documentation.  
The system supports role-based access, milestone customization, QR code scanning for workflow updates, and automated email notifications.

Note: This project is for the sole use of Lousso Designs at this time.

## Features

- **Order Creation:** Staff can create new orders, enter customer info, and select only the milestones needed for each project.
- **Custom Milestones:** Each order has its own set of milestones, chosen at creation and editable later.
- **Scan & Update:** Staff can update milestone status via a scan page (QR code supported).
- **My Orders:** Clients can view order details, milestone history, and download client-facing PDFs that exclude QR codes.
- **Master Dashboard:** Staff can view order details for all projects, their milestone historys, and download PDFs that include QR codes for staff use.
- **Email Notifications:** Sends registration and status emails to clients.
- **PDF Generation:** Generates internal and client-facing work order PDFs.
- **User Roles:** Staff and client logins, with role-based access.

## Tech Stack

- **Backend:** Python 3, Flask, psycopg2
- **Frontend:** Jinja2 templates, Bootstrap 5
- **Database:** PostgreSQL
- **PDF:** ReportLab (python library)
- **QR Codes:** qrcode (python library)
- **Email Processing:** Flask-Mail, Gmail SMTP

## Key Files

- `app.py` — Main Flask app
- `backend/shop_routes.py` — Order, scan, and dashboard routes
- `backend/order_processing.py` — Order creation and PDF logic
- `backend/db.py` — Database connection and helpers
- `templates/` — All HTML/CSS templates
- `sql/lousso_opts_schema.sql` — Database schema

## Usage

- **Staff:** Log in, create orders, select milestones, and manage progress.
- **Clients:** Log in to view their orders and download PDFs.
- **Scan Page:** Use QR code or direct link to update milestone status as work progresses.

## Customizing Milestones

- Edit the master milestone list in `app.py` (or move to DB for dynamic management).
- Only selected milestones are saved per order and shown on scan/detail pages.

