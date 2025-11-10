try: from browser import document, html, window, ajax
except: pass

from typing import Literal
import inspect, json

# Guarda componentes montados
_components = {}


class Style():
    def __init__(self,
        flex_direction:Literal["row", "column", "row-reverse", "column-reverse"]=None,
        justify_content:Literal["flex-start", "flex-end", "center", "space-between", "space-around", "space-evenly"]=None,
        align_items:Literal["flex-start", "flex-end", "center", "stretch", "baseline"]=None,
        display:Literal["flex", "grid", "block", "inline-block", "none"]=None,
        grid_template_columns:str=None,
        grid_template_rows:str=None,
        gap:str=None,
        background_color:str=None,
        padding:str=None,
        margin:str=None,
        width:str=None,
        height:str=None, border:str=None,
        border_radius:str=None,
        color:str=None, font_size:str=None,
        font_weight:Literal["normal", "bold", "bolder", "lighter"]=None,
        text_align:Literal["left", "right", "center", "justify"]=None,
        opacity:str=None,
        cursor:Literal["auto", "default", "pointer", "text", "move", "not-allowed"]=None,
        position:Literal["static", "relative", "absolute", "fixed", "sticky"]=None,
        top:str=None, bottom:str=None,
        left:str=None, right:str=None,
        z_index:str=None,
        transition:str=None,
        transform:str=None,
        animation:str=None,
        border_collapse:Literal["collapse", "separate"]=None,
        min_width="auto",
        max_width="auto",
        min_height="auto",
        max_height="auto",
        ):
        args = inspect.getfullargspec(self.__init__).args
        self.data_attr_ = {arg: locals()[arg] for arg in args if arg != "self"}

        self.style = self.render_style()

        
    def render_style(self):
        style_str = {}
        for k, v in self.data_attr_.items():
            style_str[k.replace("_", "-")] = v
        return style_str

    def __str__(self):
        return "Style Component"


# Requisição

class Request:
    def __init__(
        self,
        url: str,
        method:Literal["GET", "POST"] = "GET",
        data=None,
        files=None,
        on_success=None,
        on_error=None,
    ):
        self.url = url
        self.method = method.upper()
        self.data = data
        self.files = files
        self.on_success = on_success
        self.on_error = on_error

        self.send_request()

    def send_request(self):
        req = ajax.ajax()
        req.bind("complete", self.handle_response)
        req.bind("error", self.handle_error)

        req.open(self.method, self.url, True)

        # Se tiver arquivos → FormData
        if self.files:
            form = html.FormData()

            # arquivos
            for key, file in self.files.items():
                form.append(key, file)

            # dados normais também
            if self.data:
                for k, v in self.data.items():
                    form.append(k, v)

            req.send(form)
            return

        # Se for JSON
        req.set_header("Content-Type", "application/json")
        req.send(json.dumps(self.data or {}))

    def handle_response(self, req):
        # Detecta JSON automaticamente
        try:
            resp = json.loads(req.text)
        except:
            resp = req.text

        if 200 <= req.status < 300:
            if self.on_success:
                self.on_success(resp)
        else:
            if self.on_error:
                self.on_error(req.status, resp)

    def handle_error(self, req):
        if self.on_error:
            self.on_error(req.status, "Erro de rede")


class Element:
    def __init__(self, name="div", content="", childs=None, style=Style(), attrs=None):
        self.name = name
        self.content = content
        self.childs = childs or []
        self.style = {}

        self.attrs = attrs or {}
        self._el = None  # elemento real Brython

    def add_child(self, element: "Element"):
        self.childs.append(element)

    def set_style(self, key: str, value: str):
        self.style[key] = value

    def set_attr(self, key: str, value: str):
        self.attrs[key] = value

    def on(self, event: str, handler):
        """Associa um evento Brython (ex: 'click') a uma função Python."""
        if self._el:
            self._el.bind(event, handler)
        else:
            # guarda pra associar depois de renderizar
            self.attrs[f"on_{event}"] = handler

    def render(self):
        """Cria o elemento real do Brython"""
        el = getattr(html, self.name.upper(), html.DIV)()
        self._el = el

        if self.content:
            el <= self.content

        # aplica estilos
        for k, v in self.style.items():
            el.style[k] = v

        # aplica atributos e eventos
        for k, v in self.attrs.items():
            if callable(v):  # evento atrasado
                el.bind(k.replace("on_", ""), v)
            else:
                el.attrs[k] = v

        # renderiza filhos
        for child in self.childs:
            el <= child.render()

        return el

class Component:
    def __init__(self):
        self.state = {}
        self.element = None

    def set_state(self, new_state: dict):
        self.state.update(new_state)
        self.update()

    def render(self) -> Element:
        raise NotImplementedError

    def mount(self):
        root = self.render()
        self.element = root
        return root.render()

    def update(self):
        new_root = self.render().render()
        old_root = self.element._el
        old_root.replaceWith(new_root)
        self.element._el = new_root


class Render:
    def __init__(self, *components: Component):
        # Monta o componente automaticamente
        document["app"].clear()
        for component in components: document["app"] <= component.mount()

class BaseElement(Element):
    def __init__(self, name="div", content="", childs=None, style=None, attrs=None):
        super().__init__(name, content, childs, style, attrs)

    
    def on_click(self, callback:list["function"]):
        self.on("click", lambda e: callback())

    def on_change(self, callback=None):
        self.on("change", callback)
    
    def on_hover(self, callback=None):
        self.on("hover", lambda e: callback())

class View(BaseElement):
    """ vai servir como uma caixa onde teras as direções de leyout flex ou grid """
    def __init__(self,*elements:list[Element], className:str="", id:str="", style:Style=Style()):
        super().__init__(
            name="div",
            childs=elements,
            attrs={"class": className, "id": id},
        )

        self.style = style.style
        


class Text(BaseElement):
    def __init__(self, text:str, className:str="", id:str="", style:Style=Style()):
        super().__init__(
            name="span",
            content=text,
            attrs={"class": className, "id": id}
        )
        self.style = style.style

class Button(BaseElement):
    def __init__(self, text:str, on_click=None, className:str="", id:str="", style:Style=Style()):
        super().__init__(name="button", content=text, attrs={"class": className, "id": id})
        self.style = style.style

        if on_click: self.on_click(on_click)



class Input(BaseElement):
    def __init__(self, placeholder:str="", on_change=None, id="", type:Literal["text", "file", "checkbox", "radio"]="text", className:str="", value:str="", style:Style=Style()):
        super().__init__(
            name="input",
            attrs={"placeholder": placeholder, "type": type, "value": value, "class": className, "id": id}
        )
        self.value = ""

        

        self.style = style.style
        if on_change: 
            self.on("keyup", on_change)
            #self.on("change", on_change)

class Link(BaseElement):
    def __init__(self, text:str, href="", className:str="", *elements:Element):

        super().__init__(name="a", content=text, attrs={"href": f"#{href}", "class": className})
        self.childs = elements
        self.href = "index" if href.replace("/", "") == "" else href.replace("/", "")

        self.on("click", self.click)
    
    def click(self, e):
        #document["app"].clear()
        
        for s in document.select("script[type='text/python']"):
            if s.id == "view_atual":
                s.remove()

        script = html.SCRIPT(src=f"/ui/{self.href}")
        #script.id = "view_atual"
        script.type = "text/python"
        document <= script

class Table(BaseElement):
    def __init__(self, headers:list[str], rows:list[list[str]], className:str="", id:str="", style:Style=Style()):
        super().__init__(
            name="table",
            attrs={"class": className, "id": id}
        )
        self.style = style.style

        thead = Element(name="thead")
        header_row = Element(name="tr")
        for header in headers:
            header_row.add_child(Element(name="th", content=header))
        thead.add_child(header_row)
        self.add_child(thead)

        tbody = Element(name="tbody")
        for row in rows:
            row_el = Element(name="tr", style=Style(
                padding="10px",
                background_color="red"
            ))
            for cell in row:
                row_el.add_child(Element(name="td", content=cell, style=Style(
                    padding="1rem",

                )))
            tbody.add_child(row_el)
        self.add_child(tbody)

class ComboBox(BaseElement):
    def __init__(self, options:list[str], on_change=None, className:str="", id:str=""):
        super().__init__(
            name="select",
            attrs={"class": className, "id": id}
        )

        for option in options:
            self.add_child(Element(name="option", content=option, attrs={"value": option}))

        if on_change: self.on_change(on_change)

class Img(BaseElement):
    def __init__(self, src:str="", alt="", style:Style=Style(), className:str="", id:str=""):
        super().__init__(
            "img", 
            attrs={
                "class": className, 
                "id": id, 
                "alte": all, 
                "src": src
            }
        )

        self.style = style.style





