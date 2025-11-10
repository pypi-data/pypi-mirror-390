
from typing import cast
from typing import List

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from antlr4 import ParserRuleContext
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype

from umlextensions.input.python.pythonpegparser.PythonParser import PythonParser

from umlextensions.input.python.visitor.BaseVisitor import BaseVisitor
from umlextensions.input.python.visitor.BaseVisitor import NO_CLASS_DEF_CONTEXT
from umlextensions.input.python.visitor.ParserTypes import ParentName
from umlextensions.input.python.visitor.ParserTypes import PyutClassName

from umlextensions.input.python.visitor.ParserTypes import PyutClasses
from umlextensions.input.python.visitor.ParserTypes import VERSION

ENUMERATION_SUPER_CLASS: str = 'Enum'


class PythonPegParserClassVisitor(BaseVisitor):
    """
    The UML Extension visitor specific to the Python Input Extension

    Simply does a scan to identify all the classes;   A separate
    is needed to do inheritance

    """
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

    @property
    def pyutClasses(self) -> PyutClasses:
        return self._pyutClasses

    @pyutClasses.setter
    def pyutClasses(self, pyutClasses: PyutClasses):
        self._pyutClasses = pyutClasses

    def visitClass_def(self, ctx: PythonParser.Class_defContext):
        """
        Visit a parse tree produced by PythonParser#class_def.

        Args:
            ctx:
        """
        #
        # Check if we are an enumeration
        #
        className: PyutClassName = self._extractClassName(ctx=ctx)

        pyutClass: PyutClass = PyutClass(name=className)
        pyutClass.description = self._generateMyCredits()

        argumentsCtx: PythonParser.ArgumentsContext = self._findArgListContext(ctx)

        if argumentsCtx is not None:
            args: PythonParser.ArgsContext = argumentsCtx.args()
            parentName: ParentName = ParentName(args.getText())
            self.logger.debug(f'Class: {className} is subclass of {parentName}')
            parents: List[str] = parentName.split(',')
            for parent in parents:
                if parent == ENUMERATION_SUPER_CLASS:
                    pyutClass.stereotype = PyutStereotype.ENUMERATION
                    break

        self._pyutClasses[className] = pyutClass

        return self.visitChildren(ctx)

    def visitAssignment(self, ctx: PythonParser.AssignmentContext):
        """
        Visit a parse tree produced by PythonParser#assignment.

        Args:
            ctx:
        """
        if self._isThisAssignmentInsideAMethod(ctx=ctx) is False:

            classCtx:  PythonParser.Class_defContext = self._extractClassDefContext(ctx)
            if classCtx == NO_CLASS_DEF_CONTEXT:
                pass
            else:
                className: PyutClassName                 = self._extractClassName(ctx=classCtx)
                pyutClass: PyutClass                     = self._pyutClasses[className]
                if pyutClass.stereotype == PyutStereotype.ENUMERATION:
                    if len(ctx.children) >= 2:
                        enumName:     str = ctx.children[0].getText()
                        defaultValue: str = ctx.children[2].getText()
                        self.logger.info(f'')
                        self._makeFieldForClass(className=className, propertyName=enumName, typeStr='', defaultValue=defaultValue)

        return self.visitChildren(ctx)

    def visitPrimary(self, ctx: PythonParser.PrimaryContext):
        """
        Generates artificial/synthetic types
        Args:
            ctx:
        """
        primaryStr: str = ctx.getText()
        if primaryStr.startswith('NewType'):
            argumentsCtx: PythonParser.ArgumentsContext = ctx.arguments()
            if argumentsCtx is not None:

                argStr = ctx.children[2].getText()
                typeValueList = argStr.split(',')
                self.logger.debug(f'{typeValueList=}')

                className = typeValueList[0].strip("'").strip('"')
                self.logger.debug(f'{className}')

                pyutClass: PyutClass = PyutClass(name=className)

                pyutClass.description = self._generateMyCredits()
                pyutClass.stereotype  = PyutStereotype.TYPE

                self._pyutClasses[className] = pyutClass

        return self.visitChildren(ctx)

    def _isThisAssignmentInsideAMethod(self, ctx: PythonParser.AssignmentContext) -> bool:

        ans: bool = False

        currentCtx: ParserRuleContext = self._extractMethodContext(ctx=ctx)
        if currentCtx is not None:
            ans = True

        return ans

    def _extractMethodContext(self, ctx: ParserRuleContext) -> PythonParser.Function_defContext:

        currentCtx: ParserRuleContext = ctx

        while isinstance(currentCtx, PythonParser.Function_defContext) is False:
            currentCtx = currentCtx.parentCtx
            if currentCtx is None:
                break

        if currentCtx is not None:
            raw: PythonParser.Function_def_rawContext = cast(PythonParser.Function_defContext, currentCtx).function_def_raw()
            # self.baseLogger.debug(f'Found method: {raw.NAME()}')
            self.baseLogger.debug(f'Found method: {raw.name()}')

        return cast(PythonParser.Function_defContext, currentCtx)

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

    def _generateMyCredits(self) -> str:
        """

        Returns:    Reversed Engineered by the one and only:
                    Gato Malo - Humberto A. Sanchez II
                    Generated: ${DAY} ${MONTH_NAME_FULL} ${YEAR}
                    Version: ${VERSION}

        """
        from datetime import date

        today: date = date.today()
        formatDated: str = today.strftime('%d %B %Y')

        hasiiCredits: str = (
            f'Reversed Engineered by the one and only:{osLineSep}'
            f'Gato Malo - Humberto A. Sanchez II{osLineSep}'
            f'Generated: {formatDated}{osLineSep}'
            f'Version: {VERSION}'
        )

        return hasiiCredits
