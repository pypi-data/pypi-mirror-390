import pygenpdf_json

with open('invoice.json', 'r') as fj:
    string_json = fj.read()
    
pdf_string_base64 = pygenpdf_json.render_json_base64(string_json)
print(pdf_string_base64)

# string_json = """{
#         "config": {
#             "title": "report genpdf", 
#             "style": {}, 
#             "page_size": "A4", 
#             "fonts": [], 
#             "default_font": {"font_family_name": "LiberationSans", "dir": "/usr/share/fonts/truetype/liberation"}, 
#             "head_page": {"type": "paragraph", "value": [{"text": "report genpdf-rs", "bold": true, "size": 8, "italic": true}], "alignment": "right"}, 
#             "margins": [7, 10, 10, 10], "line_spacing": 1.0
#             }, 
#         "elements": [
#                         {
#                             "type": "layout", 
#                             "orientation": "vertical", 
#                             "elements": [
#                                             {
#                                                 "type": "paragraph", 
#                                                 "value": [{"text": "Invoice", "bold": true, "size": 25}], 
#                                                 "alignment": "center"}, 
#                                             {"type": "break", "value": 1}
#                                         ], 
#                             "frame": {"thickness": 0.1}, 
#                             "padding": [1, 1, 1, 1]
#                         }, 
#                         {"type": "break", "value": 2}, 
#                         {
#                             "type": "paragraph", 
#                             "value": [{"text": "details", "bold": true, "size": 12}], 
#                             "alignment": "center"
#                         }                
#                 ]
#     }"""
# 
# pdf_string_base64 = pygenpdf_json.render_json_base64(string_json)
# print(pdf_string_base64)
