#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pygenpdf

The goals of this library:
* Efficiently organize the JSON to be sent to genpdf-rs.
* Avoid errors
* Elegant code


ELEMENTS = [VerticalLayout, HorizontalLayout, TableLayout, OrderedList, UnorderedList, 
            Paragraph, Image, Text, StyledElement, PaddedElement, FramedElement,
            PageBreak, Break]
            
Element explanation:
* Containers: contain other elements, including themselves: VerticalLayout, HorizontalLayout, TableLayout, OrderedList, UnorderedList
* Basic: those that are not containers but generate text and images: Paragraph, Image, Text (Text has no wrapping or alignment)
* Breaks: PageBreak (page break), Break (line break)

Paragraph is the paragraph element; it is recommended for text because it has wrapping and alignment.
Image allows you to include images via path or with a base64 string. You can also scale, position, assign dpi, and rotate the image.

The vertical layouts are:
* VerticalLayout -> is the same LinearLayout as genpdf-rs: allows you to contain elements vertically.
* OrderedList and UnorderedList: organize elements sequentially with periods or symbols.
* the document is a vertical layout

Horizontal and vertical layout:
* TableLayout: allows you to contain elements horizontally and vertically. It can be used to create a table with cells or to organize other layouts
* HorizontalLayout (does not exist in genpdf-rs) is a TableLayout.

Each layout respects the space of its child layouts, which in turn can have children and be another layout, text, or image.

All elements have configurable padding.
All elements, except images, have a configurable font style. For example, paragraphs within a layout inherit the style from the parent container.
All elements can have a frame that can be configured in line thickness and color. This frame marks the outline of the element's scope.

To generate the PDF, the Document class is used, which is responsible for organizing the general configuration: adding letters, the title, margins, etc.
So far, there are two options for generating the PDF document:
* Create a PDF file.
* Obtain the base64 string from the PDF, without having to create the file on disk.

It is necessary to load at least one font. These, in turn, are embedded within the PDF, so it is recommended to use lightweight fonts (small disk size), as otherwise, very large PDFs will be generated.
"""

__author__ = ['numael.garay']

import json
import subprocess
import os
import sys
import tempfile

if sys.version_info < (3, 8):
    try:
        import pygenpdf_json
    except:
        pygenpdf_json = None
else:
    try:
        import pygenpdf_json
    except:
        print("must install pygenpdf_json or install genpdf-json-bin in the path or configure the doc in doc.use_genpdf_json_bin(path_to_gbin)")
        print("Look at: https://github.com/numaelis/genpdf-json-bin")
        pygenpdf_json = None
    #import pygenpdf_json

timeout=5 * 60

#https://github.com/numaelis/genpdf-json-bin
DIR_GENPDF_JSON_BIN = "genpdf-json-bin"


__all__ = ["Document", "VerticalLayout","TableLayout", "HorizontalLayout", "UnorderedList", "OrderedList",
           "Paragraph", "Text", "Image",  "PageBreak", "Break",
           "FramedElement","PaddedElement", "StyledElement" ,
           "Color", "LineStyle", "Margins", "Size", "StyledString", "FrameCellDecorator", "Alignment", "Style"]
            

class Document:
    """
    It is the class that organizes the structure of the document and the JSON that will be sent to the rckive-genpdf-rs library.
    doc = Document()
    doc.set_title("report genpdf")
    doc.set_skip_warning_overflowed(True)
    doc.set_margins(Margins().trbl(10,10,10,10))
    doc.push(element) # layout, table layout, ordered list, paragraph, break, page break, image
    doc.render_json_file("output.pdf")
    string64 = doc.render_json_base64()
    """
    def __init__(self):
        self.genpdf_library = "lib" # lib or console genpdf-json-bin
        self.max_elements_json = 20000 # otherwise use sqlite -> there is a small improvement in performance
        self.use_sqlite = False
        self.dict_doc = {
            "config":{
                "title":"", 
                "style":{}, 
                "page_size": "A4", 
                "fonts" : [],
                "default_font":{"font_family_name":"LiberationSans",  "dir":"/usr/share/fonts/truetype/liberation"},
                "skip_warning_overflowed": True #-> Skip the page size exceeded warning when the paragraph exceeds the layout
            },        
            "elements": [],
            
        }
        if not pygenpdf_json:
            self.genpdf_library = "console"
        self.list_tables = []
    
    # set skip the page size exceeded warning when the paragraph exceeds the layout
    def set_skip_warning_overflowed(self, skip):
         if type(skip) is not bool:
             raise ValueError("expected a bool") 
         self.dict_doc["config"]["skip_warning_overflowed"] = skip
         
    def set_default_font(self, _dir, font_name):
        if type(_dir) is not str or type(font_name) is not str:
            raise ValueError("expected a str")        
        self.dict_doc["config"]["default_font"] = {"font_family_name":font_name,  "dir":_dir}
    
    def add_font(self, _dir, font_name):
        if type(_dir) is not str or type(font_name) is not str:
            raise ValueError("expected a str")
        self.dict_doc["config"]["fonts"].append({"font_family_name":font_name,  "dir":_dir})
        
    def set_margins(self, margins):
        if type(margins) is not Margins:
            raise ValueError("expected a Margins")
        self.dict_doc["config"]["margins"] = margins.get_data()
    
    def set_head_page(self, head_page):
        if type(head_page) is not Paragraph:
            raise ValueError("expected a Paragraph")
        self.dict_doc["config"]["head_page"] = head_page.get_data()
    
    def set_head_page_count(self, head_page_count):
        if type(head_page_count) is not Paragraph:
            raise ValueError("expected a Paragraph")
        self.dict_doc["config"]["head_page_count"] = head_page_count.get_data()
    
    def set_title(self, title):
        if type(title) is not str:
            raise ValueError("expected a str")
        self.dict_doc["config"]["title"] = title
    
    def set_paper_size(self, size):
        if type(size) is not Size:
            raise ValueError("expected a Size")
        self.dict_doc["config"]["page_size"] = size.get_data()
    
    def set_line_spacing(self, line_spacing):
        if type(line_spacing) not in [float, int]:
            raise ValueError("expected a float or int")
        self.dict_doc["config"]["line_spacing"] = float(line_spacing)
    
    def set_font_size(self, font_size):
        if type(font_size) is not int:
            raise ValueError("expected a int")
        self.dict_doc["config"]["deafault_font_size"] = font_size
    
    def set_creation_date(self, date):
        pass
    
    def set_modification_date(self, date):
        pass
       
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        data = element.get_data()
        if type(element) == TableLayout:
            if len(data["rows"]) > self.max_elements_json:
                self.use_sqlite = True
                tablename = "table%s" % (str(len(self.list_tables)))
                self.list_tables.append({"tablename":tablename, "rows":data["rows"]})
                data["rows"] = tablename
        self.dict_doc["elements"].append(data)
            
    def use_genpdf_json_bin(self, path = ""):
        if path:
            global DIR_GENPDF_JSON_BIN
            DIR_GENPDF_JSON_BIN = path
        self.genpdf_library = "console"
    
    def dump_sqlite(self):
        import sqlite3
        dtemp = tempfile.mkdtemp(prefix='genpdf_')
        db_path = os.path.join(dtemp, "_sqlite_.db")        
        # dir_now = os.path.dirname(os.path.abspath(__file__))
        # db_path = dir_now+"/_sqlite2_.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS config;")
        cursor.execute('''
        CREATE TABLE config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT 
        )
        ''')
        cursor.execute("INSERT INTO config (data) VALUES (?)", (json.dumps(self.dict_doc["config"]),))
        
        cursor.execute("DROP TABLE IF EXISTS elements;")
        
        cursor.execute('''
        CREATE TABLE elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element TEXT            
        )
        ''')
        
        for element in self.dict_doc["elements"]:
            cursor.execute("INSERT INTO elements (element) VALUES (?)", (json.dumps(element),))
            
        for table in self.list_tables:
            tablename = table["tablename"]
            cursor.execute("DROP TABLE IF EXISTS %s;"%(tablename))
            cursor.execute('''
            CREATE TABLE %s (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                row TEXT 
            )
            '''%(tablename))
            for row in table["rows"]:
                sql = "INSERT INTO %s (row) VALUES (?)"%(tablename)
                cursor.execute(sql, (json.dumps(row),))
                
        conn.commit()
        conn.close()
        return db_path
    
    def render_json_file(self, out_path):
        """warning: If the json is too large, it can load all the memory and the processor."""
        if len(self.dict_doc["elements"]) > self.max_elements_json or self.use_sqlite:
            db_path = self.dump_sqlite()
            if self.genpdf_library == "lib":
                try:                    
                    pygenpdf_json.render_file_from_sqlite(db_path, out_path)
                except Exception as e:
                    raise ValueError(e.stderr)                
            else:
                try:
                    cmd = [DIR_GENPDF_JSON_BIN, db_path, out_path] 
                    subprocess.check_call(cmd, timeout=timeout)
                    
                except subprocess.CalledProcessError as e:
                    print("error executing genpdf-json-bin, is the path to it configured?")
                    print("If it doesn't exist yet, you'll need to compile it and configure the path.")
                    print("Look at: https://github.com/numaelis/genpdf-json-bin")
                    try:
                        result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                check=True
                            )
                    except subprocess.CalledProcessError as e:
                        raise ValueError(e.stderr)
        else:
            dtemp = tempfile.mkdtemp(prefix='genpdf_')
            path_json = os.path.join(dtemp, "_json_.json")
            with open(path_json, "w") as archivo:
                json.dump(self.dict_doc, archivo)
                
            if self.genpdf_library == "lib":
                try:                    
                    pygenpdf_json.render_json_file(path_json, out_path)
                except Exception as e:
                    raise ValueError(e.stderr)
            else:
                resultado=""
                try:
                    cmd = [DIR_GENPDF_JSON_BIN, path_json, out_path] 
                    subprocess.check_call(cmd, timeout=timeout)
                    
                except subprocess.CalledProcessError as e:
                    print("error executing genpdf-json-bin, is the path to it configured?")
                    print("If it doesn't exist yet, you'll need to compile it and configure the path.")
                    print("Look at: https://github.com/numaelis/genpdf-json-bin")
                    try:
                        result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                check=True
                            )
                    except subprocess.CalledProcessError as e:
                        raise ValueError(e.stderr)
    
    def render_json_base64(self):
        """warning: If the json is too large, it can load all the memory and the processor."""
        if self.genpdf_library == "console":
            import time
            import base64
            dtemp = tempfile.mkdtemp(prefix='genpdf_')
            path_pdf = os.path.join(dtemp, "temp.pdf")
            self.render_json_file(path_pdf)
            time.sleep(0.10)            
            if os.path.exists(path_pdf):
                file_content = None
                with open(path_pdf, "rb") as filepdf:
                    file_content = filepdf.read()
                time.sleep(0.10)  
                if file_content:
                    data_bytes = base64.b64encode(file_content)            
                    return data_bytes.decode('utf-8')
                else:
                    raise TypeError("Error")
            else:
                raise TypeError("Error")
        else:
            if len(self.dict_doc["elements"]) > self.max_elements_json or self.use_sqlite:
                db_path = self.dump_sqlite()
                return pygenpdf_json.render_base64_from_sqlite(db_path)
            else:
                return pygenpdf_json.render_json_base64(json.dumps(self.dict_doc))
        
        
class BaseElement:
    """
        set_frame(line_style), set_style(style), set_padding(margins)
        chained: framed(line_style).styled(style).padded(margins)        
    """
    def __init__(self):
        self.dict_element = {}
    
    def set_frame(self, line_style):
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        lines = {"top":True, "right":True, "bottom":True, "left":True}
        self.dict_element["frame"] = {**line_style.get_data(), **lines}
        
    def framed(self, line_style):
        self.set_frame(line_style)
        return self
    
    # add config sides of the rectangle
    def set_frame_trbl(self, line_style, top, right, bottom, left):
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        for param in [top, right, bottom, left]:
            if type(param) is not bool:
                raise ValueError("expected a bool" )        
        lines = {"top":top, "right":right, "bottom":bottom, "left":left}        
        self.dict_element["frame"] = {**line_style.get_data(), **lines}
        
    def framed_trbl(self, line_style, top, right, bottom, left):
        self.set_frame_trbl(line_style, top, right, bottom, left)
        return self
    
    def set_style(self, style):
        if type(style) is not Style:
            raise ValueError("expected a Style")
        self.dict_element["style"] = style.get_data()
        
    def styled(self, style):
        self.set_style(style)
        return self
        
    def set_padding(self, padding):
        if type(padding) not in [float, int, Margins]:
            raise ValueError("expected a float, int or Margins")
        if type(padding) in [float, int]:            
            padding = Margins(top=padding, right=padding, bottom=padding, left=padding)        
        self.dict_element["padding"] = padding.get_data()
    
    def padded(self, padding):
        self.set_padding(padding)
        return self
    
    def get_data(self):
        return self.dict_element
    
    
class Break:
    """line break, in the layout
    break = Break(1.2)
    layout.push(break)
    """
    def __init__(self, value):
        if type(value) not in [float, int]:
            raise ValueError("expected a float or int")
        self.dict_element = {"type" : "break", "value": value}
        
    def get_data(self):
        return self.dict_element


class PageBreak:
    """page break
    doc.push(PageBreak())
    """
    def __init__(self):
        self.dict_element = {"type" : "page_break"}
        
    def get_data(self):
        return self.dict_element
        
        
class Image(BaseElement):
    """
    image = Image().from_path("path/im.png")    
    image = Image().from_base64("sdgdQwYgHHj")
    
    
    image.set_alignment(Alignment.CENTER) o image = Image().from_path("path/im.png").aligned(Alignment.CENTER)
    
    funciones chained: from_path, from_base64, with_position, with_scale, aligned, with_clockwise_rotation, with_dpi
    funciones: set_position, set_scale, set_clockwise_rotation, set_alignment, set_clockwise_rotation, set_dpi
    """
    def __init__(self):
        self.dict_element = {"type" : "image"}
        
    def from_path(self, path):
        if type(path) is not str:
            raise ValueError("expected str")
        self.dict_element["path"] = path
        return self
        
    def from_base64(self, str_base64):
        if type(str_base64) is not str:
            raise ValueError("expected str")
        self.dict_element["base64"] = str_base64
        return self
        
    def set_position(self, pos_x, pos_y):
        if type(pos_x) not in [float, int] or type(pos_y) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["position"] = [float(pos_x), float(pos_y)]
    
    def with_position(self, pos_x, pos_y):
        self.set_position(pos_x, pos_y)
        return self
    
    def set_scale(self, scale):
        if type(scale) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["scale"] = abs(float(scale))
    
    def set_style(self, style):
        pass
    
    def with_scale(self, scale):
        self.set_scale(scale)
        return self
        
    def set_alignment(self, alignment):
        if type(alignment) is not str:
            raise ValueError("expected str")
        if alignment not in Alignment.get_values():
            raise ValueError("expected Alignment values")
        self.dict_element["alignment"] = alignment
    
    def aligned(self, alignment):
        self.set_alignment(alignment)
        return self
    
    def set_clockwise_rotation(self, rotation):
        if type(rotation) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["rotation"] = rotation        
    
    def with_clockwise_rotation(self, rotation):
        self.set_clockwise_rotation(rotation)
        return self
    
    def set_dpi(self, dpi):
        if type(dpi) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["dpi"] = dpi    
    
    def with_dpi(self, dpi):
        self.set_dpi(dpi)
        return self

    
class VerticalLayout(BaseElement):
    """
    The vertical layout allows you to add any element vertically, avoiding overlapping.
    """
    def __init__(self):
        self.dict_element = {"type" : "layout", "orientation":"vertical", "elements":[]}
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_element["elements"].append(element.get_data())    
    
    def element(self, element):
        self.push(element)
        return self

class FrameCellDecorator:
    """
    simple:
        FrameCellDecorator(True, True, True) -> inner, outer, cont (closes when there is a page break)
    set line thickness and color:
        FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.3).with_color(Color().rgb(210, 105, 30)))
    """
    def __init__(self, inner=False, outer=False, cont=False):
        if type(inner) is not bool or type(outer) is not bool or type(cont) is not bool:
            raise ValueError("expected a bool" )
        self.list_fcell = [inner, outer, cont]
        self.line_style = None
    
    def with_line_style(self, inner, outer, cont, line_style):
        if type(inner) is not bool or type(outer) is not bool or type(cont) is not bool:
            raise ValueError("expected a bool" )
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        self.list_fcell = [inner, outer, cont]
        self.line_style = line_style
        return self
    
    def get_data(self):
        return [self.list_fcell, self.line_style]


class TableLayout(BaseElement):
    def __init__(self, column_weights):
        if type(column_weights) is not list:
            raise ValueError("expected a list")
        self.column_weights = column_weights
        self.dict_element = {"type" : "table_layout", "rows":[], "column_weights": column_weights}
    
    def push_row(self, row):
        if type(row) is not list:
            raise ValueError("expected a list the elements")
        row_data = [x.get_data() for x in row]        
        if len(row_data) != len(self.column_weights):
            raise ValueError("The row count is different from the column count" )
        self.dict_element["rows"].append(row_data)
        
    def set_cell_decorator(self, cell_decorator):
        if type(cell_decorator) is not FrameCellDecorator:
            raise ValueError("expected a FrameCellDecorator")
        list_fcell, line_style = cell_decorator.get_data()
        self.dict_element["frame_decorator"] = list_fcell
        if line_style:
            self.set_frame(line_style)

## HorizontalLayout adaptacion de TableLayout con un solo row, por conveniencia de nombre, en genpdf-js no existe
class HorizontalLayout(BaseElement):
    def __init__(self, column_weights):
        if type(column_weights) is not list:
            raise ValueError("expected a list column weights")
        self.column_weights = column_weights
        self.dict_element = {"type" : "layout", "orientation":"horizontal", 
                             "column_weights": column_weights, "elements":[]}
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if len(self.column_weights) == len(self.dict_element["elements"]):
            raise ValueError("element cannot be added, because it exceeds column_weights")
        self.dict_element["elements"].append(element.get_data())   
    
    def get_data(self):
        d = len(self.column_weights) - len(self.dict_element["elements"])
        if d > 0:
            fix_row = self.dict_element["elements"] + [{"type":"paragraph", "value":[{"text":""}]} for x in range(d)]
            self.dict_element["elements"] = fix_row   
        return self.dict_element
    
class UnorderedList(BaseElement):
    def __init__(self):
        self.dict_element = {"type" : "unordered_list", "elements":[]}
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_element["elements"].append(element.get_data())
    
    def with_bullet(self, bullet):
        if type(bullet) not in [str]:
            raise ValueError("expected str")
        self.dict_element["bullet"] = bullet
        return self
    
    def element(self, element):
        self.push(element)
        return self
        
class OrderedList(BaseElement):
    def __init__(self):
        self.dict_element = {"type" : "ordered_list", "elements":[]}
        # self.with_start(1)
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_element["elements"].append(element.get_data())   
    
    def with_start(self, start):
        if type(start) not in [int]:
            raise ValueError("expected int")
        self.dict_element["start"] = start
        return self
    
    def element(self, element):
        self.push(element)
        return self
        
# Wrappers
class FramedElement:
    def __init__(self, element, line_style):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        if type(element) in [FramedElement, PaddedElement, StyledElement]:
            element = element.element
        
        element.set_frame(line_style)
        self.element = element
        
    def get_data(self):
        return self.element.get_data()
    
class PaddedElement:
    def __init__(self, element, margins):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if type(margins) is not Margins:
            raise ValueError("expected a margins" )
        if type(element) in [FramedElement, PaddedElement, StyledElement]:
            element = element.element
        
        element.set_padding(margins)
        self.element = element
        
    def get_data(self):
        return self.element.get_data()

class StyledElement:
    def __init__(self, element, style):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if type(style) is not Style:
            raise ValueError("expected a Style" )
        if type(element) in [FramedElement, PaddedElement, StyledElement]:
            element = element.element
            
        element.set_style(style)
        self.element = element
        
    def get_data(self):
        return self.element.get_data()

class Paragraph(BaseElement):
    def __init__(self, string_style):
        if type(string_style) not in [str, StyledString]:
            raise ValueError("expected a str o StyledString")
        if type(string_style) is str:
            string_style = StyledString(string_style, Style())            
        self.dict_element = {"type": "paragraph", "value":[string_style.get_data()]}                
    
    def set_alignment(self, alignment):
        if type(alignment) is not str:
            raise ValueError("expected str")
        if alignment not in Alignment.get_values():
            raise ValueError("expected Alignment values")
        self.dict_element["alignment"] = alignment
    
    def aligned(self, alignment):
        self.set_alignment(alignment)
        return self
    
    def push(self, string_style):
        if type(string_style) not in [str, StyledString]:
            raise ValueError("expected a str o StyledString")
        if type(string_style) is str:
            string_style = StyledString(string_style)
        if not "value" in self.dict_element:
            self.dict_element["value"] = []
        self.dict_element["value"].append(string_style.get_data())
    
    def string(self, string_style):
        self.push(string_style)
        return self
    
    def push_styled(self, s, style):
        if type(s) is not StyledString:
            raise ValueError("expected a StyledString")
        if type(s) is not str:
            raise ValueError("expected a str")
        self.push(StyledString(s, style))        
    
    def styled_string(self, s, style):
        self.push_styled(s, style)
        return self
    
    def set_style(self, style):
        if type(style) is not Style:
            raise ValueError("expected a Style")
        if not "value" in self.dict_element:
            self.dict_element["value"] = [StyledString("",style).get_data()]
        else:
            last_index = len(self.dict_element["value"])-1
            last_value = self.dict_element["value"][last_index]
            self.dict_element["value"][last_index] = StyledString(last_value["text"], style).get_data()
    
    def set_bullet(self, bullet):
        if type(bullet) is not str:
            raise ValueError("expected a str")
        self.dict_element["bullet"] = bullet
    
    def with_bullet(self, bullet):
        self.set_bullet(bullet);
        return self
    
    def get_data(self):
        return self.dict_element

# a single line of text, not alignment
class Text(BaseElement):
    def __init__(self, string_style):
        if type(string_style) not in [str, StyledString]:
            raise ValueError("expected a str o StyledString")
        if type(string_style) is str:
            string_style = StyledString(string_style, Style()) 
        text = string_style.text
        style = string_style.style
        self.dict_element = {"type": "text", "value": text, "style":style}                
            
    def set_bullet(self, bullet):
        if type(bullet) is not str:
            raise ValueError("expected a str")
        self.dict_element["bullet"] = bullet
    
    def with_bullet(self, bullet):
        self.set_bullet(bullet);
        return self

    
class Margins:
    def __init__(self, top=0.1, right=0.1, bottom=0.1, left=0.1):
        self.list_padding = [top, right, bottom, left]            
    
    def trbl(self, top, right, bottom, left):
        self.list_padding = [top, right, bottom, left]
        return self
    
    def vh(self, vertical, horizontal):
        self.list_padding = [vertical, horizontal, vertical, horizontal]
        return self
    
    def all(self, padding):
        if type(padding) not in [float, int]:
            raise ValueError("expected a float or int")
        padding = float(padding)
        self.list_padding = [padding, padding, padding, padding]     
        return self
    
    def get_data(self):
        return self.list_padding


class Style:
    def __init__(self):
        self._bold = None
        self._size = None
        self._fit_size_to = None
        self._italic = None
        self._font_family = None
        self._color = None
        self._line_spacing = None
        self.dict_style={}
    
    def set_italic(self):
        self._italic = True
        
    def italic(self):
        self.set_italic()
        return self
    
    def set_bold(self):
        self._bold = True
        
    def bold(self):
        self.set_bold()
        return self
    
    def set_line_spacing(self, line_spacing):
        if type(line_spacing) not in [float, int]:
            raise ValueError("expected a float or int")
        self._line_spacing = float(line_spacing)
        
    def with_line_spacing(self, line_spacing):
        self.set_line_spacing(line_spacing)
        return self
    
    def set_font_size(self, font_size):
        if type(font_size) is not int:
            raise ValueError("expected a int")
        self._size = font_size
    
    def with_font_size(self, font_size):
        self.set_font_size(font_size)
        return self
    
    # Adjust the size to a minimum value if it is exceeded in the layout.
    def set_fit_size_to(self, font_size):
        if type(font_size) is not int:
            raise ValueError("expected a int")
        self._fit_size_to = font_size
    
    #Adjust the size to a minimum value if it is exceeded in the layout.
    def with_fit_size_to(self, font_size):
        self.set_fit_size_to(font_size)
        return self
    
    def set_font_family(self, font_family):
        if type(font_family) is not str:
            raise ValueError("expected a str")
        self._font_family = font_family
        
    def with_font_family(self, font_family):
        self.set_font_family(font_family)
        return self
    
    def set_color(self, color):
        if type(color) is not Color:
            raise ValueError("expected a Color")
        self._color = color.get_data()
        
    def with_color(self, color):
        self.set_color(color)
        return self
    
    def update_style(self):
        if self._bold:
            self.dict_style["bold"]=self._bold
        if self._size:
            self.dict_style["size"]=self._size
        if self._fit_size_to:
            self.dict_style["fit_size_to"]=self._fit_size_to
        if self._italic:
            self.dict_style["italic"]=self._italic
        if self._font_family:
            self.dict_style["font_family"]=self._font_family
        if self._color:
            self.dict_style["color"]=self._color
        if self._line_spacing:
            self.dict_style["line_spacing"]=self._line_spacing
            
    def get_data(self):
        self.update_style()
        return self.dict_style


class Color:
    def __init__(self):
        self._rgb = None
        self._cmyk = None
        self._greyscale = None        
        
    def min_max(self, x):
        if x < 0:
            return 0
        if x > 255:
            return 255
        return x
        
    #An RGB color with red, green and blue values between 0 and 255.
    def rgb(self, r, g, b):
        if type(r) is not int or type(g) is not int or type(b) is not int:
            raise ValueError("expected a int")
        self._rgb = [self.min_max(r), self.min_max(g), self.min_max(b)]
        return self
    
    #An CMYK color with cyan, magenta, yellow and key values between 0 and 255.
    def cmyk(self, c, m, y, k):
        if type(c) is not int or type(m) is not int or type(y) is not int or type(k) is not int:
            raise ValueError("expected a int")
        self._cmyk = [self.min_max(c), self.min_max(m), self.min_max(y), self.min_max(k)]
        return self
    
    #A greyscale color with a value between 0 and 255.
    def greyscale(self, g):
        if type(g) is not int:
            raise ValueError("expected a int")
        self._greyscale = self.min_max(g)
        return self
    
    def get_data(self):
        if self._rgb:
            return {"type":"rgb", "value":self._rgb}
        if self._cmyk:
            return {"type":"cmyk", "value":self._cmyk}
        if self._greyscale:
            return {"type":"greyscale", "value":self._greyscale}
        return {}


class StyledString:
    __name__ = "StyledString"
    def __init__(self, s="", style=Style()):
        self.text = {"text": s}
        try:
            self.style = style.get_data()
        except:
            self.style = {}
        self.dict_styled_string = {**self.text, **self.style}
    
    def get_data(self):
        return self.dict_styled_string


class Alignment:
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    
    @classmethod
    def get_values(self):
        return ["left", "center", "right"]
      

class LineStyle:
    def __init__(self):
        self._thickness = 0.1
        self._color = None
        self._dash = 0
        self.dict_line_style = {"thickness": self._thickness}
        
    def set_thickness(self, thickness):
        if type(thickness) not in [float, int]:
            raise ValueError("expected a float or int")
        self._thickness = float(thickness)
        self.dict_line_style["thickness"] = self._thickness
        
    def with_thickness(self, thickness):
        self.set_thickness(thickness)
        return self
    
    def set_color(self, color):
        if type(color) is not Color:
            raise ValueError("expected a type Color")
        self._color = color.get_data()
        self.dict_line_style["color"] = self._color
    
    def with_color(self, color):
        self.set_color(color)
        return self
    
    def set_dash(self, dash):
        if type(dash) not in [float, int]:
            raise ValueError("expected a float or int")
        self._dash = float(dash)
        self.dict_line_style["dash"] = self._dash
        
    def with_dash(self, dash):
        self.set_dash(dash)
        return self
    
    def get_data(self):
        return self.dict_line_style
    
class Size:
    def __init__(self, w = None, h = None):
        if w == None and h == None:
            self.size = "A4"
        else:
            if type(w) is not [int, float] or type(h) is not [int, float]:
                raise ValueError("expected a int or float")
            self.size = [abs(w), abs(h)]
    
    def A4(self):
        self.size = "A4"
        return self
    
    def Legal(self):
        self.size = "Legal"
        return self
        
    def Letter(self):
        self.size = "Letter"
        return self
        
    def get_data(self):
        return self.size

ELEMENTS = [VerticalLayout, HorizontalLayout, TableLayout, OrderedList, UnorderedList, 
            Paragraph, Image, Text, StyledElement, PaddedElement, FramedElement,
            PageBreak, Break]
