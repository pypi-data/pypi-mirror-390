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
    doc = Document()
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))
    doc.set_line_spacing(1.0)
    
    margins_2 = Margins().trbl(2,2,2,2)
    
    style_bold_italic_color = Style().bold().italic().with_color(Color().rgb(12,125,12))
    
    table_coffe = TableLayout([2,3,3,4,3]).styled(Style().with_font_size(12).with_color(Color().greyscale(100)))    
    #table.set_cell_decorator(FrameCellDecorator(True, True, True))
    table_coffe.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_dash(1).with_thickness(.1).with_color(Color().greyscale(150))))
        
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
            
    
    
    image = Image().from_base64(image_png_base64).aligned(Alignment.CENTER).with_scale(2)\
                                                .framed_trbl(
                                                    LineStyle().with_dash(1).with_thickness(.2).with_color(Color().greyscale(150)),
                                                    True, False, True, False
                                                    )
    
    plorem = Paragraph(LOREM).styled(style_bold_italic_color)                
    
    
    doc.push(Paragraph("Layout Test").aligned(Alignment.CENTER)\
                                    .styled(Style().bold().italic().with_font_size(18).with_color(Color().rgb(255,20,20)))\
                                    .framed_trbl(
                                                LineStyle().with_thickness(.1).with_color(Color().greyscale(150)).with_dash(3).with_gap(1).with_dash2(1),
                                                True, True, True, True
                                                )
            )
    
    doc.push(Break(1))
    doc.push(table_coffe)                
    
    
    parafo = Paragraph(LOREM).aligned(Alignment.CENTER)\
                                    .styled(Style().bold().italic().with_font_size(18).with_color(Color().rgb(255,20,20)))\
                                    .padded(2)\
                                    .framed_trbl(
                                                LineStyle().with_thickness(.1).with_color(Color().greyscale(150)),
                                                False, True, True, False
                                                )
    doc.push(Break(1))
    doc.push(parafo)
    
    
    doc.push(Break(1))
    
    doc.push(image)
    
    doc.push(Break(1))
    
    
    
    parafo2 = Paragraph(LOREM).aligned(Alignment.CENTER)\
                                    .styled(Style().bold().italic().with_font_size(18).with_color(Color().rgb(255,20,20)))\
                                    .padded(2)\
                                    .framed_trbl(
                                                LineStyle().with_thickness(.1).with_color(Color().greyscale(150)),
                                                True, True, False, True
                                                )
    doc.push(parafo2)
    doc.push(parafo)
    
    
    
    
    
    table_coffe2 = TableLayout([2,3,3,4,3]).styled(Style().with_font_size(12).with_color(Color().greyscale(100)))    
    #table.set_cell_decorator(FrameCellDecorator(True, True, True))
    table_coffe2.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, 
                                                                         LineStyle().with_dash(3).with_gap(1)\
                                                                         .with_thickness(.2).with_color(Color().greyscale(150))))
        
    table_coffe2.push_row([
                     Paragraph("code").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("name").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("unit").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("count").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("total").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     ])
    total = 0.0
    for item in DETAILS:
        table_coffe2.push_row([
                        Paragraph(item[0]).aligned(Alignment.CENTER),
                        Paragraph(item[1]).aligned(Alignment.LEFT).padded(Margins().vh(0,1)),
                        Paragraph(item[2]).aligned(Alignment.CENTER),
                        Paragraph(item[3]).aligned(Alignment.CENTER),
                        Paragraph(item[4]).aligned(Alignment.RIGHT),
                        ])  
        total += float(item[2]) * float(item[3])
    
    doc.push(PageBreak())
    doc.push(table_coffe2)
    
    doc.render_json_file(dir_now + "/frame_dash_test.pdf")
    
    
if __name__=="__main__":
    main()
