# weather-app-gh-actions

# Weather App - GitHub Actions CI/CD

## Opis

Aplikacja pogodowa z automatycznym CI/CD pipeline'em używającym GitHub Actions.

## Workflow: Build and Push Multi-Platform Image

### Ścieżka pliku
`.github/workflows/build-and-push.yml`

### Co robi workflow?

1. **Checkout** - Pobiera kod z repo
2. **Setup Buildx** - Przygotowuje Docker Buildx dla multi-platform
3. **Login GHCR** - Loguje się do GitHub Container Registry
4. **Login DockerHub** - Loguje się do DockerHub (dla cache'a)
5. **Build** - Buduje obraz dla `linux/amd64` i `linux/arm64`
6. **CVE Scan** - Skanuje podatliwości (Docker Scout)
7. **CVE Check** - Blokuje push jeśli znajduje CRITICAL/HIGH
8. **Upload Report** - Zapisuje raport skanowania

### Tagowanie Obrazów

Używamy **dwóch strategii tagowania**:

#### 1. `latest` Tag
- Zawsze wskazuje na ostatnią wersję
- Dla developerów 

#### 2. Commit SHA Tag
- Unikalny tag dla każdego commita
- Dla produkcji

### Uzasadnienie
Ta strategia jest standard w industry:
- Możliwość wybrania wersji 
- Pełna historia buildów
- Jasne czym się różnią wersje

### Cache Strategy
**Cache Registry:** DockerHub (`kaleefff/weather-app:cache`)

**Dlaczego DockerHub?**
- Większy limit cache'a niż ghcr.io
- Bardziej stabilny w CI/CD
- Publiczny 

**Mode: max**
- Cachuje wszystkie warstwy
- Największe przyspieszenie buildów
- Rekomendowane dla CI/CD

### CVE Scanning
**Narzędzie:** Docker Scout

**Raport:** Dostępny w GitHub Actions > Artifacts

### Secrets Konfiguracja
Workflow wymaga następujących secrets w Settings → Secrets and variables → Actions:
- `DOCKERHUB_USERNAME` - Nazwa na DockerHub
- `DOCKERHUB_TOKEN` - Token DockerHub 
- `GITHUB_TOKEN` - Automatycznie dostarczany przez GitHub

### Obrazy
**GHCR (GitHub Container Registry):**

## Autor
Kyryl Nazarov

