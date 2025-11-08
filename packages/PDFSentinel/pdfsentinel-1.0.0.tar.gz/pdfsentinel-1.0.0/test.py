from pdfsentinel import PDFSentinel

sentinel = PDFSentinel()
result = sentinel.is_file_safe("test.pdf")
print(result)