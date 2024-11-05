# YouTube Transcript Downloader

This application allows you to download transcripts for YouTube videos from a channel or an individual video. It includes features for transcript filtering by date range and combining transcripts for a specific channel.

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
  - [Clone the Repository](#1-clone-the-repository)
  - [Install Dependencies](#2-install-dependencies)
  - [Run the Application](#3-run-the-application)
- [Docker Setup](#docker-setup)
  - [Build the Docker Image](#1-build-the-docker-image)
  - [Run the Docker Container](#2-run-the-docker-container)
- [Usage](#usage)
- [Customizing the Docker Image Name](#customizing-the-docker-image-name)

## Requirements

- Python 3.7+
- Docker (optional, for containerized deployment)

## Setup

### 1. Clone the Repository
Clone this repository to your local machine:

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies
Install the necessary Python packages with:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
To start the Flask application on your local machine, use:

```bash
python app.py
```

The app will be accessible at `http://localhost:5000`.

## Docker Setup

### 1. Build the Docker Image
To build the Docker image, run:

```bash
docker build -t ytscript .
```

### 2. Run the Docker Container
To run the Docker container on port 5000:

```bash
docker run -p 5000:5000 ytscript
```

You can now access the app at `http://localhost:5000` on your browser.

## Usage

1. Navigate to `http://localhost:5000`.
2. Enter a YouTube channel or video URL to download transcripts.
3. View and manage downloaded transcripts through the app interface.

## Customizing the Docker Image Name

If you'd like to use a custom Docker image name or tag, specify it as follows:

```bash
docker build -t <your-username>/ytscript:<your-tag> .
docker run -p 5000:5000 <your-username>/ytscript:<your-tag>
```

---

For questions or issues, please open an [issue](../../issues) in this repository.