from singular import *


from browser import window

def on_hash_change(ev):
    hash_value = window.location.hash

    hash_value = "index" if hash_value.replace("/", "").replace("#", "") == "" else hash_value.replace("/", "").replace("#", "")

   

    script = html.SCRIPT(src=f"/ui/{hash_value}")
    #script.id = "view_atual"
    script.type = "text/python"
    document <= script

window.bind("hashchange", on_hash_change)
