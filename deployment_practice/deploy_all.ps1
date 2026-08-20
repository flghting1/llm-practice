$ErrorActionPreference = "Stop"

$repoDir = Split-Path -Parent $PSScriptRoot
$modelCache = Join-Path $env:USERPROFILE ".cache\huggingface"

if (-not (Test-Path $modelCache)) {
    throw "Hugging Face model cache was not found: $modelCache"
}

$services = @(
    @{
        Name = "rag-practice-api"
        Image = "rag-practice-api"
        Directory = "rag_practice"
        HostPort = 8001
        ContainerPort = 8001
        ExtraArgs = @(
            "-e"
            "HF_HUB_OFFLINE=1"
            "-e"
            "TRANSFORMERS_OFFLINE=1"
            "-v"
            "${modelCache}:/root/.cache/huggingface:ro"
        )
    },
    @{
        Name = "sql-agent-api"
        Image = "sql-agent-api"
        Directory = "sql_agent_practice"
        HostPort = 8004
        ContainerPort = 8003
        ExtraArgs = @()
    },
    @{
        Name = "resume-matcher-api"
        Image = "resume-matcher-api"
        Directory = "resume_matcher_practice"
        HostPort = 8006
        ContainerPort = 8005
        ExtraArgs = @()
    }
)

foreach ($service in $services) {
    $projectDir = Join-Path $repoDir $service.Directory

    Write-Host ""
    Write-Host "Building image: $($service.Image)"
    docker build -t $service.Image $projectDir

    Write-Host "Removing old container: $($service.Name)"
    docker rm -f $service.Name 2>$null

    Write-Host "Starting container: $($service.Name)"
    docker run -d `
        --name $service.Name `
        -p "$($service.HostPort):$($service.ContainerPort)" `
        @($service.ExtraArgs) `
        $service.Image
}

Write-Host ""
Write-Host "Waiting for services..."

$healthUrls = @(
    "http://127.0.0.1:8001/health",
    "http://127.0.0.1:8004/health",
    "http://127.0.0.1:8006/health"
)

foreach ($url in $healthUrls) {
    $healthy = $false

    for ($attempt = 1; $attempt -le 15; $attempt++) {
        try {
            $result = Invoke-RestMethod `
                -Uri $url `
                -TimeoutSec 5 `
                -ErrorAction Stop

            if ($result.ok -eq $true) {
                Write-Host "Health check passed: $url"
                $healthy = $true
                break
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    if (-not $healthy) {
        throw "Health check failed: $url"
    }
}

Write-Host ""
Write-Host "Container status"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"