# Social Media Analytics Backend (Senior Capstone)

This repository houses the backend server for my senior capstone project. Developed in collaboration with a real-world sponsor, it solves a common administrative headache: **manually tracking and reporting social media growth**. 

Instead of forcing team members to manually log in, check follower counts, and copy-paste metrics every week, this service automates the entire flow—from scraping the raw data to updating a SharePoint dashboard and emailing stakeholders.

## 🏆 Sponsor Testimonial

Our project sponsor shared their feedback on what we built in this quick 46-second video:

https://github.com/user-attachments/assets/e89a430a-cc5a-426e-8ebb-e2c8c7252aa7

## ⚙️ Key Features

- **Automated Scraping**: A Python script that crawls our sponsor's social channels to fetch up-to-date follower counts and performance metrics.
- **Weekly Digests**: An automated SMTP email report sent straight to the sponsor, summarizing week-over-week growth.
- **Power Automate Integration**: A weekly scheduled Power Automate flow that pings this server to trigger the scraping run and pull back the latest data.
- **SharePoint Dashboard**: Feeds the scraped metrics directly into SharePoint to generate visual charts for easy trend analysis.

## 🛠️ Tech Stack

- **Python**: For backend logic and custom scraping scripts.
- **Microsoft Power Automate**: For scheduling the weekly runs and orchestrating the data flow.
- **Microsoft SharePoint**: Used as the database and frontend dashboard for stakeholders.
- **SMTP**: For building and sending out the weekly email reports.

## 📦 Deployment

The server is hosted externally, exposing a single endpoint. Every week, Power Automate pings this endpoint to trigger the workflow. The backend then spins up, scrapes the platforms, updates the SharePoint records, and dispatches the weekly email summary.

