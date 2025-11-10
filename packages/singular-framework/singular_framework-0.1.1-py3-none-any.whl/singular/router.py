import os
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

from flask import (
    Flask,
    request,
    url_for,
    redirect,
    Blueprint,
    render_template,
    send_file
)

from .utils import APP_START_PATH

class Router():

    """ Rotas basedo em arquibos """

    def __init__(self, app:Flask, path:os.path="pages" ):
        self.base_path = path
        self.caminho = app.app_path
        
        self.routes = app.routes
        self.app = app


        base = Path(self.caminho)

        # rotas com base nas pastas
        for page in base.rglob("*/page.py"):
            if page.is_file:
                route = page.parent.name

                if route == "index":
                    app.add_url_rule(f"/", view_func=self.view_app)
                    app.routes[route] = page

                else:
                    app.add_url_rule(f"/{route}/", view_func=self.view_app)
                    app.routes[route] = page.absolute()
        
        # rotas do backend
        for server in base.rglob("*/*.api.py"):
            if server.is_file:
                os.system("clear")

                # carregar modulo
                name_module = server.stem.replace(".", "_")
                spec = spec_from_file_location(name_module, server)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                # 
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, Blueprint):
                        app.register_blueprint(obj)
                    
        self.routes = app.routes

        # rota publica para pagina home
        app.add_url_rule("/assets/<filename>", view_func=self.routes_assets)

        # rota pa enviar o codigo python no frontend
        app.add_url_rule("/ui/<route>", view_func=self.ui)

    def ui(self, route:str):
        base = Path(self.caminho)
        
        if route in self.routes:
            return send_file(self.routes[route], mimetype="text/python")
        return "Arquivo Não Encontrado"

    def view_app(self):

        nome = str(request.url_rule).replace("/", "")
        if nome == "": nome = "index"

        return render_template("base.html", route=nome, title=self.app.title)

    def routes_assets(self, filename:str):
        base = Path(self.caminho)
        for file in base.rglob("assets/*"):
            if filename == file.name and file.is_file:
                return send_file(file.absolute())

        return "Arquivo Não Encontrado"


class Route(Blueprint):
    def __init__(self, name, import_name=__name__, static_folder = None, static_url_path = None, template_folder = None, subdomain = None, url_defaults = None, root_path = None, cli_group = ...):
        
        super().__init__(
            name, 
            import_name, 
            static_folder, 
            static_url_path, 
            template_folder, 
            f"/api/{name}", #url_prefix, 
            subdomain, 
            url_defaults, 
            root_path, 
            cli_group
        )

        caminho = Path(APP_START_PATH)

        self.request = request
    
    
        #self.add_url_rule(f"/api/{route}", view_func=callback, methods=["GET"])
    def get(self, route:str):

        def decorator(f):
            self.add_url_rule(route, view_func=f, methods=["GET"])
            return f
        return decorator

    
    def post(self, route:str):
        def decorator(f):
            self.add_url_rule(route, view_func=f, methods=["POST"])
            return f
        return decorator
    



        


