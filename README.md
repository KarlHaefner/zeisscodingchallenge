# ChallengeChat

## Overview
This is ChallengeChat, build as a coding challenge by Karl Häfner for Zeiss "Digital Technology Expert" and "GenAI Solution Architect" 

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Set-up with Dev Container](#set-up-with-dev-container)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Known issues](#known-issues)

## Installation

### Prerequisites
- Node.js
- Python (v3.11)
- pip
- npm 
- Docker
- VS Code with Extention `Remote-Containers` (or equivalent in other IDEs)

### Set-up with Dev Container
   - Configuration:
      - create `.env.local` in `./backend` by copying `./backend/.env.example`
      - Set variables `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`
	- Start dev container
   - Start backend
      - cd into `./backend` if not there
      - run `python manage.py migrate`
      - optional: run `python manage.py createsuperuser` to create a user for the Django admin panel (accessible via `localhost:8000/admin`)
      - run `python manage.py runserver 0.0.0.0:8000`
   - Start Frontend
      - open a new terminal 
      - cd into `./frontend`
      - run `npm run dev`

3. **Start chatting**
   When everything is running got to `http://localhost:5173/` in your browser (works best on Chromium based browsers). The first start might take a while befor the frontend is loading.

## Features
   - General Chat: Chat with the bot to your hearts content. All answer will come streaming, with syntax highlighting and copy options for the whole answer and code blocks 
   - Search for papers: Ask for papers from arXiv. The bot will give you a selection of papers.
   - View papers: You can view the papers in the pdf viewer on the right
   - Aks questions on papers: Ask the bot any questions regarding one of the papers
   - (DEACTIVATED) Ask questions crossing multiple papers: You can ask the bot questions spanning multiple papers, e.g. to compare them. (This feature is deactivated by default because of a bug. See below)

- Technical GenAI features:
   - using LangChain langgraph
   - streaming
   - two tools (+ one buggy tool, see below)
   - message truncation if exceding token limit
   - in memory storage of conversation history using langgraph MemorySaver
   - logging of some info via Django into SQLite

## Tech Stack
- Frontend: React, JavaScript/TypeScript, CSS, Tailwind, Ant Design

- Backend: Django, Python, LangChain (LangGraph), Azure OpenAI

## Configuration
Mandatory configurations are only the `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` in the .env.local

The are two more configuration options:
- `./backend/model_config.yaml` 
   - Sets the deployment names and defines which models can be selected in the frontend. Set instructions in the file.
- `./backend/chat/promt_templates` containes the promts for easy adaption as Jinja2 files
   - Note that the summarization_prompt is not used by default. See explanation below

## Running Tests
Backend Tests

```bash
cd app/backend
python manage.py test
```
Frontend Tests

- not implemented

## Deployment

The app can be deployed as two separate Docker Containers.

To start the containers:
```bash
docker-compose up --build -d
```

## Known issues

- **Summarization**

The summarization tool is currently deactivated due to issues. It is intended to allow the bot to summarize up to three papers for questions involving multiple papers. However, it only supports discussions on a single paper for now.
The problem with the summarization feature is that the summary is always included in the final answer, which it should not be. This is likely due to streaming, as the app starts streaming the summary before it is complete, bypassing the system prompt. The actual answer from the bot follows after the summary is done.
You can activate this feature in the `.env.local` file. To address the issues, the `fetch_paper_content()` function in `./backend/chat/services/arxiv_service.py` needs to return a string. This function currently doubles as the replacement tool for single-paper discussions. This solution is not ideal, but it preserves the work done so far.

- **PDF must be removed manually**

Currently there is no removal of the PDF files implemented.
