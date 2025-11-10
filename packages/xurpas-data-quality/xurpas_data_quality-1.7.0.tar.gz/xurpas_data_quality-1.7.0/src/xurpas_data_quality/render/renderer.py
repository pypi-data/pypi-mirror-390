from abc import ABC, abstractmethod
from typing import Any, Dict,List
from visions import VisionsBaseType

from xurpas_data_quality.render.template_loader import template

class BaseRenderer(ABC):
    def __init__(self, content: Dict[str, Any], name: str = None, id:str=None, type:VisionsBaseType=None, config:dict=None,**kwargs):

        self.content = content
        self.kwargs = kwargs

        if name is not None:
            self.content['name'] = name
        
        if config is not None:
            self.content['config'] = config

        if id is not None:
            self.content['id'] = id

        if type is not None:
            self.type = type
        

    @property
    def name(self) -> str:
        return self.content.get('name', None)
    
    @property
    def id(self) -> str:
        return self.content.get('id', None)

    @abstractmethod
    def render(self) -> Any:
        pass

class HTMLTable(BaseRenderer):
    """Renders a Table"""
    def __init__(self, data:Any=None, id:str=None, name:str=None, headers:List[str]=None, config:list|dict=None,**kwargs):
        self.kwargs = kwargs
        super().__init__(id=id, name=name, config=config,content={'data': data, 'headers': headers}, **kwargs)

    def render(self):
        if self.kwargs:
            return template("table.html").render(**self.content, **self.kwargs)
        else:
            return template("table.html").render(**self.content)
        
class HTMLToggle(BaseRenderer):
    """Renders a Toggle Button"""
    def __init__(self, text:str, id:str, **kwargs):
        super().__init__( content={'text': text, 'id': id}, **kwargs)

    def render(self):
        return template("toggle.html").render(**self.content)
        
class HTMLCollapse(BaseRenderer):
    """Renders a collapsing block. 
    Needs a HTMLToggle class initialized"""
    def __init__(self, button: HTMLToggle, body:Any, **kwargs):
        super().__init__({'button':button, 'body':body}, **kwargs)
    
    def render(self):
        return template("collapse.html").render(**self.content)
    
class HTMLVariable(BaseRenderer):
    """Renders the variable section of the report"""
    def __init__(self, name, body, bottom=None, **kwargs):
        super().__init__({"variable_name":name, "variable_body": body, "variable_bottom": bottom}, **kwargs)

    def render(self):
        return template("variable.html").render(name = self.content['variable_name'], bottom=self.content['variable_bottom'], content = self.content['variable_body'], type=self.type)
    
class HTMLPlot(BaseRenderer):
    """Renders any images"""
    def __init__(self, plot:Any, type="small", **kwargs):
        super().__init__({"plot": plot}, **kwargs)

        if type !="small" and type !="large" and type!='categorical':
            raise ValueError("Plot type should be either 'small' or 'large' or 'categorical'")
        else:
            self.type=type

    def render(self):
        return template("plot.html").render(**self.content, type=self.type)
    

class HTMLDropdown(BaseRenderer):
    """Renders a dropdown menu and the javascript for the dropdown"""
    def __init__(self, id:str, dropdown_items: List[str], dropdown_content: Any,name:str=None, **kwargs):
        super().__init__(
                        {
                            'dropdown_items': dropdown_items,
                            'dropdown_content': dropdown_content
                        },
                        name,
                        id,
                        **kwargs)
    def render(self):
        return template("dropdown.html").render(**self.content)

class HTMLText(BaseRenderer):
    """Just Text"""
    def __init__(self, text:List[str]=None, **kwargs):
        if not isinstance(text,list):
            text = [text]
        super().__init__(content={'text':text}, **kwargs)

    def render(self):
        return template("text.html").render(content = self.content, **self.kwargs)

class HTMLContainer(BaseRenderer):
    """Renders different containers for the report"""
    def __init__(self, type:str, container_items:list, name:str=None, id:str=None, col=None, **kwargs):
        super().__init__({'container_items':container_items, 'name': name, 'id':id, 'col':col}, **kwargs)
        self.type = type
        self.kwargs = kwargs
        
    def render(self):
        if self.type == 'box':
            return template("containers/box.html").render(container_items=self.content['container_items'], **self.kwargs)
        elif self.type == 'column':
            return template("containers/column.html").render(container_items=self.content['container_items'], **self.kwargs)
        elif self.type == 'sections':
            return template("containers/sections.html").render(
                container_items=self.content['container_items'], **self.kwargs)
        elif self.type == 'tabs':
            return template("containers/tabs.html").render(**self.content, **self.kwargs)
        elif self.type == 'default':
            return template("containers/default.html").render(**self.content, **self.kwargs)
        elif self.type == 'test':
            return template("containers/test.html").render(**self.content, **self.kwargs)
        else:
            raise ValueError(f"unknown Container ({self.type}) type!")

class HTMLBase(BaseRenderer):
    """Renders the base report"""
    def __init__(self, body: Any, name: str, **kwargs):
        if name is None:
            name = "Profile Report"
        super().__init__(content={"body":body}, name=name, *kwargs)

    def render(self, **kwargs) -> str:
        nav_items = [self.content['name']]
        return template("base.html").render(**self.content, nav_items=nav_items, **kwargs)