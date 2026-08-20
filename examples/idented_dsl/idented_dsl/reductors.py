from pylgen.common.types import ASTListView,AST

from .asts import (
    ConfigsAST,
    ConfigSequenceAST,
    ConfigSectionAST,
    SectionConfigSequenceAST,
    AtomConfigAST
)

def config_configsequence_reductor(asts:ASTListView) -> AST:
    config = ConfigsAST(1,1)
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config._configs = config_sequence._configs
    return config

def configsequence_section_reductor(asts:ASTListView) -> AST:
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config_sequence._configs.append(asts[1])
    return config_sequence

def configsequence_direct_reductor(asts:ASTListView) -> AST:
    config = ConfigSequenceAST(asts[0].line,asts[0].column)
    config._configs.append(asts[0])
    return config

def section_reductor(asts:ASTListView) -> AST:
    configs:SectionConfigSequenceAST = asts[5] # type:ignore
    var:Token = asts[1] # type:ignore
    config = ConfigSectionAST(var.text,asts[0].line,asts[0].column)
    config._configs = configs._configs
    return config

def sectionconfigsequence_configatom_reductor(asts:ASTListView) -> AST:
    config = SectionConfigSequenceAST(asts[0].line,asts[0].column)
    config._configs.append(asts[0])
    return config

def sectionconfigsequence_sectionconfigsequence_configatom(asts:ASTListView) -> AST:
    config:SectionConfigSequenceAST = asts[0] # type:ignore
    config._configs.append(asts[1])
    return config

def configatom_variable_colon_string_reductor(asts:ASTListView) -> AST:
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text[1:-1],var.line,var.column)
    return config

def configatom_variable_colon_boolean_reductor(asts:ASTListView) -> AST:
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text == 'true',var.line,var.column)
    return config

def configatom_variable_colon_number_reductor(asts:ASTListView) -> AST:
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,float(val.text),var.line,var.column)
    return config