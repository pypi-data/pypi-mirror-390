import os
import importlib
from flask import Flask


from .utils import BASE_PATH, APP_START_PATH
from .router import Router



class Singular(Flask):
    def __init__(self, import_name=__name__, title="Singular", static_url_path = None, static_host = None, host_matching = False, subdomain_matching = False, instance_path = None, instance_relative_config = False, root_path = None):
        
        static_folder   = os.path.join(BASE_PATH, "static")
        template_folder = os.path.join(BASE_PATH, "templates")
        self.app_path = os.getcwd()
        self.routes = {}
        self.title = title
        
        
        super().__init__(
            import_name, 
            static_url_path, 
            static_folder, 
            static_host, 
            host_matching, 
            subdomain_matching, 
            template_folder, 
            instance_path, 
            instance_relative_config, 
            root_path
        )


        Router(self)
    
   

