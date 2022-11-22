from typing import Any, Dict, Tuple, Union
from textx import metamodel_from_str, TextXSyntaxError
from fractions import Fraction
import sys

# This is TextX version of the XText grammar in the clang repository
# Xtext file:
# src\info.computationalmodeling.lang.parent\info.computationalmodeling.lang\src\main\java\info\computationalmodeling\lang\MaxPlusMatrix.xtext
# repository:
# https://git.ics.ele.tue.nl/computational-modeling/cmlang.git

MPMGrammar = """

MaxPlusMatrixModel:
	'max-plus' 'model' name=ID ':'
	('matrices' (matrices = MaxPlusMatrix)+)?
	('vector sequences' (vectorsequences = VectorSequence)+)?
	('event sequences' (eventsequences = EventSequence)+)?
	;

MaxPlusMatrix:
	name=ID 
	(labels = Labels  (',')?)?
	'='
	'['
	(rows = Row (',')?)*
	']'
;

VectorSequence:
	name=ID 
	(labels = Labels (',')?)?
	'='
	'['
	(vectors += Row (',')?)*
	']'
;

EventSequence:
	name=ID '='
	sequence = Row
;

Labels:
	'('
	(label = ID (',')? )+	
	')'
;

Row:
	'[' ( elements = Element (',')?)* ']'
;

Element:
	Number | '-inf'
;


Number:
	ratio=Ratio | float=Float | int=Int
;

Ratio:
	numerator=Int '/' denominator=INT
;

Float: STRICTFLOAT;

Int: '-'? INT;

Comment:
    /\\/\\*(.|\\n)*?\\*\\// | /\\/\\/.*?$/
;

"""

MetaModelMPM = metamodel_from_str(MPMGrammar, classes=[])

def parseMPMDSL(content: str, factory: Dict[str,Any]) -> Union[Tuple[None,None,None,None],Tuple[str,Dict[str,Any],Dict[str,Any],Dict[str,Any]]]:

    def _getNumber(n):
        if n.ratio != None:
            return Fraction("{}/{}".format(n.ratio.numerator, n.ratio.denominator)).limit_denominator()
        if n.float != None:
            return Fraction(n.float).limit_denominator()
        if n.int != None:
            return Fraction(n.int).limit_denominator()

    def _parseRow(r: Any, mpm: Any, factory: Dict[str,Any]):
        row = []
        for e in r.elements:
            if e == "-inf":
                row.append(None)
            else:
                row.append(_getNumber(e))

        factory['AddRow'](mpm, row)

    def _parseLabels(labels):
        return labels.label

    try:
        model =  MetaModelMPM.model_from_str(content)
    except TextXSyntaxError as err:
        sys.stderr.write("Syntax error in line %d col %d: %s\n" % (err.line, err.col, err.message))
        return (None, None, None, None)
    
    resMatrices = {}
    for m in model.matrices:
        mpm = factory['Init']()
        if m.labels:
            factory['AddLabels'](mpm, _parseLabels(m.labels))
        for r in m.rows:
            _parseRow(r, mpm, factory)
        resMatrices[m.name] = mpm

    resVectorSequences = {}
    for v in model.vectorsequences:
        vs = factory['InitVectorSequence']()
        if v.labels:
            factory['AddLabels'](vs, _parseLabels(v.labels))
        for r in v.vectors:
            _parseRow(r, vs, factory)
        resVectorSequences[v.name] = vs

    resEventSequences = {}
    for e in model.eventsequences:
        es = factory['InitEventSequence']()
        _parseRow(e.sequence, es, factory)
        resEventSequences[e.name] = es

    return model.name, resMatrices, resVectorSequences, resEventSequences

