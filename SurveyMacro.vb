Sub GenerateFeedDetails()
    Dim wsInput As Worksheet
    Dim wsOutput As Worksheet
    Dim wsMain As Worksheet
    Dim lastRow As Long, lastCol As Long
    Dim rowID As Long, colID As Long
    Dim cellValue As String
    Dim feedDescription As String
    Dim outputLastRow As Long

    ' Assign sheets
    Set wsInput = ThisWorkbook.Sheets("Sheet1") ' Input sheet
    Set wsOutput = ThisWorkbook.Sheets("Sheet2") ' Output sheet
    On Error Resume Next
    Set wsMain = ThisWorkbook.Sheets("Main") ' Main sheet
    If wsOutput Is Nothing Then
        Set wsOutput = ThisWorkbook.Sheets.Add
        wsOutput.Name = "Sheet2"
    End If
    On Error GoTo 0

    ' Define last row and column in Input sheet
    lastRow = wsInput.Cells(wsInput.Rows.Count, 1).End(xlUp).Row
    lastCol = wsInput.Cells(1, wsInput.Columns.Count).End(xlToLeft).Column

    ' Set headers for the output sheet
    wsOutput.Cells(1, 1).Value = "Feed Description"
    wsOutput.Cells(1, 2).Value = "Feed Type"
    wsOutput.Cells(1, 3).Value = "Data Set Type"
    wsOutput.Cells(1, 4).Value = "Existing Controls"

    ' Loop through all cells in the Input sheet
    For rowID = 2 To lastRow
        For colID = 2 To lastCol
            cellValue = UCase(wsInput.Cells(rowID, colID).Value)
            If cellValue = "X" Or cellValue = "Y" Or cellValue = "XY" Then
                ' Create feed description
                feedDescription = "Feed from App" & rowID - 1 & " to App" & colID - 1

                ' Find the last row in the output sheet
                outputLastRow = wsOutput.Cells(wsOutput.Rows.Count, 1).End(xlUp).Row + 1

                ' Write details to the output sheet
                wsOutput.Cells(outputLastRow, 1).Value = feedDescription
                wsOutput.Cells(outputLastRow, 2).Value = "Type of Feed" ' Placeholder for Feed Type
                wsOutput.Cells(outputLastRow, 3).Value = "Type of Data Set" ' Placeholder for Data Set Type
                wsOutput.Cells(outputLastRow, 4).Value = "Existing Controls" ' Placeholder for Controls

                ' Update original sheet with lowercase values
                wsInput.Cells(rowID, colID).Value = LCase(cellValue)
            End If
        Next colID
    Next rowID

    MsgBox "Feed details generated in Sheet2!", vbInformation
End Sub

Sub CreateGenerateButton()
    Dim wsMain As Worksheet
    Dim btn As Button
    Dim btnLeft As Double, btnTop As Double, btnWidth As Double, btnHeight As Double

    ' Assign the Main sheet
    Set wsMain = ThisWorkbook.Sheets("Main")
    On Error Resume Next
    wsMain.Buttons.Delete ' Remove existing buttons if any
    On Error GoTo 0

    ' Set button dimensions
    btnLeft = 100
    btnTop = 50
    btnWidth = 150
    btnHeight = 30

    ' Add the button
    Set btn = wsMain.Buttons.Add(btnLeft, btnTop, btnWidth, btnHeight)
    btn.OnAction = "GenerateFeedDetails"
    btn.Caption = "Generate Feeds"
    btn.Name = "btnGenerateFeeds"

    MsgBox "Generate Button created on the Main sheet!", vbInformation
End Sub