from pylgen.grammar.grammar cimport AttributedGrammar
from pylgen.parser.parser_builder cimport _build_lalr_parser_from_attributed
from pylgen.parser.parser cimport BottomUpParser
from pylgen.common.types cimport AST,ASTListView



from .asts cimport (
    VecLangProgram,
    VecLangInstruction,
    VecLangInstructionsSequence,
    ArithmeticExpressionLevel1,
    ArithmeticExpressionLevel2,
    ArithmeticExpressionLevel3,
    ArithmeticExpressionLevel4,
    Number,
    ComplexNumber,
    NumberExpression,
    VariableExpression,
    Components,
    Vector,
    Range,
    Indexing,
    Slicing,
    FunctionArgs,
    FunctionCall,
    FunctionDecl,
    FunctionDeclArgs,
    Type,
    int_number,
    float_number,
    variable,
    lp,
    rp,
    new_line,
    plus,
    minus,
    mod,
    mul,
    div,
    exp,
    eq,
    lc,
    rc,
    com,
    double_dot,
    sum_keyword,
    mean_keyword,
    dot_keyword,
    print_keyword,
    type_complex,
    type_float,
    type_int,
    type_vector,
    single_reductor,
    instructions_sequence_reductor,
    plus_reductor,
    minus_reductor,
    mul_reductor,
    div_reductor,
    mod_reductor,
    exp_reductor,
    assignment_reductor,
    extractor_reductor,
    number_reductor,
    variable_reductor,
    complex_number_reductor,
    complex_number_reductor_1,
    vector_reductor,
    vector_components_reductor,
    range_reductor,
    range_reductor_1,
    range_reductor_2,
    range_reductor_3,
    indexing_reductor,
    slicing_reductor,
    function_call_reductor,
    function_args_reductor,
    built_in_function_call_reductor,
    function_declare_args_reductor,
    function_declare_reductor,
    type_reductor
)

cpdef BottomUpParser build_parser():
    cdef AttributedGrammar VecLangGrammar = AttributedGrammar(VecLangProgram) # type:ignore

    VecLangGrammar._add_attributed_production(VecLangProgram,[VecLangInstructionsSequence],single_reductor)

    VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstructionsSequence,new_line,VecLangInstruction],instructions_sequence_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstructionsSequence,new_line],instructions_sequence_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstructionsSequence,[VecLangInstruction],instructions_sequence_reductor)

    VecLangGrammar._add_attributed_production(VecLangInstruction,[ArithmeticExpressionLevel1],single_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstruction,[FunctionDecl],single_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstruction,[VariableExpression,eq,ArithmeticExpressionLevel1],assignment_reductor)
    VecLangGrammar._add_attributed_production(VecLangInstruction,[print_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel1,plus,ArithmeticExpressionLevel2],plus_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel1,minus,ArithmeticExpressionLevel2],minus_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel1,[ArithmeticExpressionLevel2],single_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,mul,ArithmeticExpressionLevel3],mul_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,div,ArithmeticExpressionLevel3],div_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel2,mod,ArithmeticExpressionLevel3],mod_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel2,[ArithmeticExpressionLevel3],single_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel3,[ArithmeticExpressionLevel3,exp,ArithmeticExpressionLevel4],exp_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel3,[ArithmeticExpressionLevel4],single_reductor)

    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[NumberExpression],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[VariableExpression],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[Vector],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[Indexing],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[FunctionCall],single_reductor)
    VecLangGrammar._add_attributed_production(ArithmeticExpressionLevel4,[lp,ArithmeticExpressionLevel1,rp],extractor_reductor)

    VecLangGrammar._add_attributed_production(NumberExpression,[Number],single_reductor)
    VecLangGrammar._add_attributed_production(NumberExpression,[ComplexNumber],single_reductor)

    VecLangGrammar._add_attributed_production(Number,[int_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[float_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[plus,int_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[minus,int_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[plus,float_number],number_reductor)
    VecLangGrammar._add_attributed_production(Number,[minus,float_number],number_reductor)

    VecLangGrammar._add_attributed_production(ComplexNumber,[type_complex,lp,Number,com,Number,rp],complex_number_reductor)
    VecLangGrammar._add_attributed_production(ComplexNumber,[Number,variable],complex_number_reductor_1)

    VecLangGrammar._add_attributed_production(VariableExpression,[variable],variable_reductor)

    VecLangGrammar._add_attributed_production(Vector,[lc,Components,rc],vector_reductor)
    VecLangGrammar._add_attributed_production(Vector,[lc,Range,rc],extractor_reductor)
    VecLangGrammar._add_attributed_production(Vector,[Slicing],single_reductor)

    VecLangGrammar._add_attributed_production(Components,[ArithmeticExpressionLevel1],vector_components_reductor)
    VecLangGrammar._add_attributed_production(Components,[Components,com,ArithmeticExpressionLevel1],vector_components_reductor)

    VecLangGrammar._add_attributed_production(Range,[int_number,double_dot,int_number],range_reductor)
    VecLangGrammar._add_attributed_production(Range,[minus,int_number,double_dot,int_number],range_reductor_1)
    VecLangGrammar._add_attributed_production(Range,[int_number,double_dot,minus,int_number],range_reductor_2)
    VecLangGrammar._add_attributed_production(Range,[minus,int_number,double_dot,minus,int_number],range_reductor_3)

    VecLangGrammar._add_attributed_production(Indexing,[VariableExpression,lc,int_number,rc],indexing_reductor)
    VecLangGrammar._add_attributed_production(Indexing,[Vector,lc,int_number,rc],indexing_reductor)

    VecLangGrammar._add_attributed_production(Slicing,[VariableExpression,lc,Range,rc],slicing_reductor)
    VecLangGrammar._add_attributed_production(Slicing,[Vector,lc,Range,rc],slicing_reductor)

    VecLangGrammar._add_attributed_production(FunctionCall,[VariableExpression,lp,FunctionArgs,rp],function_call_reductor)
    VecLangGrammar._add_attributed_production(FunctionCall,[sum_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
    VecLangGrammar._add_attributed_production(FunctionCall,[mean_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)
    VecLangGrammar._add_attributed_production(FunctionCall,[dot_keyword,lp,FunctionArgs,rp],built_in_function_call_reductor)

    VecLangGrammar._add_attributed_production(FunctionArgs,[ArithmeticExpressionLevel1],function_args_reductor)
    VecLangGrammar._add_attributed_production(FunctionArgs,[FunctionArgs,com,ArithmeticExpressionLevel1],function_args_reductor)

    VecLangGrammar._add_attributed_production(FunctionDecl,[VariableExpression,lp,FunctionDeclArgs,rp,eq,ArithmeticExpressionLevel1],function_declare_reductor)

    VecLangGrammar._add_attributed_production(FunctionDeclArgs,[VariableExpression,double_dot,Type],function_declare_args_reductor)
    VecLangGrammar._add_attributed_production(FunctionDeclArgs,[FunctionDeclArgs,com,VariableExpression,double_dot,Type],function_declare_args_reductor)

    VecLangGrammar._add_attributed_production(Type,[type_complex],type_reductor)
    VecLangGrammar._add_attributed_production(Type,[type_float],type_reductor)
    VecLangGrammar._add_attributed_production(Type,[type_int],type_reductor)
    VecLangGrammar._add_attributed_production(Type,[type_vector],type_reductor)

    return _build_lalr_parser_from_attributed(VecLangGrammar)