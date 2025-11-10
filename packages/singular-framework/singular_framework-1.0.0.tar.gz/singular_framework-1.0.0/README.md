# Singular

Singular é um Framework Desenvolvido para facilidar o desenvolvimento de aplicativo Web usando apenas python com Interfaces reativas sistema de rontas com base em Diretorios

## Instalação
Instalar o singular e simples Sem muito segredo basta Rodar o comando no Terminal e já esta.
### pip
```sh
pip install singular
```

## Linha de Comando

### Iniciar um Projeto Singular Ficou mais simples
```sh
singular init
```
Esse Comando vai criar uma estrutura no modelo MVC: Model, View e Cntroller
Nota Esse padrão pode ser mudado o singular da essa liberdade
### Rodar o projeto
```sh
singular start
```
Esse comando iniciara um servidor Flask de Desenvolvimento


## Exempo de Usuo

Isso Inicia um aplicativo È basicamento um Objeto __Flask__ ex: app = Flask(...)
```python
from singular import Singular


app = Singular(__name__)
```

## criar uma pagina

```python
from singular import (
    View,
    Text,
    Button,
    Link,
    Render,
    Component,
    Style,
    Link,
    Img
)


class Contador(Component):
    def __init__(self):
        super().__init__()
        self.state = {'count': 0}
    
    def increment(self):
        self.state['count'] += 1
        self.set_state(self.state)
    
    def render(self):
        return View(
            Text("Um Contador simples feito em Singular"),
            
            Button(
                f"Contador: {self.state['count']}", 
                on_click=self.increment,
                style=Style(
                    padding=".8rem",
                    font_size=".8rem",
                    background_color="blue",
                    color="#FFF",
                    border="none",
                    border_radius="0.5rem",
                    cursor="pointer",
                    font_weight="bold",
                )
            ),
            Link(
                "Ir Para o Lista de tarefa",
                href="/"
            ),
            style=Style(
                display="flex",
                flex_direction="column",
                gap="20px",
                padding="20px",
                width="100%",
                height="100dvh",
                align_items="center",
                justify_content="center",
                background_color="#111827",
                color="#FFF",
            )
            
        )



Render(
    Contador(),
)
```




