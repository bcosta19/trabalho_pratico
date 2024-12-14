# main.py
from lexer import lexer
from parser import Parser

def main():
    # source_code = """
    # class Example {
    #     public static void main(String[] args) {
    #         if (true) {
    #             System.out.println(42);
    #         } else {
    #             System.out.println(0);
    #         }
    #         while (false) {
    #             System.out.println(100);
    #         }
    #     }
    # }
    # """

    with open("exemplo.minijava", 'r') as file:
        source_code = ''
        line = file.readline()

        while line:
            source_code += line
            line = file.readline()

    tokens = lexer(source_code)
    parser = Parser(tokens)
    syntax_tree = parser.parse_prog()
    print(syntax_tree)

if __name__ == "__main__":
    main()
