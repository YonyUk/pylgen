from pylgen.grammar.grammar import AttributedGrammar
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType

from .grammar_symbols import (
    Config,
    ConfigSequence,
    Section,
    SectionConfigSequence,
    SubSection,
    ConfigAtom,
    lbracket,
    rbracket,
    variable,
    newline,
    indent,
    dedent,
    colon,
    string,
    boolean,
    number,
    minus
)

from .reductors import (
    config_configsequence_reductor,
    configsequence_section_reductor,
    configsequence_direct_reductor,
    section_reductor,
    sectionconfigsequence_configatom_reductor,
    sectionconfigsequence_sectionconfigsequence_configatom,
    configatom_variable_colon_boolean_reductor,
    configatom_variable_colon_number_reductor,
    configatom_variable_colon_string_reductor
)

G = AttributedGrammar(Config,'$')

G[Config] += (ConfigSequence,),config_configsequence_reductor

G[ConfigSequence] += (ConfigSequence,Section),configsequence_section_reductor
G[ConfigSequence] += (Section,),configsequence_direct_reductor

G[Section] += (lbracket,variable,rbracket,newline,indent,SectionConfigSequence,dedent),section_reductor

G[SectionConfigSequence] += (ConfigAtom,),sectionconfigsequence_configatom_reductor
G[SectionConfigSequence] += (SubSection,),sectionconfigsequence_configatom_reductor
G[SectionConfigSequence] += (SectionConfigSequence,ConfigAtom),sectionconfigsequence_sectionconfigsequence_configatom
G[SectionConfigSequence] += (SectionConfigSequence,SubSection),sectionconfigsequence_sectionconfigsequence_configatom

G[ConfigAtom] += (variable,colon,string,newline),configatom_variable_colon_string_reductor
G[ConfigAtom] += (variable,colon,boolean,newline),configatom_variable_colon_boolean_reductor
G[ConfigAtom] += (variable,colon,number,newline),configatom_variable_colon_number_reductor
G[ConfigAtom] += (variable,colon,string),configatom_variable_colon_string_reductor
G[ConfigAtom] += (variable,colon,boolean),configatom_variable_colon_boolean_reductor
G[ConfigAtom] += (variable,colon,number),configatom_variable_colon_number_reductor

G[SubSection] += (minus,variable,colon,newline,indent,SectionConfigSequence,dedent),section_reductor

parser = ParserBuilder.build_parser_from_attributed(G,ParserType.LALR1)