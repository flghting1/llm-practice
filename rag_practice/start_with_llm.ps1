param(
    [Parameter(Mandatory = $true)]
    [string]$BaseUrl,
    [Parameter(Mandatory = $true)]
    [string]$Model,
    [string]$Port = "8013"
)

& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\start_with_llm.py" --base-url $BaseUrl --model $Model --port $Port
