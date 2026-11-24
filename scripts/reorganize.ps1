# Project File Organization Script
# Run this to reorganize the project structure

# Create organized folder structure
New-Item -ItemType Directory -Force -Path ".\docker"
New-Item -ItemType Directory -Force -Path ".\deployment"
New-Item -ItemType Directory -Force -Path ".\development"

# Move Docker-related files
Move-Item -Force ".\Dockerfile" ".\docker\Dockerfile"
Move-Item -Force ".\docker-compose.yml" ".\docker\docker-compose.yml"
Move-Item -Force ".\.dockerignore" ".\docker\.dockerignore"
Move-Item -Force ".\.env.docker" ".\docker\.env.docker"
Move-Item -Force ".\DOCKER_README.md" ".\docker\README.md"

# Move deployment files
Move-Item -Force ".\DEPLOYMENT.md" ".\deployment\DEPLOYMENT.md"

# Move test/check scripts to development
Move-Item -Force ".\check_ollama.py" ".\development\check_ollama.py"
Move-Item -Force ".\check_openrouter.py" ".\development\check_openrouter.py"
Move-Item -Force ".\count_categories.py" ".\development\count_categories.py"
Move-Item -Force ".\debug_schema_string.py" ".\development\debug_schema_string.py"
Move-Item -Force ".\inspect_schema.py" ".\development\inspect_schema.py"
Move-Item -Force ".\test_api_quick.py" ".\development\test_api_quick.py"
Move-Item -Force ".\test_cache.py" ".\development\test_cache.py"
Move-Item -Force ".\test_query.py" ".\development\test_query.py"
Move-Item -Force ".\test_streamlit_api.py" ".\development\test_streamlit_api.py"

# Clean up temporary files
Remove-Item -Force ".\temp.xlsx" -ErrorAction SilentlyContinue
Remove-Item -Force ".\chatbot.log" -ErrorAction SilentlyContinue

Write-Host "✅ Project reorganized successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "New structure:" -ForegroundColor Cyan
Write-Host "  docker/          - Docker configuration files"
Write-Host "  deployment/      - Deployment guides"
Write-Host "  development/     - Development & testing scripts"
Write-Host "  api/             - API endpoints (existing)"
Write-Host "  chatbot/         - Core chatbot logic (existing)"
Write-Host "  database/        - Database utilities (existing)"
Write-Host "  llm/             - LLM providers (existing)"
Write-Host "  scripts/         - Utility scripts (existing)"
Write-Host "  tests/           - Unit tests (existing)"
Write-Host "  docs/            - Documentation (existing)"
