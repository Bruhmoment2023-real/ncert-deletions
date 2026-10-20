param([string]$Paper)
# Usage: powershell -File finish.ps1 04-sslc-webcasting   (runs R, python figures, evidence, PDFs, docs; logs in data\run_finish.log)
$k = 'D:\Research-Publishing\_tools\biblio-kit'
$b = "D:\Research-Publishing\$Paper\bibliometrics"
$py = 'D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe'
$env:PYTHONIOENCODING = 'utf-8'
$env:R_LIBS_USER = 'D:\Research-Publishing\_tools\R-lib;C:\Users\seans\AppData\Local\R\win-library\4.5'
$log = "$b\data\run_finish.log"
function Step($n, [scriptblock]$s) { "[$(Get-Date -f HH:mm:ss)] $n" | Add-Content $log; & $s *>&1 | Select-Object -Last 15 | Add-Content $log }
"" | Set-Content $log
Step 'R bibliometrix' { & 'C:\Program Files\R\R-4.5.3\bin\Rscript.exe' "$k\R\bibliometrix_analysis.R" $b }
Step 'python figures' { & $py "$k\figures.py" $b }
if (Test-Path "$k\topic_chart_$($Paper.Substring(0,2)).py") { Step 'topic chart' { & $py "$k\topic_chart_$($Paper.Substring(0,2)).py" $b } }
Step 'law supplement' { if ($Paper -like '06*') { & $py "$k\law_supplement.py" $b } }
Step 'evidence select' { & $py "$k\evidence_auto.py" $b 48 }
Step 'pdf download' { & $py "$k\pdfs.py" $b download }
Step 'evidence table' { & $py "$k\pdfs.py" $b evidence }
Step 'docs' { & $py "$k\docs.py" $b }
New-Item -ItemType Directory -Force "$b\R", "$b\python" | Out-Null
Copy-Item "$k\R\bibliometrix_analysis.R" "$b\R\" -Force
Copy-Item "$k\*.py", "$k\finish.ps1" "$b\python\" -Force
"[$(Get-Date -f HH:mm:ss)] FINISHED" | Add-Content $log
