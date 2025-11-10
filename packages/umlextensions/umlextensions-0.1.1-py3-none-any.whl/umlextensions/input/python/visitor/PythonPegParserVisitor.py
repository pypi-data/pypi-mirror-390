
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from re import search as regExSearch
from re import Match as regExMatch

from dataclasses import dataclass

from antlr4.tree.Tree import TerminalNodeImpl

from pyutmodelv2.PyutType import PyutType
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutMethod import PyutMethods
from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutMethod import SourceCode
from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility

from umlextensions.input.python.pythonpegparser.PythonParser import PythonParser

from umlextensions.input.python.visitor.BaseVisitor import BaseVisitor
from umlextensions.input.python.visitor.BaseVisitor import NO_CLASS_DEF_CONTEXT

from umlextensions.input.python.visitor.ParserTypes import Associate
from umlextensions.input.python.visitor.ParserTypes import AssociateName
from umlextensions.input.python.visitor.ParserTypes import Associates
from umlextensions.input.python.visitor.ParserTypes import AssociationType
from umlextensions.input.python.visitor.ParserTypes import Associations
from umlextensions.input.python.visitor.ParserTypes import Parents
from umlextensions.input.python.visitor.ParserTypes import PropertyMap
from umlextensions.input.python.visitor.ParserTypes import PropertyName
from umlextensions.input.python.visitor.ParserTypes import PropertyNames
from umlextensions.input.python.visitor.ParserTypes import PyutClassName
from umlextensions.input.python.visitor.ParserTypes import PyutClasses
from umlextensions.input.python.visitor.ParentsDictionaryHandler import ParentsDictionaryHandler

MethodName    = NewType('MethodName', str)

"""
    Find 
        the 'def' 
        skip over the method name until we find a '(' 
        then skip until we find ');'
"""

# noinspection SpellCheckingInspection
MAGIC_DUNDER_METHODS:      List[str] = ['__init__', '__str__', '__repr__', '__new__', '__del__',
                                        '__eq__', '__ne__', '__lt__', '__gt__', '__le__', '__ge__'
                                        '__pos__', '__neg__', '__abs__', '__invert__', '__round__', '__floor__', '__floor__', '__trunc__',
                                        '__add__', '__sub__', '__mul__', '__floordiv__', '__div__', '__truediv__', '__mod__', '__divmod__', '__pow__',
                                        '__lshift__', '__rshift__', '__and__', '__or__', '__xor__',
                                        '__hash__',
                                        '__getattr__', '__setattr__', '__getattribute__', '__delattr__',
                                        '__len__', '__setitem__', '__delitem__', '__contains__', '__missing__',
                                        '__call__', '__enter__', '__exit__',
                                        '__bool__'
                                        ]
PARAMETER_SELF:      str = 'self'
PROTECTED_INDICATOR: str = '_'
PRIVATE_INDICATOR:   str = '__'
PROPERTY_DECORATOR:  str = 'property'

"""
    Find 
        the 'def' 
        skip over the method name until we find a '(' 
        then skip until we find ');'
"""
# METHOD_FIND_PATTERN: str = 'def(.*\(.*\):)'     # noqa
METHOD_FIND_PATTERN: str = 'def(.*\x28.*\x29:)'     # noqa


@dataclass
class ParameterNameAndType:
    name:     str = ''
    typeName: str = ''


class PythonPegParserVisitor(BaseVisitor):
    """
    The general purpose Python Code Parser
    """
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._associations: Associations = Associations({})
        self._propertyMap:  PropertyMap  = PropertyMap({})

        self._currentCode:              SourceCode               = cast(SourceCode, None)
        self._parentsDictionaryHandler: ParentsDictionaryHandler = ParentsDictionaryHandler()

    @property
    def pyutClasses(self) -> PyutClasses:
        return self._pyutClasses

    @pyutClasses.setter
    def pyutClasses(self, pyutClasses: PyutClasses):

        classNames = pyutClasses.keys()
        #
        # Create property map for each class
        #
        for className in classNames:
            self._propertyMap[className] = PropertyNames([])
        self._pyutClasses = pyutClasses

    @property
    def parents(self) -> Parents:
        return self._parentsDictionaryHandler.parents

    @parents.setter
    def parents(self, parents: Parents):
        self._parentsDictionaryHandler.parents = parents

    @property
    def associations(self) -> Associations:
        return self._associations

    @associations.setter
    def associations(self, newValue: Associations):
        self._associations = newValue

    def visitClass_def(self, ctx: PythonParser.Class_defContext):
        """
        Visit a parse tree produced by PythonParser#class_def.

        Args:
            ctx:

        """
        className: PyutClassName = self._extractClassName(ctx=ctx)

        self.logger.debug(f'{className=}')

        argumentsCtx: PythonParser.ArgumentsContext = self._findArgListContext(ctx)
        if argumentsCtx is not None:
            self._parentsDictionaryHandler.createParentChildEntry(argumentsCtx, className)

        return self.visitChildren(ctx)

    def visitFunction_def(self, ctx: PythonParser.Function_defContext):
        """
        Visit a parse tree produced by PythonParser#function_def.

        Args:
            ctx:
        """
        classCtx: PythonParser.Class_defContext = self._extractClassDefContext(ctx)

        if classCtx != NO_CLASS_DEF_CONTEXT:

            className:     PyutClassName = self._extractClassName(ctx=classCtx)
            methodName:    MethodName    = self._extractMethodName(ctx=ctx.function_def_raw())
            returnTypeStr: str           = self._extractReturnType(ctx=ctx)

            pyutVisibility: PyutVisibility = PyutVisibility.PUBLIC
            if methodName in MAGIC_DUNDER_METHODS:
                pass
            elif methodName.startswith(PRIVATE_INDICATOR):
                pyutVisibility = PyutVisibility.PRIVATE
            elif methodName.startswith(PROTECTED_INDICATOR):
                pyutVisibility = PyutVisibility.PROTECTED

            if self._isProperty(ctx) is True:
                self._makePropertyEntry(className=className, methodName=methodName)
                self._handleField(ctx=ctx)
            else:
                self.logger.debug(f'{methodName=}')
                if className not in self._pyutClasses:
                    assert False, f'This should not happen missing class name for: {methodName}'
                else:
                    pyutClass:  PyutClass  = self._pyutClasses[className]
                    pyutMethod: PyutMethod = PyutMethod(name=methodName, returnType=PyutType(returnTypeStr), visibility=pyutVisibility)

                    try:
                        pyutMethod.sourceCode = self._currentCode
                        pyutClass.methods.append(pyutMethod)
                    except Exception as e:
                        self.logger.error(f'{e=}')
                        self.logger.error(f'Missing source code for {className}.{methodName}')

        return self.visitChildren(ctx)

    def visitParameters(self, ctx: PythonParser.ParametersContext):
        """
        Visit a parse tree produced by PythonParser#parameters.

        parameters
            : slash_no_default param_no_default* param_with_default* star_etc?
            | slash_with_default param_with_default* star_etc?
            | param_no_default+ param_with_default* star_etc?
            | param_with_default+ star_etc?
            | star_etc;

        Args:
            ctx:

        Returns:
        """
        classCtx:  PythonParser.Class_defContext    = self._extractClassDefContext(ctx)
        if classCtx == NO_CLASS_DEF_CONTEXT:
            self.logger.warning('This set of parameters belong to a method outside of a class')
        else:
            methodCtx: PythonParser.Function_defContext = self._extractMethodContext(ctx)

            className:    PyutClassName    = self._extractClassName(ctx=classCtx)
            propertyName: PropertyName = self._extractPropertyName(ctx=methodCtx.function_def_raw())
            if self._isThisAParameterListForAProperty(className=className, propertyName=propertyName) is True:
                pass
            else:
                methodName: MethodName = self._extractMethodName(ctx=methodCtx.function_def_raw())
                self.logger.debug(f'{className=} {methodName=}')
                noDefaultContexts: List[PythonParser.Param_no_defaultContext]   = ctx.param_no_default()
                defaultContexts:   List[PythonParser.Param_with_defaultContext] = ctx.param_with_default()

                ctx2 = ctx.slash_no_default()
                ctx3 = ctx.slash_with_default()

                if len(defaultContexts) != 0:
                    self._handleFullParameters(className=className, methodName=methodName, defaultContexts=defaultContexts)
                elif len(noDefaultContexts) != 0:
                    self._handleTypeAnnotated(className=className, methodName=methodName, noDefaultContexts=noDefaultContexts)
                elif ctx2 is not None:
                    self.logger.error(f'{ctx2.getText()}')
                    assert False, f'Unhandled {ctx2.getText()}'
                elif ctx3 is not None:
                    self.logger.error(f'{ctx3.getText()}')
                    assert False, f'Unhandled {ctx3.getText()}'

        return self.visitChildren(ctx)

    def visitAssignment(self, ctx: PythonParser.AssignmentContext):
        """
        Visit a parse tree produced by PythonParser#assignment.
        Do data classes

        Args:
            ctx:
        """
        classDefContext: PythonParser.Class_defContext = self._extractClassDefContext(ctx=ctx)

        if classDefContext != NO_CLASS_DEF_CONTEXT:

            if self._isThisAnAssignmentForADataClass(ctx=classDefContext) is True and self._isThisAssignmentInsideAMethod(ctx=ctx) is False:

                className: PyutClassName = self._extractClassName(ctx=classDefContext)
                self.logger.debug(f'{className} is a data class')
                if len(ctx.children) == 5:
                    self._handleFullField(className, ctx)

                elif len(ctx.children) == 3:
                    # if isinstance(ctx.children[0], TerminalNodeImpl):
                    if isinstance(ctx.children[0], PythonParser.NameContext):
                        self._handleNoDefaultValueField(className, ctx)
                    else:
                        self._handleNoTypeSpecifiedField(className, ctx)

        return self.visitChildren(ctx)

    def visitStatements(self, ctx: PythonParser.StatementsContext):

        parentCtx = ctx.parentCtx

        if isinstance(parentCtx, PythonParser.BlockContext):
            blockContext: PythonParser.BlockContext      = cast(PythonParser.BlockContext, parentCtx)
            statements:   PythonParser.StatementsContext = blockContext.statements()

            for child in statements.children:

                statement:     PythonParser.StatementContext = cast(PythonParser.StatementContext, child)
                statementText: str = statement.start.getInputStream().getText(statement.start.start, statement.stop.stop)

                match: regExMatch | None = regExSearch(METHOD_FIND_PATTERN, statementText)

                if match is not None:

                    self.logger.debug(f'statementText:\n{statementText}')

                    splitStatements: List[str] = statementText.split('\n')

                    sourceCode: SourceCode = SourceCode([])
                    for s in splitStatements:
                        s = s.removeprefix('    ')
                        sourceCode.append(f'{s}')
                    self._currentCode = sourceCode

        return self.visitChildren(ctx)

    def _extractMethodName(self, ctx: PythonParser.Function_def_rawContext) -> MethodName:

        methodName: MethodName       = MethodName(self._extractFunctionNameRawString(ctx=ctx))
        return methodName

    def _extractFunctionNameRawString(self, ctx: PythonParser.Function_def_rawContext) -> str:

        name: TerminalNodeImpl = ctx.name()
        return name.getText()

    def _isProperty(self, ctx: PythonParser.Function_defContext) -> bool:
        """
        Used by the function definition visitor to determine if the current method name is marked as a property.

        Args:
            ctx:  The function's raw context

        Returns: 'True' if it is an annotated property, else 'False'
        """
        ans: bool = False

        decorators: PythonParser.DecoratorsContext = ctx.decorators()
        if decorators is None:
            pass
        else:
            namedExpressions: List[PythonParser.Named_expressionContext] = decorators.named_expression()
            for ne in namedExpressions:
                self.logger.debug(f'{ne.getText()=}')
                if ne.getText() == PROPERTY_DECORATOR:
                    ans = True
                    break
        return ans

    def _extractReturnType(self, ctx: PythonParser.Function_defContext) -> str:

        exprCtx: PythonParser.ExpressionContext = ctx.function_def_raw().expression()

        if exprCtx is None:
            returnTypeStr: str = ''
        else:
            returnTypeStr = exprCtx.getText()

        return returnTypeStr

    def _makePropertyEntry(self, className: PyutClassName, methodName: MethodName):
        """
        Make an entry into the property map.  This ensures that we do not try to create
        arguments for an annotated method when we visit the method parameters

        Args:
            methodName:  A property name which we turn into a field

        """
        self._propertyMap[className].append(cast(PropertyName, methodName))

    def _handleField(self, ctx: PythonParser.Function_defContext):
        """
        Turns methods annotated as a property into an UML field
        Also check to see if it needs to make a entry into the association dictionary

        Args:
            ctx:
        """

        classCtx:  PythonParser.Class_defContext    = self._extractClassDefContext(ctx)
        methodCtx: PythonParser.Function_defContext = self._extractMethodContext(ctx)

        className:    PyutClassName  = self._extractClassName(ctx=classCtx)
        propertyName: PropertyName   = self._extractPropertyName(ctx=methodCtx.function_def_raw())
        self.logger.debug(f'{className} property name: {propertyName}')
        #
        # it is really a property name
        #
        typeStr: str = self._extractReturnType(ctx=ctx)

        self._makeFieldForClass(className, propertyName, typeStr, defaultValue='')

        self._makeAssociationEntry(className, typeStr)

    def _extractPropertyName(self, ctx: PythonParser.Function_def_rawContext) -> PropertyName:

        propertyName: PropertyName = PropertyName(self._extractFunctionNameRawString(ctx=ctx))
        return propertyName

    def _makeAssociationEntry(self, className, typeStr):
        """
        Now check to see if this type is one of our known classes;  If so, then create
        an association entry

        Args:
            className:
            typeStr:

        """
        if typeStr in self._pyutClasses:

            associateName: AssociateName = AssociateName(typeStr)
            associate:     Associate     = Associate(associateName=associateName, associationType=AssociationType.ASSOCIATION)

            if className in self._associations:
                self._associations[className].append(associate)
            else:
                self._associations[className] = Associates([associate])

    def _isThisAnAssignmentForADataClass(self, ctx: PythonParser.Class_defContext) -> bool:

        ans: bool = False

        decoratorsCtx: PythonParser.DecoratorsContext = ctx.decorators()
        if decoratorsCtx is not None:
            for decorator in decoratorsCtx.children:
                if isinstance(decorator, PythonParser.Named_expressionContext) is True:
                    # self.logger.info(f'{decorator.getText()=}')
                    ans = True
                    break
        return ans

    def _handleFullField(self, className: PyutClassName, ctx: PythonParser.AssignmentContext):
        """
        From within a data class
        Full annotated and with default value
        Args:
            className:
            ctx:
        """
        fieldName:  str = ctx.children[0].getText()
        typeStr:    str = ctx.children[2].getText()
        fieldValue: str = ctx.children[4].getText()

        self._makeFieldForClass(className=className, propertyName=fieldName, typeStr=typeStr, defaultValue=fieldValue)
        self._makeAssociationEntry(className=className, typeStr=typeStr)

    def _handleNoDefaultValueField(self, className: PyutClassName, ctx: PythonParser.AssignmentContext):
        """
        From inside a data class
        no default value

        Args:
            className:
            ctx:
        """
        fieldName: str = ctx.children[0].getText()
        typeStr:   str = ctx.children[2].getText()

        self._makeFieldForClass(className=className, propertyName=fieldName, typeStr=typeStr, defaultValue='')
        self._makeAssociationEntry(className=className, typeStr=typeStr)

    def _handleNoTypeSpecifiedField(self, className: PyutClassName, ctx: PythonParser.AssignmentContext):
        """
        From inside a data class

        Args:
            className:
            ctx:
        """
        fieldName:    str = ctx.children[0].getText()
        defaultValue: str = ctx.children[2].getText()

        self._makeFieldForClass(className=className, propertyName=fieldName, typeStr='', defaultValue=defaultValue)

    def _isThisAParameterListForAProperty(self, className: PyutClassName, propertyName: PropertyName):
        ans: bool = False

        propertyNames: PropertyNames = self._propertyMap[className]
        if propertyName in propertyNames:
            ans = True

        return ans

    def _handleFullParameters(self, className: PyutClassName, methodName: MethodName, defaultContexts: List[PythonParser.Param_with_defaultContext]):
        """
        Handles these type:
            fullScale(self, intParameter: int = 0, floatParameter: float = 42.0, stringParameter: str = ''):
        """

        for withDefaultCtx in defaultContexts:

            paramCtx:          PythonParser.ParamContext              = withDefaultCtx.param()
            nameAndType:       ParameterNameAndType                   = self._extractParameterNameAndType(paramCtx=paramCtx)
            defaultAssignment: PythonParser.Default_assignmentContext = withDefaultCtx.default_assignment()
            expr:               str                                   = defaultAssignment.children[1].getText()

            pyutParameter: PyutParameter = PyutParameter(name=nameAndType.name, type=PyutType(nameAndType.typeName), defaultValue=expr)
            self._updateModelMethodParameter(className=className, methodName=methodName, pyutParameter=pyutParameter)

    def _handleTypeAnnotated(self, className: PyutClassName, methodName: MethodName, noDefaultContexts: List[PythonParser.Param_no_defaultContext]):

        for noDefaultCtx in noDefaultContexts:
            paramCtx:    PythonParser.ParamContext = noDefaultCtx.param()
            nameAndType: ParameterNameAndType      = self._extractParameterNameAndType(paramCtx=paramCtx)

            if nameAndType.name == PARAMETER_SELF:
                continue

            pyutParameter: PyutParameter = PyutParameter(name=nameAndType.name, type=PyutType(nameAndType.typeName))

            self._updateModelMethodParameter(className=className, methodName=methodName, pyutParameter=pyutParameter)

    def _extractParameterNameAndType(self, paramCtx: PythonParser.ParamContext) -> ParameterNameAndType:

        terminalNode:  TerminalNodeImpl = paramCtx.children[0]
        if len(paramCtx.children) > 1:
            annotationCtx: PythonParser.AnnotationContext = paramCtx.children[1]
            exprCtx:       PythonParser.ExpressionContext = annotationCtx.children[1]
            typeStr: str = exprCtx.getText()
        else:
            typeStr = ''

        paramName: str = terminalNode.getText()

        return ParameterNameAndType(name=paramName, typeName=typeStr)

    def _updateModelMethodParameter(self, className: PyutClassName, methodName: MethodName, pyutParameter: PyutParameter):

        self.logger.debug(f'{pyutParameter=}')

        pyutClass:  PyutClass  = self._pyutClasses[className]
        pyutMethod: PyutMethod = self._findModelMethod(methodName=methodName, pyutClass=pyutClass)

        pyutMethod.addParameter(parameter=pyutParameter)

    def _findModelMethod(self, pyutClass: PyutClass, methodName: MethodName) -> PyutMethod:

        foundMethod: PyutMethod = cast(PyutMethod, None)

        pyutMethods: PyutMethods = pyutClass.methods
        for method in pyutMethods:
            pyutMethod: PyutMethod = cast(PyutMethod, method)
            if pyutMethod.name == methodName:
                foundMethod = pyutMethod
                break

        return foundMethod
