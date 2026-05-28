# Capstone Project – Social Media Analytics Backend

This repository contains the backend server built for my senior **Capstone Project**, a requirement for graduation. The project was completed in collaboration with a real-world sponsor, and it focuses on **automating social media tracking and reporting**.

## 🎯 Project Overview

The backend service is responsible for collecting and delivering weekly insights on our sponsor’s social media performance. It automates the process of tracking follower growth across platforms and integrates with SharePoint to present the data in a visual, user-friendly way.

## 🏆 Sponsor Testimonial

Here is a 46-second message from our project sponsor sharing feedback on our work:

<video src="dave_testimonial.mp4" width="100%" controls></video>

## ⚙️ Key Features

- **Social Media Scraper**: A Python-based scraper that pulls follower counts and other key metrics from our sponsor's social platforms.
- **Weekly Email Reports**: Automatically sends an email summary of week-to-week social media growth to our sponsor via SMTP.
- **Power Automate Integration**: A Power Automate workflow triggers this server weekly, retrieves updated metrics, and sends the data to SharePoint.
- **SharePoint Dashboard**: The scraped data is displayed as a chart view in SharePoint, making it easy for stakeholders to review trends.

## 🛠️ Tech Stack

- **Python** – for backend scripting and data scraping.
- **SMTP** – for sending automated weekly reports.
- **Microsoft Power Automate** – for scheduled execution and integration.
- **Microsoft SharePoint** – for storing and visualizing the social media data.

## 📦 Deployment

The backend server is hosted externally and exposed via an endpoint that Power Automate calls on a weekly schedule. The server handles the entire data retrieval and delivery workflow from social media scraping to SharePoint integration.
