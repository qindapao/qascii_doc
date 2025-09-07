#/bin/bash
asciidoctor -b html5 demo.adoc -o demo.html
node export-pdf.js input=demo.html output=demo.pdf size=A3 title="my tech doc"
python generate_pdf_outline.py

