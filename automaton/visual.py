import urllib.request
import pickle
import os
import webbrowser
from typing import Dict
import networkx as nx
from html.parser import HTMLParser

from pyvis.network import Network
from .automaton import Automaton

class ResourceEmbedder(HTMLParser):

    def __init__(self,cache:Dict[str,str]={}):
        super().__init__()
        self._output = []
        self._current_tag = None
        self._attrs = None
        self._skip_until_end = False
        self._cache = cache
    
    def _download(self,url:str) -> str:
        response = urllib.request.urlopen(url)
        content = response.read().decode()
        response.close()
        return content
    
    def _build_start_tag(self, tag:str, attrs:list[tuple[str, str | None]]):
        attr_str = ''.join(f' {k}="{v}"' for k, v in attrs)
        return f'<{tag}{attr_str}>'

    @property
    def output(self) -> str:
        return ''.join(self._output)
    
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        
        attr_dict = dict(attrs)

        if tag == 'link' and attr_dict.get('rel') == 'stylesheet' and attr_dict.get('href', '').startswith('http'):  # type: ignore

            href:str = attr_dict['href']  # type: ignore
            css_file = href[href.rindex('/') + 1:]
            if not css_file in self._cache:
                self._cache[css_file] = self._download(href)
            css_content = self._cache[css_file]
            self._output.append(f'<style> /* {href}*/\n{css_content}\n</style>\n')
            self._skip_until_end = True
            return

        if tag == 'script' and attr_dict.get('src', '').startswith('http'): # type: ignore

            src:str = attr_dict['src'] # type: ignore
            js_file = src[src.rindex('/') + 1:]
            if not js_file in self._cache:
                self._cache[js_file] = self._download(src)
            js_content = self._cache[js_file]
            self._output.append(f'<script>/* {src} */\n{js_content}\n</script>\n')
            self._skip_until_end = True
            return
        
        self._current_tag = tag
        self._attrs = attrs
        self._output.append(self._build_start_tag(tag,attrs))
    
    def handle_endtag(self, tag: str) -> None:
        if self._skip_until_end:
            self._skip_until_end = False
            return
        self._output.append(f'</{tag}>\n')
    
    def handle_data(self, data: str) -> None:
        if self._skip_until_end:
            return
        self._output.append(data)
    
    def handle_entityref(self, name: str) -> None:
        if self._skip_until_end:
            return
        self._output.append(f'&{name};')
    
    def handle_charref(self, name: str) -> None:
        if self._skip_until_end:
            return
        self._output.append(f'&#{name};')

def _to_graph(automaton:Automaton) -> nx.DiGraph:
    G = nx.DiGraph()

    transitions = automaton.transition_function
    epsilon_transitions = automaton.epsilon_transitions

    for transition,destination in transitions.items():
        f,symbol = transition
        if not (f,destination) in G.edges:
            G.add_edge(f,destination)
            G.edges[f,destination]["label"] = symbol
        else:
            G.edges[f,destination]["label"] += f',{symbol}'
    
    for origin,destinations in epsilon_transitions.items():
        for destination in destinations:
            G.add_edge(origin,destination)
            G.edges[origin,destination]['dashes'] = True
    
    for state in automaton.states:

        if state == automaton.start_state:
            G.nodes[state.id]['color'] = {'background':'white','border':'green' if state.is_accept else 'black'}
        elif state.is_accept:
            G.nodes[state.id]['color'] = 'green'
        
        G.nodes[state.id]['label'] = f'{state.value}'
        G.nodes[state.id]['title'] = f'id: {state.id}'
    
    return G

def draw_automaton(automaton:Automaton,filename:str | None=None,show:bool=True,cache_file:str|None=None,**kwargs) -> None:
    '''
    Args:
        automaton (Automaton): automaton to draw
        filename (str): filename of the output file with the automaton drawed
        interactive (bool): tells if the graphic is interactive (nx-vis-visualizer in web),
            or a figure of matplotlib
        
        kwargs (dict): optional values
            physics:bool
            select_menu:bool
            filter_menu:bool
            nodes:bool
            edges:bool
            as_tree:bool

    Returns:
        None: creates an interactive graphic showing the automaton
    '''
    physics = kwargs.get('physics',False)
    filters = []
    if not isinstance(physics,bool):
        raise ValueError('physics argument must be a boolean value')
    select_menu = kwargs.get('select_menu',False)
    if not isinstance(select_menu,bool):
        raise ValueError('select_menu argument must be a boolean value')
    filter_menu = kwargs.get('filter_menu',False)
    if not isinstance(filter_menu,bool):
        raise ValueError('filter_menu argument must be a boolean value')
    nodes = kwargs.get('filter_menu',False)
    if not isinstance(nodes,bool):
        raise ValueError('nodes argument must be a boolean value')
    edges = kwargs.get('filter_menu',False)
    if not isinstance(edges,bool):
        raise ValueError('edges argument must be a boolean value')
    as_tree = kwargs.get('as_tree',False)

    if physics:
        filters.append('physics')
    if nodes:
        filters.append('nodes')
    if edges:
        filters.append('edges')

    G = _to_graph(automaton)
    if not filename:
        filename = f'automaton-{automaton.id}'
    
    net = Network(directed=True,height='100vh',width='100%',bgcolor='white',select_menu=select_menu,filter_menu=filter_menu,layout=as_tree)
    if filters:
        net.show_buttons(filter_=filters)

    for node_id,node_attrs in G.nodes(data=True):

        color = node_attrs.get('color',None)
        label = node_attrs.get('label',str(node_id))
        title = node_attrs.get('title','')

        net.add_node(node_id,label=label,title=title,color=color)
    
    for u,v,edge_attrs in G.edges(data=True):
        label = edge_attrs.get('label','')
        dashes = edge_attrs.get('dashes',False)

        net.add_edge(u,v,label=label,dashes=dashes)
    
    output_path = f'{filename}.html'
    if cache_file:
        cache = {}
        if os.path.exists(cache_file):
            with open(cache_file,'rb') as f:
                cache = pickle.load(f)
        html = net.generate_html(output_path)
        embedder = ResourceEmbedder(cache)
        embedder.feed(html)
        if not os.path.exists(cache_file):
            with open(cache_file,'wb') as f:
                pickle.dump(cache,f)
        html = embedder.output
        with open(output_path,'w',encoding='utf-8') as f:
            f.write(html)
    else:
        net.save_graph(output_path)
    
    if show:
        webbrowser.open(output_path,2)