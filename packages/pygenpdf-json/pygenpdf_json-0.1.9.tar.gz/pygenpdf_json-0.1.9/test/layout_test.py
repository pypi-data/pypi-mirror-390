import os
from pygenpdf import *

image_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAACXBIWXMAABibAAAYmwFJdYOUAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABCRJREFUaIHt282vnFMcwPHPOfNSbwuKBWErUYIgoknTVISl2CAVuRm33D+ADSKxEcSGrWpvXzfaSCMRFgSpJg0RIUpSXQsJVQuq7szz/CyeGZ1bve9t752n97uZ5JzznDnf+T3nPM955vekiLAktqUbNG1Uule2TrgJV+JSNBfZaw9/4w/Jj0o/SA5rOGgsflrKcNOihHeka4UxjEluQ0i6svbpnpcyLMS0zymlVr/XbyR7TNltIn5baLcLE96RbhRelHSQZQ1Zkhf6tYukRCmUChTCdk2vLCTq8xPen9r+9BxekGRZS2PRwz43lCh0hQIv63rdRHTnOmxu4W3pZk3vCOs0NJZd9EyqWBc4IjxmPI7O1nx24cn0IA5I2lqaS56X54tATxc94VFPxvszNZ159k2mjuRDDZesaFmqpaypJVmD90ymsRmbnjXCO9Jm7JXlRV9YloseSqWw2XjsO7P6/8KTaT0OamporOi4zkwhFHpKG2yJL4erpgtvTddoOSK7WnPkYjudrkL4VcOtxuL4oHj6HG57U7JWY8RloamBa/S8MVx8OsK70v1KH2uabSkbLUrVul3aZEscZFit8IqsVxtZKruskL02XMTOtElyzwiuyXNTTc/1tqeNDITDRP/mv34kJF0NT0GKt1ym5YSmdi2FGczlf1zhqqxtI9ojesWdH5XbGn/ZkIVNkqnaCydTwn1ZuF3WWu4xnXeSlnBblq2z9OcTK58kSW7JwlXLPZYLQhXStRmXXQTxHXB5ZsU9wzifNOp65Z2RVeG6sypcd1aF686qcN1ZFa47q8J1Z1W47mTVf+gXC0XGyeUexQWh+gvtzyw5YYmpWiPEiaz0g7gIlCvHI1nyrTBnus/IUzl+l/Gp0K51jAOhjU+yrs8xVWvhEpySHMom4qRkv6LGp3Wpi306caq68ShsFVr9X6JelAgt4W2Gczx2pMOyu0c+e+dMenrCFzqxgeFby+R5pWatolxl3zaUnhsUnRbuxGfYradbmwWsiu4u43FoUDR989DwjOQ3hd4FH9y5JJxOTAvPDldNFx6L4woPK4VihONcCtWm6CFb4vfhqv9vD7fEl8IT/XzF0ZPuqXItS48bj6/OrD77fng89kk6SqXuCC1jvf/OzTHj8e7ZmsyeIL4zPSAcwBpNzRX7uGCQIB66kkd04oOZms6u0ImPhLvwvV4/0X6lUagWKL6T3DGbLPN5xDMeR13hHrykcMpUv/vlphLtKpwUXjTlXp04NtdhC3uNZzJdL3keT0uakqwhXbAckWrtDaEUusLbel41ET/Pt4vFvai1O12tMIYncKfBi1qpn9F3rn6AMNjpTKHVv2Z8LezVtGc48Xu+LE54mK3pOi0bsZ7+q3jJWuFSaZH35aEn+RvHcUzyvdJh2UGd+GUpw/0Xd1aE2duxJhUAAAAASUVORK5CYII="

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

DETAILS = [["1", "Cafe", "1", "1000", "$1000"],
           ["3", "Chocolate", "2", "2000", "$4000"],
           ["5", "Medialuna salada", "2", "1500", "$3000"],
           ["2", "Factura crema", "2", "1500", "$3000"],
           ["8", "Chipa 100 gramos", "2", "3000", "$6000"]]


def main():
    
    margins_2 = Margins().trbl(2,2,2,2)
    
    style_bold_italic_color = Style().bold().italic().with_color(Color().rgb(12,125,12))
    
    table_coffe = TableLayout([1,2,1,1,1]).styled(Style()).padded(2)
    table_coffe.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.3).with_color(Color().greyscale(150))))
    table_coffe.push_row([
                     Paragraph("code").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("name").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("unit").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("count").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("total").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     ])
    total = 0.0
    for item in DETAILS:
        table_coffe.push_row([
                        Paragraph(item[0]).aligned(Alignment.CENTER),
                        Paragraph(item[1]).aligned(Alignment.LEFT).padded(Margins().vh(0,1)),
                        Paragraph(item[2]).aligned(Alignment.CENTER),
                        Paragraph(item[3]).aligned(Alignment.CENTER),
                        Paragraph(item[4]).aligned(Alignment.RIGHT),
                        ])  
        total += float(item[2]) * float(item[3])
            
    unordered_list = UnorderedList().element(Paragraph("urano")).element(Paragraph("neptuno")).framed(LineStyle()).padded(1)
    
    ordered_list = OrderedList()\
            .element(Paragraph("sun"))\
            .element(Paragraph("venus"))\
            .element(Paragraph("jupiter"))\
            .element(unordered_list)\
            .framed(LineStyle())\
            .padded(1)\
            .styled(style_bold_italic_color)
    
    image = Image().from_base64(image_png_base64).aligned(Alignment.CENTER).with_scale(2)
    
    plorem = Paragraph(LOREM).styled(style_bold_italic_color)
    
    layout_vertical = VerticalLayout().element(image).element(ordered_list)
        
    table_orden = TableLayout([1,1,1])
    table_orden.set_cell_decorator(FrameCellDecorator(True, True, True))
    
    table_orden.push_row([
            plorem,
            image,
            ordered_list
        ])
    
    table_orden.push_row([
            table_coffe,
            Paragraph(LOREM).styled(style_bold_italic_color).padded(1),
            unordered_list
        ])
    
    table_orden.push_row([
            layout_vertical,
            VerticalLayout().element(Paragraph(LOREM).aligned(Alignment.CENTER).styled(Style().with_font_size(5))).element(table_coffe).element(image),           
            image
        ])
    
    doc = Document()
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))
    # doc.add_font("/usr/share/fonts/truetype/noto", "NotoSans")
    doc.set_line_spacing(1.0)
    
    doc.push(Paragraph("Layout Test").aligned(Alignment.CENTER).styled(Style().bold().italic().with_font_size(18).with_color(Color().rgb(255,20,20))))
    
    doc.push(Break(1))
    doc.push(table_orden)
    
    doc.render_json_file(dir_now + "/layout_test.pdf")
    
    
if __name__=="__main__":
    main()
