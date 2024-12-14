# parser.py
from typing import List, Union
from lexer import Token

class Node:
    def __init__(self, type_: str, children: Union[List['Node'], str]):
        self.type = type_
        self.children = children

    def __repr__(self, level=0):
        indent = "  " * level
        if isinstance(self.children, list):
            children_rep = "".join(child.__repr__(level+1) for child in self.children)
            return f"{indent}{self.type}:\n{children_rep}"
        else:
            return f"{indent}{self.type}: {self.children}\n"
        

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def consume(self, expected_type: str, expected_value=None) -> Token:
        if self.pos >= len(self.tokens):  # Verifica se chegou ao fim da lista
            raise RuntimeError(f"Unexpected end of input, expected {expected_type} {'with value ' + expected_value if expected_value else ''}")
        
        token = self.tokens[self.pos]
        if token.type != expected_type or (expected_value is not None and token.value != expected_value):
            raise RuntimeError(f"Expected {expected_type} {'with value ' + expected_value if expected_value else ''}, got {token.type}({token.value}) at {token.line}:{token.column}")
        self.pos += 1
        return token

    def lookahead(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token("EOF", "", -1, -1)
        return self.tokens[self.pos]

    def parse_prog(self) -> Node:
        main_node = self.parse_main()
        classes = []
        while self.lookahead().type == "RESERVED" and self.lookahead().value == "class":
            classes.append(self.parse_class())
        return Node("PROG", [main_node] + classes)

    def parse_main(self) -> Node:
        self.consume("RESERVED", "class")
        class_name = self.consume("IDENTIFIER").value
        self.consume("PUNCTUATION", "{")
        self.consume("RESERVED", "public")
        self.consume("RESERVED", "static")
        self.consume("RESERVED", "void")
        self.consume("RESERVED", "main")
        self.consume("PUNCTUATION", "(")
        self.consume("RESERVED", "String")
        self.consume("PUNCTUATION", "[")
        self.consume("PUNCTUATION", "]")
        param_name = self.consume("IDENTIFIER").value
        self.consume("PUNCTUATION", ")")
        self.consume("PUNCTUATION", "{")
        commands = self.parse_cmds()
        self.consume("PUNCTUATION", "}")
        self.consume("PUNCTUATION", "}")
        return Node("MAIN", [Node("CLASS", class_name), Node("PARAMS", param_name), Node("COMMANDS", commands)])

    def parse_cmds(self) -> List[Node]:
        commands = []
        while self.lookahead().type != "PUNCTUATION" or self.lookahead().value != "}":
            commands.append(self.parse_cmd())
        return commands

    def parse_cmd(self) -> Node:
        token = self.lookahead()
        if token.type == "RESERVED" and token.value == "if":
            return self.parse_if()
        elif token.type == "RESERVED" and token.value == "while":
            return self.parse_while()
        elif token.type == "RESERVED" and token.value == "System.out.println":
            return self.parse_print()
        elif token.type == "IDENTIFIER":
            return self.parse_assignment()
        elif token.type == "PUNCTUATION" and token.value == "{":
            # Trata bloco de comandos
            self.consume("PUNCTUATION", "{")
            commands = self.parse_cmds()
            self.consume("PUNCTUATION", "}")
            return Node("BLOCK", commands)
        else:
            raise RuntimeError(f"Unexpected token {token.value} at {token.line}:{token.column}")

    def parse_if(self) -> Node:
        self.consume("RESERVED", "if")
        self.consume("PUNCTUATION", "(")
        condition = self.parse_exp()
        self.consume("PUNCTUATION", ")")
        then_cmd = self.parse_cmd()
        if self.lookahead().type == "RESERVED" and self.lookahead().value == "else":
            self.consume("RESERVED", "else")
            else_cmd = self.parse_cmd()
            return Node("IF", [condition, then_cmd, else_cmd])
        return Node("IF", [condition, then_cmd])

    def parse_while(self) -> Node:
        self.consume("RESERVED", "while")
        self.consume("PUNCTUATION", "(")
        condition = self.parse_exp()
        self.consume("PUNCTUATION", ")")
        body = self.parse_cmd()
        return Node("WHILE", [condition, body])

    def parse_print(self) -> Node:
        self.consume("RESERVED", "System.out.println")
        self.consume("PUNCTUATION", "(")
        expression = self.parse_exp()
        self.consume("PUNCTUATION", ")")
        self.consume("PUNCTUATION", ";")
        return Node("PRINT", [expression])

    def parse_assignment(self) -> Node:
        identifier = self.consume("IDENTIFIER").value
        if self.lookahead().type == "PUNCTUATION" and self.lookahead().value == "=":
            self.consume("PUNCTUATION", "=")
            value = self.parse_exp()
            self.consume("PUNCTUATION", ";")
            return Node("ASSIGNMENT", [Node("IDENTIFIER", identifier), value])
        raise RuntimeError(f"Unexpected token in assignment at {self.lookahead().line}:{self.lookahead().column}")

    def parse_exp(self) -> Node:
        # Apenas um exemplo simplificado para parsear expressões
        token = self.consume(self.lookahead().type)
        if token.type == "NUMBER":
            return Node("NUMBER", token.value)
        elif token.type == "RESERVED" and token.value in {"true", "false"}:
            return Node("BOOLEAN", token.value)
        elif token.type == "IDENTIFIER":
            return Node("IDENTIFIER", token.value)
        else:
            raise RuntimeError(f"Unexpected token in expression: {token.value}")
