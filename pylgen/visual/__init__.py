import urllib.request
import pickle
import os
import webbrowser
from typing import Any, Dict, Tuple
import networkx as nx
from html.parser import HTMLParser
import json
import hashlib

from pyvis.network import Network
from ..automaton.automaton import Automaton
from ..lexer.base_lexer import BaseLexer
from ..parser.parser import ParseTreeNode, Parser
from ..common.types import AST
from ..grammar.grammar import Grammar

from .table import build_propagation_edges_table

CACHE_FILE:str | None = None

class ResourceEmbedder(HTMLParser):

    def __init__(self,cache:Dict[str,str]={}):
        super().__init__()
        self._output = []
        self._current_tag = None
        self._attrs = None
        self._skip_until_end = False
        self._cache = cache
    
    def _download(self,url:str) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url,headers=headers)
        response = urllib.request.urlopen(req)
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

class JsonSerializer(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o,(set,frozenset)):
            return list(o)
        return super().default(o)

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

def _is_json_serializable(obj:Any) -> bool:
    if not obj and type(obj) not in [int,bool]:
        return False
    try:
        s = json.dumps(obj,cls=JsonSerializer)
        return True
    except Exception:
        return False

def _ast_to_graph(ast_root:AST) -> nx.DiGraph:
    G = nx.DiGraph()

    stack = [
        (
            ast_root,
            list(
                filter(
                    lambda _attr:not _attr.startswith('_') and _attr != 'symbol' and _is_json_serializable(ast_root.__getattribute__(_attr)),
                    dir(ast_root)
                    )
                ),
            0,
            0,
        )
    ]
    asts = {}
    asts_levels = {}
    ast_attrs = {}
    while stack:
        entered = False
        ast,attrs,index,level = stack[-1]
        from_node = f'{ast.line}-{ast.column}-{level}'
        childs = ast.children()
        for i in range(index,len(childs)):
            child = childs[i]
            to_node = f'{child.line}-{child.column}-{level + 1}'
            G.add_edge(from_node,to_node)
            if not from_node in asts:
                asts[from_node] = ast
            if not from_node in asts_levels:
                asts_levels[from_node] = level
            if not to_node in asts:
                asts[to_node] = child
            if not to_node in asts_levels:
                asts_levels[to_node] = level + 1
            if not from_node in ast_attrs:
                ast_attrs[from_node] = list(
                    filter(
                        lambda _attr:not _attr.startswith('_') and _attr != 'symbol' and _is_json_serializable(ast.__getattribute__(_attr)),
                        dir(ast)
                    )
                )
            if not to_node in ast_attrs:
                ast_attrs[to_node] = list(
                    filter(
                        lambda _attr:not _attr.startswith('_') and _attr != 'symbol' and _is_json_serializable(child.__getattribute__(_attr)),
                        dir(child)
                    )
                )
            stack[-1] = ast,attrs,i + 1,level
            top = child,list(filter(lambda _attr:not _attr.startswith('_') and _attr != 'symbol' and _is_json_serializable(child.__getattribute__(_attr)),dir(child))),0,level + 1
            stack.append(top)
            entered = True
            break
        if not entered:
            stack.pop()

    if len(G.edges) == 0:
        node = f'{ast_root.line}-{ast_root.column}'
        G.add_node(node)
        asts[node] = ast_root
        ast_attrs[node] = list(
            filter(
                lambda _attr:not _attr.startswith('_') and _attr != 'symbol' and _is_json_serializable(ast_root.__getattribute__(_attr)),
                dir(ast_root)
            )
        )
        asts_levels[node] = 0

    for node in G.nodes:
        n = asts[node]
        level = asts_levels[node]
        attrs = ast_attrs[node]
        G.nodes[node]['label'] = n.symbol.symbol
        title = '\n'.join([f'{attr}: {n.__getattribute__(attr)}' for attr in attrs if not isinstance(n.__getattribute__(attr),AST)])
        G.nodes[node]['title'] = title
        G.nodes[node]['level'] = level
    
    return G

def _get_graph_from_parse_tree(parser:Parser) -> nx.DiGraph:
    G = nx.DiGraph()
    tree = parser.parse_tree
    nodes_by_id:Dict[str,Tuple[ParseTreeNode,int]] = {}

    stack = [(tree,0)]
    while stack:
        current,level = stack.pop()
        current_id = f'{current.symbol}-{current.line}-{current.column}-{level}'
        if not current_id in nodes_by_id:
            nodes_by_id[current_id] = (current,level)
        for children in current.childrens:
            children_id = f'{children.symbol}-{children.line}-{children.column}-{level + 1}'
            stack.append((children,level + 1))
            nodes_by_id[children_id] = (children,level+1)
            G.add_edge(current_id,children_id)
    
    for node in G.nodes:
        n,level = nodes_by_id[node]
        G.nodes[node]['label'] = n.symbol.symbol
        G.nodes[node]['level'] = level

    return G

def draw_automaton(automaton:Automaton,**kwargs) -> None:
    '''
    Args:
        automaton (Automaton): automaton to draw
        
        kwargs (dict): optional values

            filename:str filename of the output file with the automaton drawed
            
            show:bool tells if the result will be opened after created
            
            cache:bool tells if the cache will be used
            
            physics:bool tells if show physics controls
            
            select_menu:bool tells if show select menu controls
            
            filter_menu:bool tells if show filter menu controls
            
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
    nodes = kwargs.get('nodes',False)
    if not isinstance(nodes,bool):
        raise ValueError('nodes argument must be a boolean value')
    edges = kwargs.get('edges',False)
    if not isinstance(edges,bool):
        raise ValueError('edges argument must be a boolean value')
    as_tree = kwargs.get('as_tree',False)
    filename = kwargs.get('filename',f'automaton-{automaton.id}')
    if not isinstance(filename,str):
        raise ValueError('filename must be an string value')
    show = kwargs.get('show',False)
    if not isinstance(show,bool):
        raise ValueError('edges argument must be a boolean value')
    cache = kwargs.get('cache',False)
    if not isinstance(cache,bool):
        raise ValueError('edges argument must be a boolean value')

    if physics:
        filters.append('physics')
    if nodes:
        filters.append('nodes')
    if edges:
        filters.append('edges')

    G = _to_graph(automaton)
    
    net = Network(directed=True,height='100vh',width='100%',bgcolor='white',select_menu=select_menu,filter_menu=filter_menu,layout=as_tree)
    if filters:
        net.show_buttons(filter_=filters)

    for node_id,node_attrs in G.nodes(data=True):

        color = node_attrs.get('color',None)
        label = node_attrs.get('label',str(node_id))
        title = node_attrs.get('title','')

        net.add_node(node_id,label=label,title=title,color=color) # type:ignore
    
    for u,v,edge_attrs in G.edges(data=True):
        label = edge_attrs.get('label','')
        dashes = edge_attrs.get('dashes',False)

        net.add_edge(u,v,label=label,dashes=dashes)
    
    output_path = f'{filename}.html'
    if cache:
        if not CACHE_FILE:
            raise ValueError('cache file not set')
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE,'rb') as f:
                cache = pickle.load(f)
        html = net.generate_html(output_path)

        json_str_or = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest_or = hashlib.sha256(json_str_or.encode()).hexdigest()

        embedder = ResourceEmbedder(cache)
        embedder.feed(html)

        json_str = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest = hashlib.sha256(json_str.encode()).hexdigest()
        
        if not os.path.exists(CACHE_FILE) or digest_or != digest:
            with open(CACHE_FILE,'wb') as f:
                pickle.dump(cache,f)

        html = embedder.output
        with open(output_path,'w',encoding='utf-8') as f:
            f.write(html)
    else:
        net.save_graph(output_path)
    
    if show:
        webbrowser.open(output_path,2)

def draw_lexer(lexer:BaseLexer,**kwargs) -> None:
    '''
    Args:
        automaton (Automaton): automaton to draw
        
        kwargs (dict): optional values

            filename:str filename of the output file with the lexer-automaton drawed
            
            show:bool tells if the result will be opened after created
            
            cache:bool tells if the cache will be used
            
            physics:bool tells if show physics controls
            
            select_menu:bool tells if show select menu controls
            
            filter_menu:bool tells if show filter menu controls
            
            nodes:bool
            
            edges:bool
            
            as_tree:bool

    Returns:
        None: creates an interactive graphic showing the automaton
    '''
    draw_automaton(lexer.dfa,**kwargs)

def draw_ast(ast:AST,**kwargs) -> None:
    '''
    Args:
        ast (AST): ast to draw
        
        kwargs (dict): optional values

            filename:str filename of the output file with the ast drawed
            
            show:bool tells if the result will be opened after created
            
            cache:bool tells if the cache will be used
            
            physics:bool tells if show physics controls
            
            select_menu:bool tells if show select menu controls
            
            filter_menu:bool tells if show filter menu controls
            
            nodes:bool
            
            edges:bool

    Returns:
        None: creates an interactive graphic showing the AST graph of the given AST.
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
    nodes = kwargs.get('nodes',False)
    if not isinstance(nodes,bool):
        raise ValueError('nodes argument must be a boolean value')
    edges = kwargs.get('edges',False)
    if not isinstance(edges,bool):
        raise ValueError('edges argument must be a boolean value')
    filename = kwargs.get('filename','ast')
    if not isinstance(filename,str):
        raise ValueError('filename must be an string value')
    show = kwargs.get('show',False)
    if not isinstance(show,bool):
        raise ValueError('edges argument must be a boolean value')
    cache = kwargs.get('cache',False)
    if not isinstance(cache,bool):
        raise ValueError('edges argument must be a boolean value')

    if physics:
        filters.append('physics')
    if nodes:
        filters.append('nodes')
    if edges:
        filters.append('edges')
    
    G = _ast_to_graph(ast)
    if not filename:
        filename = f'ast'
    
    layout = {
        'hierarchical':{
            'enabled':True,
            'direction':'UD',
            'sortMethod':'directed'
        }
    }
    net = Network(directed=True,height='100vh',width='100%',bgcolor='white',select_menu=select_menu,filter_menu=filter_menu,layout=layout)
    if filters:
        net.show_buttons(filter_=filters)
    
    for node,node_attrs in G.nodes(data=True):

        label = node_attrs['label']
        title = node_attrs['title']
        level = node_attrs['level']

        net.add_node(
            node,
            label=label,
            title=title,
            level=level,
            shape='circle',
            size=60,
            font={
                'size': 14,
                'face': 'arial',
                'align': 'center'
            }
        )
    
    for u,v in G.edges:
        net.add_edge(u,v)

    output_path = f'{filename}.html'
    if cache:
        cache = {}
        if not CACHE_FILE:
            raise ValueError('cache file not set')
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE,'rb') as f:
                cache = pickle.load(f)

        html = net.generate_html(output_path)

        json_str_or = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest_or = hashlib.sha256(json_str_or.encode()).hexdigest()

        embedder = ResourceEmbedder(cache)
        embedder.feed(html)

        json_str = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest = hashlib.sha256(json_str.encode()).hexdigest()
        
        if not os.path.exists(CACHE_FILE) or digest_or != digest:
            with open(CACHE_FILE,'wb') as f:
                pickle.dump(cache,f)
        
        html = embedder.output
        with open(output_path,'w',encoding='utf-8') as f:
            f.write(html)
    else:
        net.save_graph(output_path)
    
    if show:
        webbrowser.open(output_path,2)

def draw_parse_tree_from_parser(parser:Parser,**kwargs) -> None:
    '''
    Args:
        parser (Parser): parser to draw
        
        kwargs (dict): optional values

            filename:str filename of the output file with the ast drawed
            
            show:bool tells if the result will be opened after created
            
            cache:bool tells if the cache will be used
            
            physics:bool tells if show physics controls
            
            select_menu:bool tells if show select menu controls
            
            filter_menu:bool tells if show filter menu controls
            
            nodes:bool
            
            edges:bool

    Returns:
        None: creates an interactive graphic showing the AST graph of the given AST.
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
    nodes = kwargs.get('nodes',False)
    if not isinstance(nodes,bool):
        raise ValueError('nodes argument must be a boolean value')
    edges = kwargs.get('edges',False)
    if not isinstance(edges,bool):
        raise ValueError('edges argument must be a boolean value')
    filename = kwargs.get('filename','parse tree')
    if not isinstance(filename,str):
        raise ValueError('filename must be an string value')
    show = kwargs.get('show',False)
    if not isinstance(show,bool):
        raise ValueError('edges argument must be a boolean value')
    cache = kwargs.get('cache',False)
    if not isinstance(cache,bool):
        raise ValueError('edges argument must be a boolean value')

    if physics:
        filters.append('physics')
    if nodes:
        filters.append('nodes')
    if edges:
        filters.append('edges')
    
    G = _get_graph_from_parse_tree(parser)
    if not filename:
        filename = f'ast'
    
    layout = {
        'hierarchical':{
            'enabled':True,
            'direction':'UD',
            'sortMethod':'directed'
        }
    }
    net = Network(directed=True,height='100vh',width='100%',bgcolor='white',select_menu=select_menu,filter_menu=filter_menu,layout=layout)
    if filters:
        net.show_buttons(filter_=filters)
    
    for node,node_attrs in G.nodes(data=True):

        label = node_attrs['label']
        level = node_attrs['level']

        net.add_node(
            node,
            label=label,
            level=level,
            shape='circle',
            size=60,
            font={
                'size': 14,
                'face': 'arial',
                'align': 'center'
            }
        )
    
    for u,v in G.edges:
        net.add_edge(u,v)

    output_path = f'{filename}.html'
    if cache:
        cache = {}
        if not CACHE_FILE:
            raise ValueError('cache file not set')
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE,'rb') as f:
                cache = pickle.load(f)
        html = net.generate_html(output_path)

        json_str_or = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest_or = hashlib.sha256(json_str_or.encode()).hexdigest()

        embedder = ResourceEmbedder(cache)
        embedder.feed(html)

        json_str = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest = hashlib.sha256(json_str.encode()).hexdigest()
        
        if not os.path.exists(CACHE_FILE) or digest_or != digest:
            with open(CACHE_FILE,'wb') as f:
                pickle.dump(cache,f)

        html = embedder.output
        with open(output_path,'w',encoding='utf-8') as f:
            f.write(html)
    else:
        net.save_graph(output_path)
    
    if show:
        webbrowser.open(output_path,2)

def show_propagation_edges_table(g:Grammar,**kwargs) -> None:
    '''
    Args:
        parser (Parser): parser to draw
        
        kwargs (dict): optional values

            filename:str filename of the output file with the ast drawed
            
            show:bool tells if the result will be opened after created
            
            cache:bool tells if the cache will be used
    
        Returns:
            None: creates an interactive graphic showing the propagation edges for the given grammar.
    '''

    filename = kwargs.get('filename','parse tree')
    if not isinstance(filename,str):
        raise ValueError('filename must be an string value')
    show = kwargs.get('show',False)
    if not isinstance(show,bool):
        raise ValueError('edges argument must be a boolean value')
    cache = kwargs.get('cache',False)
    if not isinstance(cache,bool):
        raise ValueError('edges argument must be a boolean value')

    output_path = f'{filename}.html'
    html = build_propagation_edges_table(g)

    if cache:
        cache = {}
        if not CACHE_FILE:
            raise ValueError('cache file not set')
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE,'rb') as f:
                cache = pickle.load(f)
        
        json_str_or = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest_or = hashlib.sha256(json_str_or.encode()).hexdigest()
        
        embedder = ResourceEmbedder(cache)
        embedder.feed(html)

        json_str = json.dumps(cache,sort_keys=True,ensure_ascii=True)
        digest = hashlib.sha256(json_str.encode()).hexdigest()

        if not os.path.exists(CACHE_FILE) or digest_or != digest:
            with open(CACHE_FILE,'wb') as f:
                pickle.dump(cache,f)
        html = embedder.output

    with open(output_path,'w',encoding='utf-8') as f:
        f.write(html)    

    if show:
            webbrowser.open(output_path,2)

def set_cache_file(filename:str) -> None:
    '''
    Args:
        filename (str)
    
    Description:
        sets the cache file for the resources of the html files result

    !!!WARNING:
        if filename already exists, it will be overwrited
    '''
    global CACHE_FILE
    if not filename:
        raise ValueError()
    CACHE_FILE = filename