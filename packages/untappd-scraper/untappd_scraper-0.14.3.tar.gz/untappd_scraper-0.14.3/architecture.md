# untappd-scraper architecture

## Overview

```mermaid
graph
    %% High-level consumers of the library


    %% External data source kept generic
    subgraph "Public web site"
        W1["Various web pages<br>Some using XHR"]
    end

    %% Your library with concrete tech choices
    subgraph "untappd-scraper (library)"
        F1["Fetcher<br/><sub>httpx + hishel (cache)</sub>"]
        P1["Parser<br/><sub>BeautifulSoup4</sub>"]
        V1["Normaliser / Validators<br/><sub>Pydantic, utpd-models-web</sub>"]
    end

    %% Explicit typed outputs
    subgraph Outputs
        O1["Pydantic models"]
    end

    %% Wiring

    F1 --> W1
    W1 --> P1 --> V1 --> O1
```

## Main libraries used

- httpx
- hishel
- BeautifulSoup4 and requests-html (legacy)
- Pydantic
- utpd-models-web, created specifically for this project
- Brotli
- Loguru, logfire
- tenacity, ratelim

## Automated testing

Testing done under GitLab CI/CD pipelines using pytest and captured / simulated HTML responses.
