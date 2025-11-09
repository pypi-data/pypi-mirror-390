# Generated from Expr.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ExprParser import ExprParser
else:
    from ExprParser import ExprParser

# This class defines a complete listener for a parse tree produced by ExprParser.
class ExprListener(ParseTreeListener):

    # Enter a parse tree produced by ExprParser#prog.
    def enterProg(self, ctx:ExprParser.ProgContext):
        pass

    # Exit a parse tree produced by ExprParser#prog.
    def exitProg(self, ctx:ExprParser.ProgContext):
        pass


    # Enter a parse tree produced by ExprParser#block.
    def enterBlock(self, ctx:ExprParser.BlockContext):
        pass

    # Exit a parse tree produced by ExprParser#block.
    def exitBlock(self, ctx:ExprParser.BlockContext):
        pass


    # Enter a parse tree produced by ExprParser#stat.
    def enterStat(self, ctx:ExprParser.StatContext):
        pass

    # Exit a parse tree produced by ExprParser#stat.
    def exitStat(self, ctx:ExprParser.StatContext):
        pass


    # Enter a parse tree produced by ExprParser#ctrl.
    def enterCtrl(self, ctx:ExprParser.CtrlContext):
        pass

    # Exit a parse tree produced by ExprParser#ctrl.
    def exitCtrl(self, ctx:ExprParser.CtrlContext):
        pass


    # Enter a parse tree produced by ExprParser#expr.
    def enterExpr(self, ctx:ExprParser.ExprContext):
        pass

    # Exit a parse tree produced by ExprParser#expr.
    def exitExpr(self, ctx:ExprParser.ExprContext):
        pass


    # Enter a parse tree produced by ExprParser#symbol.
    def enterSymbol(self, ctx:ExprParser.SymbolContext):
        pass

    # Exit a parse tree produced by ExprParser#symbol.
    def exitSymbol(self, ctx:ExprParser.SymbolContext):
        pass


    # Enter a parse tree produced by ExprParser#package.
    def enterPackage(self, ctx:ExprParser.PackageContext):
        pass

    # Exit a parse tree produced by ExprParser#package.
    def exitPackage(self, ctx:ExprParser.PackageContext):
        pass


    # Enter a parse tree produced by ExprParser#list.
    def enterList(self, ctx:ExprParser.ListContext):
        pass

    # Exit a parse tree produced by ExprParser#list.
    def exitList(self, ctx:ExprParser.ListContext):
        pass


    # Enter a parse tree produced by ExprParser#args.
    def enterArgs(self, ctx:ExprParser.ArgsContext):
        pass

    # Exit a parse tree produced by ExprParser#args.
    def exitArgs(self, ctx:ExprParser.ArgsContext):
        pass


    # Enter a parse tree produced by ExprParser#params.
    def enterParams(self, ctx:ExprParser.ParamsContext):
        pass

    # Exit a parse tree produced by ExprParser#params.
    def exitParams(self, ctx:ExprParser.ParamsContext):
        pass


    # Enter a parse tree produced by ExprParser#num.
    def enterNum(self, ctx:ExprParser.NumContext):
        pass

    # Exit a parse tree produced by ExprParser#num.
    def exitNum(self, ctx:ExprParser.NumContext):
        pass


    # Enter a parse tree produced by ExprParser#str.
    def enterStr(self, ctx:ExprParser.StrContext):
        pass

    # Exit a parse tree produced by ExprParser#str.
    def exitStr(self, ctx:ExprParser.StrContext):
        pass


    # Enter a parse tree produced by ExprParser#var.
    def enterVar(self, ctx:ExprParser.VarContext):
        pass

    # Exit a parse tree produced by ExprParser#var.
    def exitVar(self, ctx:ExprParser.VarContext):
        pass



del ExprParser