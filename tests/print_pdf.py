import requests
import cups


fn = '../temp/test.pdf'
r = requests.get('http://serverx/test.pdf')
with open(fn,'wb') as f:
  f.write(r.content)

conn = cups.Connection()
printers = conn.getPrinters()
printer_name = printers.keys()[0]
print(printers)

print(printer_name)
conn.printFile(printer_name, fn, "", {})