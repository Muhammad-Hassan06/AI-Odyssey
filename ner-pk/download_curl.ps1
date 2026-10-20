$ErrorActionPreference = "Stop"
$dest = "$env:USERPROFILE\.cache\huggingface\hub\models--xlm-roberta-base\blobs\6fd4797bc397c3b8b55d6bb5740366b57e6a3ce91c04c77f22aafc0c128e6feb.incomplete"
$target = "$env:USERPROFILE\.cache\huggingface\hub\models--xlm-roberta-base\blobs\6fd4797bc397c3b8b55d6bb5740366b57e6a3ce91c04c77f22aafc0c128e6feb"
$snapshot = "$env:USERPROFILE\.cache\huggingface\hub\models--xlm-roberta-base\snapshots\e73636d4f797dec63c3081bb6ed5c7b0bb3f2089\model.safetensors"

Write-Host "Downloading model.safetensors with curl..."
curl.exe -L -C - --retry 10 --retry-delay 3 -o $dest "https://huggingface.co/xlm-roberta-base/resolve/main/model.safetensors"

$item = Get-Item $dest
Write-Host "Download finished. Size: $($item.Length) bytes"
if ($item.Length -ge 1115567652) {
    if (Test-Path $target) { Remove-Item $target -Force }
    Move-Item $dest $target -Force
    Copy-Item $target $snapshot -Force
    Write-Host "Model placed in snapshot successfully!"
} else {
    Write-Error "Incomplete download: $($item.Length) bytes"
}
