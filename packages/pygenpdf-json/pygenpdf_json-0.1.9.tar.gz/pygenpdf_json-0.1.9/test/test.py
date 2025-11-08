import os
from pygenpdf import *

image_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAACXBIWXMAABibAAAYmwFJdYOUAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAABCRJREFUaIHt282vnFMcwPHPOfNSbwuKBWErUYIgoknTVISl2CAVuRm33D+ADSKxEcSGrWpvXzfaSCMRFgSpJg0RIUpSXQsJVQuq7szz/CyeGZ1bve9t752n97uZ5JzznDnf+T3nPM955vekiLAktqUbNG1Uule2TrgJV+JSNBfZaw9/4w/Jj0o/SA5rOGgsflrKcNOihHeka4UxjEluQ0i6svbpnpcyLMS0zymlVr/XbyR7TNltIn5baLcLE96RbhRelHSQZQ1Zkhf6tYukRCmUChTCdk2vLCTq8xPen9r+9BxekGRZS2PRwz43lCh0hQIv63rdRHTnOmxu4W3pZk3vCOs0NJZd9EyqWBc4IjxmPI7O1nx24cn0IA5I2lqaS56X54tATxc94VFPxvszNZ159k2mjuRDDZesaFmqpaypJVmD90ymsRmbnjXCO9Jm7JXlRV9YloseSqWw2XjsO7P6/8KTaT0OamporOi4zkwhFHpKG2yJL4erpgtvTddoOSK7WnPkYjudrkL4VcOtxuL4oHj6HG57U7JWY8RloamBa/S8MVx8OsK70v1KH2uabSkbLUrVul3aZEscZFit8IqsVxtZKruskL02XMTOtElyzwiuyXNTTc/1tqeNDITDRP/mv34kJF0NT0GKt1ym5YSmdi2FGczlf1zhqqxtI9ojesWdH5XbGn/ZkIVNkqnaCydTwn1ZuF3WWu4xnXeSlnBblq2z9OcTK58kSW7JwlXLPZYLQhXStRmXXQTxHXB5ZsU9wzifNOp65Z2RVeG6sypcd1aF686qcN1ZFa47q8J1Z1W47mTVf+gXC0XGyeUexQWh+gvtzyw5YYmpWiPEiaz0g7gIlCvHI1nyrTBnus/IUzl+l/Gp0K51jAOhjU+yrs8xVWvhEpySHMom4qRkv6LGp3Wpi306caq68ShsFVr9X6JelAgt4W2Gczx2pMOyu0c+e+dMenrCFzqxgeFby+R5pWatolxl3zaUnhsUnRbuxGfYradbmwWsiu4u43FoUDR989DwjOQ3hd4FH9y5JJxOTAvPDldNFx6L4woPK4VihONcCtWm6CFb4vfhqv9vD7fEl8IT/XzF0ZPuqXItS48bj6/OrD77fng89kk6SqXuCC1jvf/OzTHj8e7ZmsyeIL4zPSAcwBpNzRX7uGCQIB66kkd04oOZms6u0ImPhLvwvV4/0X6lUagWKL6T3DGbLPN5xDMeR13hHrykcMpUv/vlphLtKpwUXjTlXp04NtdhC3uNZzJdL3keT0uakqwhXbAckWrtDaEUusLbel41ET/Pt4vFvai1O12tMIYncKfBi1qpn9F3rn6AMNjpTKHVv2Z8LezVtGc48Xu+LE54mK3pOi0bsZ7+q3jJWuFSaZH35aEn+RvHcUzyvdJh2UGd+GUpw/0Xd1aE2duxJhUAAAAASUVORK5CYII="


DETAILS = [["1", "Cafe", "1", "1000", "$1000"],
           ["3", "Chocolate", "2", "2000", "$4000"],
           ["5", "Medialuna salada", "2", "1500", "$3000"],
           ["2", "Factura crema", "2", "1500", "$3000"],
           ["8", "Chipa 100 gramos", "2", "3000", "$6000"]]


def invoice_test_fit_size_font():
    print("invoice_test_fit_size_font")
    doc = Document()
    doc.set_skip_warning_overflowed(True)
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))
    # doc.use_genpdf_json_bin("genpdf-json-bin")
    # doc.add_font("/usr/share/fonts/truetype/noto", "NotoSans")
    doc.set_line_spacing(1.0)
    
    
    layout = VerticalLayout().framed(LineStyle().with_thickness(.1)).padded(1)
    
    layout.push(
        Paragraph("Invoice").styled(Style().bold().with_font_size(25)).aligned(Alignment.CENTER)
        )        
    
    layout_horizontal = HorizontalLayout([1,2,1])
    layout_horizontal.push(Paragraph("Date_2025").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Image().from_base64(image_png_base64).aligned(Alignment.CENTER).with_scale(2.5))
    layout_horizontal.push(Paragraph("Number_12345").styled(Style().with_fit_size_to(5).with_font_size(100).bold()).aligned(Alignment.RIGHT))
    
    layout.push(
         layout_horizontal
        )
    
    layout.push(
        Break(1)
        )
    
    doc.push(layout)
    
    doc.push(
        Break(2)
        )
        
    doc.push(
        Paragraph("details").styled(Style().bold().with_font_size(20)).aligned(Alignment.CENTER)
        )
    #table
    table = TableLayout([1,2,1,1,1, 2]).styled(Style())
    #table.set_cell_decorator(FrameCellDecorator(True, True, True))
    table.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.2).with_color(Color().rgb(210, 105, 30))))
    table.push_row([
                     Paragraph("code").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("name").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("unit").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("count").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("total").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     Paragraph("total").styled(Style().bold().italic()).aligned(Alignment.CENTER),
                     ])
    total = 0.0
    for item in DETAILS:
        table.push_row([
                        Paragraph(item[0]).styled(Style().with_fit_size_to(20).with_font_size(100).bold().italic()).aligned(Alignment.CENTER),
                        Paragraph(item[1]).styled(Style().with_fit_size_to(20).with_font_size(100).bold().italic()).aligned(Alignment.LEFT).padded(Margins().vh(0,1)),
                        Paragraph(item[2]).styled(Style().with_fit_size_to(20).with_font_size(100).bold().italic()).aligned(Alignment.CENTER),
                        Paragraph(item[3]).styled(Style().with_fit_size_to(20).with_font_size(100).bold().italic()).aligned(Alignment.CENTER),
                        Paragraph(item[4]).styled(Style().with_fit_size_to(20).with_font_size(100).bold().italic()).aligned(Alignment.RIGHT),
                        Paragraph(item[4]).styled(Style().with_fit_size_to(20).with_font_size(100).bold().italic()).aligned(Alignment.RIGHT),
                        ])  
        total += float(item[2]) * float(item[3])
    
    doc.push(table)
    
    doc.push(
        Break(2)
        )
    
    layout_horizontal = HorizontalLayout([4,1])
    layout_horizontal.push(
            Paragraph("Total").styled(Style().with_fit_size_to(12).with_font_size(100).bold()).aligned(Alignment.RIGHT).padded(Margins().vh(0, 3))
        )
    layout_horizontal.push(
            Paragraph("$"+str(total)).styled(Style().with_fit_size_to(12).with_font_size(100).bold()).aligned(Alignment.RIGHT)\
            .framed(LineStyle().with_thickness(.3).with_color(Color().rgb(210, 105, 30)))
        )
    doc.push(layout_horizontal)
        
    doc.render_json_file(dir_now + "/invoice_test_fit_size_font.pdf")
        
    # print(doc.render_json_base64()[:3])


def test_emit_error():
    print("test_emit_error")
    doc = Document()
    doc.set_skip_warning_overflowed(False) #emit Warning or not
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))   
    doc.set_line_spacing(1.0)
    
    
    layout = VerticalLayout().framed(LineStyle().with_thickness(.1)).padded(1)
    
    layout.push(
        Paragraph("Invoice").styled(Style().bold().with_font_size(25)).aligned(Alignment.CENTER)
        )        
    
    layout_horizontal = HorizontalLayout([1,1,1,1,1])
    layout_horizontal.push(Paragraph("medialunas").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Paragraph("palmeritas").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Paragraph("facturas_crema").styled(Style().with_font_size(100).bold())) # force to show error with overflowed
    layout_horizontal.push(Paragraph("chipa_100").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Paragraph("Number_12345").styled(Style().with_fit_size_to(5).with_font_size(100).bold()).aligned(Alignment.RIGHT))
    
    layout.push(
         layout_horizontal
        )
    
    layout.push(
        Break(1)
        )
    
    doc.push(layout)
    
    
        
    doc.render_json_file(dir_now + "/test_emit_error.pdf")
        
    # print(doc.render_json_base64()[:3])
 
def test_hyphen_or_force_cut_word():
    print("test_hyphen_or_force_cut_word")
    doc = Document()
    doc.set_skip_warning_overflowed(True) #skip Warning or not
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))   
    doc.set_line_spacing(1.0)
    
    
    layout = VerticalLayout().framed(LineStyle().with_thickness(.1)).padded(1)
    
    layout.push(
        Paragraph("Invoice").styled(Style().bold().with_font_size(25)).aligned(Alignment.CENTER)
        )        
    
    layout_horizontal = HorizontalLayout([1,1,1,1,1])
    layout_horizontal.push(Paragraph("medialunas").styled(Style().with_font_size(20).bold()))
    layout_horizontal.push(Paragraph("palmeritas").styled(Style().with_font_size(30).bold()).framed(LineStyle().with_thickness(.1)).padded(1))
    layout_horizontal.push(Paragraph("facturas_crema").styled(Style().with_font_size(30).bold()).framed(LineStyle().with_thickness(.1)).padded(1))
    layout_horizontal.push(Paragraph("chipa_100").styled(Style().with_font_size(30).bold()).framed(LineStyle().with_thickness(.1)).padded(1))
    layout_horizontal.push(Paragraph("Number_12345").styled(Style().with_fit_size_to(5).with_font_size(20).bold()).aligned(Alignment.RIGHT))
    
    layout.push(
         layout_horizontal
        )
    
    layout.push(
        Break(1)
        )
    
    doc.push(layout)
    
    
        
    doc.render_json_file(dir_now + "/test_hyphen_or_force_cut_word.pdf")
        
    # print(doc.render_json_base64()[:3])

def test_skip_error_and_not_render_text():
    print("test_skip_error_and_not_render_text")
    doc = Document()
    doc.set_skip_warning_overflowed(True) #emit Warning or not
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))   
    doc.set_line_spacing(1.0)
    
    
    layout = VerticalLayout().framed(LineStyle().with_thickness(.1)).padded(1)
    
    layout.push(
        Paragraph("Invoice").styled(Style().bold().with_font_size(25)).aligned(Alignment.CENTER)
        )        
    
    layout_horizontal = HorizontalLayout([1,1,1,1,1])
    layout_horizontal.push(Paragraph("medialunas").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Paragraph("palmeritas").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Paragraph("facturas_crema").styled(Style().with_font_size(100).bold())) # do not show paragraph in overflowed
    layout_horizontal.push(Paragraph("chipa_100").styled(Style().with_fit_size_to(5).with_font_size(100).bold()))
    layout_horizontal.push(Paragraph("Number_12345").styled(Style().with_fit_size_to(5).with_font_size(100).bold()).aligned(Alignment.RIGHT))
    
    layout.push(
         layout_horizontal
        )
    
    layout.push(
        Break(1)
        )
    
    doc.push(layout)
    
    
        
    doc.render_json_file(dir_now + "/test_skip_error_and_not_render_text.pdf")
        
    # print(doc.render_json_base64()[:3])
    
    
if __name__=="__main__":
    invoice_test_fit_size_font()    
    test_skip_error_and_not_render_text()
    test_hyphen_or_force_cut_word()
    test_emit_error()
