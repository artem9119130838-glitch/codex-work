function Resolve-ExistingPaths {
    param([string[]]$Paths)

    $result = New-Object System.Collections.Generic.List[string]
    foreach ($path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        $hasWildcard = $path.Contains('*') -or $path.Contains('?')
        if ($hasWildcard) {
            foreach ($item in (Get-Item -Path $path -ErrorAction SilentlyContinue)) {
                if ($item -and (Test-Path -LiteralPath $item.FullName)) {
                    $result.Add($item.FullName)
                }
            }
        } elseif (Test-Path -LiteralPath $path) {
            $result.Add($path)
        }
    }
    return @($result | Sort-Object -Unique)
}

function Test-ExcludedPath {
    param(
        [string]$Path,
        [string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        if ($Path -like $pattern) { return $true }
    }
    return $false
}

function Export-TableFiles {
    param(
        [Parameter(Mandatory = $true)]$Rows,
        [Parameter(Mandatory = $true)][string]$BasePath,
        [string]$WorksheetName = 'Data'
    )

    $csvPath = "$BasePath.csv"
    $xlsxPath = "$BasePath.xlsx"

    $Rows | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding UTF8

    try {
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $false
        $excel.DisplayAlerts = $false
        $workbook = $excel.Workbooks.Add()
        $sheet = $workbook.Worksheets.Item(1)
        $sheet.Name = $WorksheetName

        $data = Import-Csv -LiteralPath $csvPath
        if ($data.Count -gt 0) {
            $headers = @($data[0].PSObject.Properties.Name)
        } else {
            $headers = @()
        }

        for ($c = 0; $c -lt $headers.Count; $c++) {
            $sheet.Cells.Item(1, $c + 1) = $headers[$c]
        }

        for ($r = 0; $r -lt $data.Count; $r++) {
            for ($c = 0; $c -lt $headers.Count; $c++) {
                $sheet.Cells.Item($r + 2, $c + 1) = [string]$data[$r].($headers[$c])
            }
        }

        if ($headers.Count -gt 0) {
            $lastRow = [Math]::Max(1, $data.Count + 1)
            $lastCol = $headers.Count
            $range = $sheet.Range($sheet.Cells.Item(1, 1), $sheet.Cells.Item($lastRow, $lastCol))
            $null = $range.EntireColumn.AutoFit()
            $null = $range.AutoFilter()
        }

        $workbook.SaveAs($xlsxPath, 51)
        $workbook.Close($false)
        $excel.Quit()

        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($sheet) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

        Write-Output "Excel file saved to: $xlsxPath"
    } catch {
        Write-Warning "Excel export failed. CSV is still available at: $csvPath"
    }

    Write-Output "CSV file saved to: $csvPath"
}
