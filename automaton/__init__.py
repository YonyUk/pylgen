from .automaton import State,Automaton,DFA,NFA,create_dfa,get_word_automaton,get_words_automaton
import networkx as nx
from nx_vis_visualizer import nx_to_vis

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
            G.edges[origin,destination]['label'] = 'epsilon'
            G.edges[origin,destination]['dashes'] = True
    
    for state in automaton.states:

        if state == automaton.start_state:
            G.nodes[state.id]['color'] = {'background':'white','border':'green' if state.is_accept else 'black'}
        elif state.is_accept:
            G.nodes[state.id]['color'] = 'green'
        
        G.nodes[state.id]['label'] = f'{state.value}'
        G.nodes[state.id]['title'] = f'id: {state.id}'
    
    return G

def draw_automaton(automaton:Automaton,filename:str | None=None) -> None:
    '''
    Args:
        automaton (Automaton): automaton to draw
        filename (str): filename of the output file with the automaton drawed
        interactive (bool): tells if the graphic is interactive (nx-vis-visualizer in web),
            or a figure of matplotlib

    Returns:
        None: creates an interactive graphic showing the automaton
    '''
    G = _to_graph(automaton)
    if not filename:
        filename = f'automaton-{automaton.id}'
    nx_to_vis(G,output_filename=f'{filename}.html',show_browser=True)