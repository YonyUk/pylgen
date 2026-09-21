from pylgen.common.types import ASTListView,AST

from .asts import (
    ConfigsAST,
    ConfigSequenceAST,
    ConfigSectionAST,
    SectionConfigSequenceAST,
    AtomConfigAST
)

def config_configsequence_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    config = ConfigsAST(sl,sc,el,ec)
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config._configs = config_sequence._configs
    return config

def configsequence_section_reductor(asts:ASTListView) -> AST:
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config_sequence._configs.append(asts[1])
    config_sequence.end_position = asts[1].end_position
    return config_sequence

def configsequence_direct_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    config = ConfigSequenceAST(sl,sc,el,ec)
    config._configs.append(asts[0])
    return config

def section_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[5].end_position
    configs:SectionConfigSequenceAST = asts[5] # type:ignore
    var:Token = asts[1] # type:ignore
    config = ConfigSectionAST(var.text,sl,sc,el,ec)
    config._configs = configs._configs
    return config

def sectionconfigsequence_configatom_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    config = SectionConfigSequenceAST(sl,sc,el,ec)
    config._configs.append(asts[0])
    return config

def sectionconfigsequence_sectionconfigsequence_configatom(asts:ASTListView) -> AST:
    config:SectionConfigSequenceAST = asts[0] # type:ignore
    config._configs.append(asts[1])
    config.end_position = asts[1].end_position
    return config

def configatom_variable_colon_string_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text[1:-1],sl,sc,el,ec)
    return config

def configatom_variable_colon_boolean_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[2].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text == 'true',sl,sc,el,ec)
    return config

def configatom_variable_colon_number_reductor(asts:ASTListView) -> AST:
    (sl,sc),(el,ec) = asts[0].start_position,asts[0].end_position
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,float(val.text),sl,sc,el,ec)
    return config