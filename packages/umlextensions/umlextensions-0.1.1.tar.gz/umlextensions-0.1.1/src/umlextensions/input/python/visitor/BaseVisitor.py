from typing import Union
from typing import cast

from logging import Logger
from logging import getLogger

from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl
from codeallybasic.ConfigurationProperties import PropertyName
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutType import PyutType
from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility

from umlextensions.input.python.pythonpegparser.PythonParser import PythonParser
from umlextensions.input.python.visitor.ParserTypes import PyutClassName
from umlextensions.input.python.visitor.ParserTypes import PyutClasses

from umlextensions.input.python.pythonpegparser.PythonParserVisitor import PythonParserVisitor


NO_CLASS_DEF_CONTEXT: PythonParser.Class_defContext = cast(PythonParser.Class_defContext, None)

class BaseVisitor(PythonParserVisitor):
    def __init__(self):
        super().__init__()
        self.baseLogger: Logger = getLogger(__name__)

        self._pyutClasses:  PyutClasses = PyutClasses({})

    def _isThisAssignmentInsideAMethod(self, ctx: PythonParser.AssignmentContext) -> bool:

        ans: bool = False

        currentCtx: ParserRuleContext = self._extractMethodContext(ctx=ctx)
        if currentCtx is not None:
            ans = True

        return ans

    def _makeFieldForClass(self, className: PyutClassName, propertyName: Union[PropertyName, str], typeStr: str, defaultValue: str):
        """

        Args:
            className:
            propertyName:
            typeStr:
            defaultValue:
        """
        pyutField: PyutField = PyutField(name=propertyName, type=PyutType(typeStr), visibility=PyutVisibility.PUBLIC, defaultValue=defaultValue)
        pyutClass: PyutClass = self._pyutClasses[className]

        pyutClass.fields.append(pyutField)

    def _extractClassName(self, ctx: PythonParser.Class_defContext) -> PyutClassName:
        """
        Get a class name from a Class_defContext
        Args:
            ctx:

        Returns:    A class name
        """

        child:     PythonParser.Class_def_rawContext = ctx.class_def_raw()
        # name:      TerminalNodeImpl                  = child.NAME()
        name:      TerminalNodeImpl = child.name()
        className: PyutClassName    = name.getText()

        return className

    def _extractClassDefContext(self, ctx: ParserRuleContext) -> PythonParser.Class_defContext:
        """
        Args:
            ctx:

        Returns:  Either a class definition context or the sentinel value NO_CLASS_DEF_CONTEXT
        """
        currentCtx: ParserRuleContext = ctx
        while currentCtx.parentCtx:
            if isinstance(currentCtx, PythonParser.Class_defContext):
                return currentCtx
            currentCtx = currentCtx.parentCtx

        return NO_CLASS_DEF_CONTEXT

    def _extractMethodContext(self, ctx: ParserRuleContext) -> PythonParser.Function_defContext:

        currentCtx: ParserRuleContext = ctx

        while isinstance(currentCtx, PythonParser.Function_defContext) is False:
            currentCtx = currentCtx.parentCtx
            if currentCtx is None:
                break

        if currentCtx is not None:
            raw: PythonParser.Function_def_rawContext = cast(PythonParser.Function_defContext, currentCtx).function_def_raw()
            self.baseLogger.debug(f'Found method: {raw.name()}')

        return cast(PythonParser.Function_defContext, currentCtx)

    def _findArgListContext(self, ctx: PythonParser.Class_defContext) -> PythonParser.ArgumentsContext:

        argumentsCtx: PythonParser.ArgumentsContext = cast(PythonParser.ArgumentsContext, None)

        classDefRawContext: PythonParser.Class_def_rawContext = ctx.class_def_raw()
        for childCtx in classDefRawContext.children:
            if isinstance(childCtx, PythonParser.ArgumentsContext):
                argumentsCtx = childCtx
                break

        return argumentsCtx
