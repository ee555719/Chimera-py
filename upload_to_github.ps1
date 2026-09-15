# Upload all files to GitHub
$repo = "ee555719/Chimera-py"
$gh = "C:\Program Files\GitHub CLI\gh.exe"

function Upload-File {
    param([string]$Path, [string]$Message)
    
    $relativePath = $Path.Replace("D:\Chimera-py\", "").Replace("\", "/")
    $content = Get-Content -Path $Path -Raw -Encoding UTF8
    $base64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
    
    # Get existing file SHA
    $sha = & $gh api "repos/$repo/contents/$relativePath" --jq '.sha' 2>$null
    
    $args = @("api", "repos/$repo/contents/$relativePath", "--method", "PUT", "-f", "message=$Message", "-f", "content=$base64")
    if ($sha) {
        $args += "-f"
        $args += "sha=$sha"
    }
    
    & $gh @args 2>$null | Out-Null
    Write-Host "Uploaded: $relativePath"
}

$files = Get-ChildItem -Path "D:\Chimera-py" -Recurse -File | Where-Object {
    $_.FullName -notlike "*\__pycache__\*" -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\dist\*" -and
    $_.FullName -notlike "*\build\*" -and
    $_.FullName -notlike "*\*.spec" -and
    $_.Name -ne "*.pyc"
}

foreach ($file in $files) {
    Upload-File -Path $file.FullName -Message "Add $($file.Name)"
}

Write-Host "Done!"
