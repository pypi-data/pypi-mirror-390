# pygenpdf

Fast PDF generator

pygenpdf is the Pythonic way to create PDFs with pygenpdf_json (https://gitlab.com/numaelis/pygenpdf_json)

pygenpdf_json es un binding a la libreria en rust: genpdf-json-rs (https://github.com/numaelis/genpdf-json-rs)

To use pygenpdf_json, python >=3.8 is required.

For Python versions lower than 3.8, it is recommended to use : genpdf-json-bin (https://github.com/numaelis/genpdf-json-bin) and configure in the path

usage example:
```
from pygenpdf import *

doc = Document()
doc.set_default_font( "/usr/share/fonts/truetype/liberation", "LiberationSans")
doc.set_title("report genpdf")
doc.set_paper_size(Size().A4())
doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
doc.set_margins(Margins().trbl(7,10,10,10))
# doc.add_font("/usr/share/fonts/truetype/noto", "NotoSans")
doc.set_line_spacing(1.0)


details = [["1", "Cafe", "1", "1000", "$1000"],
           ["3", "Chocolate", "2", "2000", "$4000"],
           ["5", "Medialuna salada", "2", "1500", "$3000"],
           ["2", "Factura crema", "2", "1500", "$3000"],
           ["8", "Chipa 100 gramos", "2", "3000", "$6000"]]

layout = VerticalLayout().framed(LineStyle().with_thickness(.1)).padded(1)
    
layout.push(
    Paragraph("Invoice").styled(Style().bold().with_font_size(25)).aligned(Alignment.CENTER)
    )

layout.push(
    Break(1)
    )

doc.push(layout)

doc.push(
    Break(2)
    )
    
doc.push(
    Paragraph("details").styled(Style().bold().with_font_size(12)).aligned(Alignment.CENTER)
    )
#table
table = TableLayout([1,2,1,1,1]).styled(Style())
#table.set_cell_decorator(FrameCellDecorator(True, True, True))
table.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.2).with_color(Color().rgb(210, 105, 30))))
table.push_row([
                    Paragraph("code").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                    Paragraph("name").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                    Paragraph("unit").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                    Paragraph("count").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                    Paragraph("total").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                    ])
total = 0.0
for item in details:
    table.push_row([
                    Paragraph(item[0]).aligned(Alignment.CENTER),
                    Paragraph(item[1]).aligned(Alignment.LEFT).padded(Margins().vh(0,1)),
                    Paragraph(item[2]).aligned(Alignment.CENTER),
                    Paragraph(item[3]).aligned(Alignment.CENTER),
                    Paragraph(item[4]).aligned(Alignment.RIGHT),
                    ])  
    total += float(item[2]) * float(item[3])

doc.push(table)

doc.push(
    Break(2)
    )

layout_horizontal = HorizontalLayout([4,1])
layout_horizontal.push(
        Paragraph("Total").styled(Style().bold().with_font_size(14)).aligned(Alignment.RIGHT).padded(Margins().vh(0, 3))
    )
layout_horizontal.push(
        Paragraph("$"+str(total)).styled(Style().bold().with_font_size(14)).aligned(Alignment.RIGHT)\
        .framed(LineStyle().with_thickness(.3).with_color(Color().rgb(210, 105, 30)))
    )
doc.push(layout_horizontal)
doc.render_json_file("invoice.pdf") 
```


Important information:

If you need a small PDF file size on disk, use light fonts, as they are embedded within the PDF.


Links:

https://gitlab.com/numaelis/pygenpdf_json

https://github.com/numaelis/genpdf-json-bin

https://github.com/numaelis/genpdf-json-rs

