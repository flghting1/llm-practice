$ErrorActionPreference = "Stop"

$containers = @(
    "rag-practice-api",
    "sql-agent-api",
    "resume-matcher-api"
)

foreach ($container in $containers) {
    $existingContainer = docker ps -aq `
        --filter "name=^$container$"

    if ($existingContainer) {
        Write-Host "Stopping container: $container"
        docker rm -f $container
    }
    else {
        Write-Host "Container not found: $container"
    }
}

Write-Host ""
Write-Host "Remaining project containers"
docker ps -a --filter "name=rag-practice-api"
docker ps -a --filter "name=sql-agent-api"
docker ps -a --filter "name=resume-matcher-api"