# Automated Research Guide Generator

---

## 🚀 Overview
The **Automated Research Guide Generator** is an open-source Flask-based web application that enables libraries to quickly create research or subject guides.  

By integrating **Koha**, **Google Books API**, and **OpenAlex API** with a library’s journal database, the system retrieves relevant books and articles on any given topic — significantly reducing the manual effort librarians spend curating guides.

---

## ✨ Key Features
- 🔎 **Automated retrieval of books** using Koha + Google Books APIs.  
- 📑 **Automated retrieval of articles** using OpenAlex API + journal subscription database.  
- ⚡ **Fast & scalable**: reduces weeks of manual curation to minutes.  
- 🌍 **Open-source and reusable** by any library (swap CSV with your own journal database).  
- 🛠️ **Extensible architecture** with clear integration points for additional APIs or features.  

---

## 🏗️ System Architecture
The application follows a modular workflow:

1. **Book Retrieval**  
   - Queries Google Books API for topic-relevant titles.  
   - Cross-checks results with the Koha catalog via its API.  

2. **Article Retrieval**  
   - Queries OpenAlex API for topic-relevant articles.  
   - Filters results using a CSV of subscribed journals (title + year range).  

3. **Web Application Layer (Flask)**  
   - Presents curated results via a clean and accessible web interface.  

---

## 💡 Use Cases

- Academic libraries without access to paid discovery/curation services.  
- Institutions looking to streamline research guide creation.  
- Libraries aiming to reduce turnaround time for delivering curated resources.  

---

## 📊 Research Context

Originally developed at **Ashoka University Library (2025)** to reduce weeks of manual librarian effort into an automated, API-driven workflow.  
The system is adaptable for any library by simply replacing the subscription database CSV with their own.  

---

## 📜 License

This project is released under the **MIT License**.
