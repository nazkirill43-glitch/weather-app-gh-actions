# Weather App - GitHub Actions CI/CD Pipeline

Aplikacja pogodowa z automatycznym CI/CD pipeline'em GitHub Actions. Pipeline buduje multi-platform obrazy Docker, skanuje podatliwości i publikuje na GHCR.

Autor: Kyryl Nazarov | Data: 2026-05-26

## Workflow

Plik: `.github/workflows/build-and-push.yml`

Workflow uruchamia się automatycznie przy push'u do main lub otwieraniu Pull Request'a. Etapy: checkout kodu, setup Buildx, login do GHCR i DockerHub, build multi-platform (amd64 + arm64), CVE scan Docker Scout, sprawdzenie rezultatów, upload raportu.

## Zmienne Globalne

```yaml
REGISTRY_GHCR: ghcr.io
REGISTRY_DOCKERHUB: docker.io
CACHE_REGISTRY: docker.io
IMAGE_NAME_GHCR: ${{ github.repository }}
IMAGE_NAME_DOCKERHUB: kaleefff/weather-app
```

## Build Multi-Platform

Buduje dla linux/amd64 i linux/arm64. Pobiera cache z DockerHub, uploaduje zbudowany obraz na GHCR z dwoma tagami (latest i commit SHA), uploaduje cache z mode=max do DockerHub.

## Tagowanie

- `latest` - ostatnia wersja
- `commit-sha` - unikalny tag dla każdego commita

Dwutagowa strategia umożliwia szybki dostęp do ostatniej wersji i pełną reproducibility.

## CVE Scanning

Skanuje z Docker Scout. CRITICAL lub HIGH vulnerabilities powodują fail workflow'u - obraz nie jest uploadowany. MEDIUM/LOW przechodzą pomyślnie.

## Secrets Wymagane

`DOCKERHUB_USERNAME` - nazwa na DockerHub  
`DOCKERHUB_TOKEN` - token z uprawnieniami Read, Write, Delete  
`GHCR_PAT` - GitHub PAT z uprawnieniami write:packages, read:packages, delete:packages

## Cache Strategy

DockerHub cache (`kaleefff/weather-app:cache`) ze względu na większy limit i niezawodność. Mode=max cachuje wszystkie warstwy dla przyspieszenia przyszłych buildów.

## Pull Image

```bash
docker login ghcr.io -u nazkirill43-glitch -p <GHCR_PAT>
docker pull ghcr.io/nazkirill43-glitch/weather-app-gh-actions:latest
```

## Run Container

```bash
docker run -p 5000:5000 ghcr.io/nazkirill43-glitch/weather-app-gh-actions:latest
# http://localhost:5000
```

## Struktura Repozytorium

.github/workflows/build-and-push.yml - workflow
app.py - Flask aplikacja
Dockerfile - multi-stage build
templates/index.html - HTML interfejs
static/style.css - stylizacja
README.md - dokumentacja

## Linki

GitHub: https://github.com/nazkirill43-glitch/weather-app-gh-actions  
Actions: https://github.com/nazkirill43-glitch/weather-app-gh-actions/actions  
GHCR: https://ghcr.io/nazkirill43-glitch/weather-app-gh-actions  
DockerHub Cache: https://hub.docker.com/r/kaleefff/weather-app
