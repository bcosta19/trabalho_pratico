# lexer.py
import re
from typing import List, Tuple, Union

# Define categorias de tokens
TOKEN_SPECIFICATION = [
    ("RESERVED", r'\b(?:boolean|class|extends|public|static|void|main|String|return|int|if|else|while|System\.out\.println|length|true|false|this|new|null)\b'),
    ("IDENTIFIER", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("NUMBER", r'\b\d+\b'),
    ("OPERATOR", r'(\+|-|\*|&&|!|<|>|>=|<=|==|!=)'),
    ("PUNCTUATION", r'[(),;.\[\]{}=]'),
    ("WHITESPACE", r'[ \n\t\r\f]+'),  # Ignorar espaços em branco
    ("COMMENT", r'//.*|/\*.*?\*/'),  # Ignorar comentários
    ("MISMATCH", r'.'),  # Para identificar erros
]

class Token:
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"

def lexer(source_code: str) -> List[Token]:
    tokens = []
    line_num = 1
    line_start = 0
    token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)
    
    for mo in re.finditer(token_regex, source_code):
        kind = mo.lastgroup
        value = mo.group(kind)
        column = mo.start() - line_start
        
        if kind == "WHITESPACE" or kind == "COMMENT":
            if '\n' in value:
                line_num += value.count('\n')
                line_start = mo.end()
            continue
        elif kind == "MISMATCH":
            raise RuntimeError(f"Unexpected character {value!r} at {line_num}:{column}")
        
        tokens.append(Token(kind, value, line_num, column))
    
    return tokens
