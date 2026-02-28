# ScrapLLM

> Intelligent e-commerce scraping platform powered by LLMs to extract structured product data from dynamic websites without hardcoded selectors.

ScrapLLM combines scraping infrastructure, HTML preprocessing, LLM-based structured extraction, validation, and monitoring into a production-ready pipeline.

---

## Overview

ScrapLLM is designed to automate large-scale product data extraction across heterogeneous e-commerce websites.

The system:
- Scrapes product pages from 50+ websites
- Cleans and preprocesses raw HTML to reduce noise
- Uses LLMs to extract structured product fields
- Validates and normalizes outputs
- Monitors performance, latency, and cost across multiple models

---

## Results

| Metric | Result |
|---|---|
| Structured extraction accuracy | **95%** |
| Token consumption reduction | **60%** |
| API cost reduction | **$400/month** |
| Response time improvement | **40%** |

---

## Problem

Traditional scraping systems rely on manual CSS selector mapping per website. This approach:
- Does not scale across many brands
- Breaks when websites update layouts
- Requires continuous maintenance
- Increases operational cost

ScrapLLM eliminates the need for static selectors by leveraging LLMs to dynamically interpret and extract structured product data directly from cleaned HTML.

---

## Architecture

**High-level flow:**
```
URL Ingestion
     ↓
Scraping Layer (HTML Retrieval)
     ↓
HTML Cleaning & Preprocessing
     ↓
LLM-Based Structured Extraction
     ↓
Output Validation & Normalization
     ↓
Monitoring & Evaluation
```

The system is modular, extensible, and designed for multi-model experimentation.

---

## Key Engineering Decisions

### HTML Preprocessing Pipeline

To reduce token usage and cost:
- Removed non-semantic DOM elements
- Extracted product-relevant sections
- Applied intelligent truncation strategies
- Reduced prompt size by **60%** without degrading extraction quality

### Structured Output Enforcement

- JSON schema-based prompting
- Output validation layer
- Automatic retry on malformed responses
- Normalization of price, currency, and availability formats

### Multi-Model Evaluation

Integrated monitoring to:
- Compare multiple LLM providers
- Track latency and token usage
- Measure cost efficiency
- Evaluate structured field accuracy

This enabled data-driven model selection and performance optimization.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| AI Orchestration | LangChain |
| Monitoring | Langfuse |
| Frontend | React |
| Containerization | Docker |
| Cloud | GCP |

---

## Impact

- Eliminated manual product data entry
- Scaled extraction across 50+ heterogeneous websites
- Reduced API costs through preprocessing optimization
- Improved response latency through structured benchmarking
- Built a reusable architecture adaptable to new brands without selector engineering

---
## Demos
### Scrapping 
Check out the [Link](https://drive.google.com/file/d/1sjn5ra1Lo0u0-8n1uADBndOGfipgUFyQ/view?usp=sharing) 

### Benchmark
Check out the [Link](https://drive.google.com/file/d/1Awrw0R0zPvftdgHWcsfSKkG70wIVKOG1/view?usp=sharing) 

## Future Improvements

- [ ] Distributed scraping workers
- [ ] Queue-based processing architecture
- [ ] Extraction confidence scoring
- [ ] Hybrid selector + LLM fallback strategy
- [ ] Domain-specific fine-tuned extraction model
