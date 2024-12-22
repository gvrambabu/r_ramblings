Sub ProcessDataFlow()
    Dim wsInput As Worksheet
    Dim wsOutput As Worksheet
    Dim lastRow As Long, lastCol As Long
    Dim rowID As Long, colID As Long
    Dim cellValue As String
    Dim columnName As String
    Dim outputHeaderRow As Long
    Dim outputCol As Range

    ' Assign sheets
    Set wsInput = ThisWorkbook.Sheets(1) ' Input sheet (update if necessary)
    On Error Resume Next
    Set wsOutput = ThisWorkbook.Sheets("Output")
    If wsOutput Is Nothing Then
        Set wsOutput = ThisWorkbook.Sheets.Add
        wsOutput.Name = "Output"
    End If
    On Error GoTo 0

    ' Define last row and column
    lastRow = wsInput.Cells(wsInput.Rows.Count, 1).End(xlUp).Row
    lastCol = wsInput.Cells(1, wsInput.Columns.Count).End(xlToLeft).Column
    outputHeaderRow = 1

    ' Loop through all cells in the input sheet
    For rowID = 2 To lastRow
        For colID = 2 To lastCol
            cellValue = UCase(wsInput.Cells(rowID, colID).Value)
            If cellValue = "X" Or cellValue = "Y" Or cellValue = "XY" Then
                ' Create a new column in Output Sheet for Xn or Yn
                If cellValue Like "*X*" Then
                    columnName = "X" & colID - 1
                    Set outputCol = wsOutput.Rows(outputHeaderRow).Find(What:=columnName, LookIn:=xlValues, LookAt:=xlWhole)
                    If outputCol Is Nothing Then
                        wsOutput.Cells(outputHeaderRow, wsOutput.Cells(outputHeaderRow, wsOutput.Columns.Count).End(xlToLeft).Column + 1).Value = columnName
                        Set outputCol = wsOutput.Rows(outputHeaderRow).Find(What:=columnName, LookIn:=xlValues, LookAt:=xlWhole)
                    End If
                    wsOutput.Cells(rowID, outputCol.Column).Value = "x"
                End If
                If cellValue Like "*Y*" Then
                    columnName = "Y" & colID - 1
                    Set outputCol = wsOutput.Rows(outputHeaderRow).Find(What:=columnName, LookIn:=xlValues, LookAt:=xlWhole)
                    If outputCol Is Nothing Then
                        wsOutput.Cells(outputHeaderRow, wsOutput.Cells(outputHeaderRow, wsOutput.Columns.Count).End(xlToLeft).Column + 1).Value = columnName
                        Set outputCol = wsOutput.Rows(outputHeaderRow).Find(What:=columnName, LookIn:=xlValues, LookAt:=xlWhole)
                    End If
                    wsOutput.Cells(rowID, outputCol.Column).Value = "y"
                End If

                ' Update original sheet with lowercase values
                wsInput.Cells(rowID, colID).Value = LCase(cellValue)
            End If
        Next colID
    Next rowID

    MsgBox "Data processing completed!", vbInformation
End Sub