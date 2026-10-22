# Mo bao cao bang Microsoft Word: cap nhat muc luc, danh muc bang/hinh, so trang; luu lai va xuat PDF de kiem tra.
# Chay: powershell -NoProfile -ExecutionPolicy Bypass -File docs\report\finalize_word.ps1
param([string]$Docx = (Join-Path $PSScriptRoot "..\BaoCao_KhoaLuan.docx"), [switch]$NoPdf)
$Docx = (Resolve-Path $Docx).Path
$pdf = [IO.Path]::ChangeExtension($Docx, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Docx)
    for ($i = 0; $i -lt 2; $i++) {
        foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
        $doc.Fields.Update() | Out-Null
    }
    $doc.Save()
    if (-not $NoPdf) { $doc.ExportAsFixedFormat($pdf, 17) }
    $pages = $doc.ComputeStatistics(2)
    "OK: $pages trang -> $Docx ; PDF -> $pdf"
    $doc.Close(0)
}
finally {
    $word.Quit()
}
