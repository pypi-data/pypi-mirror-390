# Generated from Expr.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ExprParser import ExprParser
else:
    from ExprParser import ExprParser

# This class defines a complete generic visitor for a parse tree produced by ExprParser.

class ExprVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ExprParser#prog.
    def visitProg(self, ctx:ExprParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#block.
    def visitBlock(self, ctx:ExprParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#stat.
    def visitStat(self, ctx:ExprParser.StatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#ctrl.
    def visitCtrl(self, ctx:ExprParser.CtrlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#expr.
    def visitExpr(self, ctx:ExprParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#symbol.
    def visitSymbol(self, ctx:ExprParser.SymbolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#package.
    def visitPackage(self, ctx:ExprParser.PackageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#list.
    def visitList(self, ctx:ExprParser.ListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#args.
    def visitArgs(self, ctx:ExprParser.ArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#params.
    def visitParams(self, ctx:ExprParser.ParamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#num.
    def visitNum(self, ctx:ExprParser.NumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#str.
    def visitStr(self, ctx:ExprParser.StrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#var.
    def visitVar(self, ctx:ExprParser.VarContext):
        return self.visitChildren(ctx)



del ExprParser