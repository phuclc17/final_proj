# Mo kho du lieu DuckDB bang Harlequin - IDE SQL chay trong terminal: cay schema/bang ben trai,
# o go SQL, bang ket qua. Day la "noi truy van kho du lieu" giong mot CSDL that.
# Dung: powershell -File tools\open_warehouse.ps1 [calibration|holdout]
param([string]$Profile = "calibration")
$Db = "data\$Profile\warehouse\fastfat.duckdb"
if (-not (Test-Path $Db)) { Write-Error "Khong tim thay $Db"; exit 1 }
& ".venv\Scripts\harlequin.exe" $Db -r
