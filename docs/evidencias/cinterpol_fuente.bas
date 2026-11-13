Attribute VB_Name = "Interpolacion"
Option Explicit


Function CInterPol(ByVal fecha As Variant, _
ByRef inCurva As Variant, Optional ByVal modo As Integer) As Variant
    
    Dim a As Integer, b As Integer, n As Integer, m As Integer
    Dim curva As Variant
    
    curva = inCurva
    If IsMissing(modo) Then
    
        m = 0
    Else
        m = modo
    End If
      
    a = 1
    b = UBound(curva, 1)
    n = Int((a + b) / 2)
      
    While b - a > 1
        If curva(n, 1) >= fecha Then b = n
        If curva(n, 1) < fecha Then a = n
        n = Int((a + b) / 2)
    Wend
    
    Select Case modo
        Case 0
            CInterPol = Exp(Log(curva(a, 2)) + (Log(curva(b, 2)) _
            - Log(curva(a, 2))) * ((fecha - curva(a, 1)) _
            / (curva(b, 1) - curva(a, 1))))
        Case 1
            CInterPol = curva(a, 2) + (curva(b, 2) - curva(a, 2)) * (fecha - curva(a, 1)) / (curva(b, 1) - curva(a, 1))
    End Select
    
End Function

