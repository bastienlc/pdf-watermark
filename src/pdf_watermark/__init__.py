from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 直接注册 ReportLab 内置中文 CID 字体 'STSong-Light'
try:
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    print("Successfully registered built-in CID font: STSong-Light")
except Exception as e:
    print(f"Warning: Failed to register built-in CID font STSong-Light: {e}")
