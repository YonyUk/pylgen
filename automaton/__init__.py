from .automaton import State,Automaton,DFA,NFA,create_dfa,get_word_automaton,get_words_automaton
import networkx as nx
from pyvis.network import Network

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

def draw_automaton(automaton:Automaton,filename:str | None=None,**kwargs) -> None:
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
    
    if physics:
        filters.append('physics')
    if nodes:
        filters.append('nodes')
    if edges:
        filters.append('edges')

    G = _to_graph(automaton)
    if not filename:
        filename = f'automaton-{automaton.id}'
    
    net = Network(directed=True,height='100vh',width='100%',bgcolor='white',select_menu=select_menu,filter_menu=filter_menu)
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
    net.show(output_path,notebook=False)