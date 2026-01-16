import java.lang.StringBuilder; 
import java.util.ArrayList;
import java.util.List;

enum TokenType { 
    // Fixed punctuation
    LEFT_PAREN,
    RIGHT_PAREN,
    LEFT_BRACE,
    RIGHT_BRACE,
    CARET,
    AMPERSAND,
    ATSIGN,
    NOT,
    DOT,
    COLON,
    COMMA,
    // Keywords
    THIS,
    IF,
    IFONLY,
    WHILE,
    RETURN,
    PRINT,
    EOF,
    // Tokens with data
    OPERATOR,
    NUMBER,
    IDENTIFIER
}

sealed interface Token 
    permits Number, LeftParen, RightParen, Operator, Caret, Ampersand, AtSign, Not, Dot, If, IfOnly, While, Return, Print, Colon, LeftBrace, RightBrace, Identifier, Eof, This, Comma {
    TokenType getType();
}
record Number(long value) implements Token {
    @Override public TokenType getType() { return TokenType.NUMBER; }
}
record LeftParen() implements Token {
    @Override public TokenType getType() { return TokenType.LEFT_PAREN; }
}
record RightParen() implements Token {
    @Override public TokenType getType() { return TokenType.RIGHT_PAREN; }
}
record LeftBrace() implements Token {
    @Override public TokenType getType() { return TokenType.LEFT_BRACE; }
}
record RightBrace() implements Token {
    @Override public TokenType getType() { return TokenType.RIGHT_BRACE; }
}
record Operator(char op) implements Token {
    @Override public TokenType getType() { return TokenType.OPERATOR; }
}
record Caret() implements Token {
    @Override public TokenType getType() { return TokenType.CARET; }
}
record Ampersand() implements Token {
    @Override public TokenType getType() { return TokenType.AMPERSAND; }
}
record AtSign() implements Token {
    @Override public TokenType getType() { return TokenType.ATSIGN; }
}
record Not() implements Token {
    @Override public TokenType getType() { return TokenType.NOT; }
}
record Dot() implements Token {
    @Override public TokenType getType() { return TokenType.DOT; }
}
record If() implements Token {
    @Override public TokenType getType() { return TokenType.IF; }
}
record IfOnly() implements Token {
    @Override public TokenType getType() { return TokenType.IFONLY; }
}
record While() implements Token {
    @Override public TokenType getType() { return TokenType.WHILE; }
}
record Return() implements Token {
    @Override public TokenType getType() { return TokenType.RETURN; }
}
record Print() implements Token {
    @Override public TokenType getType() { return TokenType.PRINT; }
}
record Colon() implements Token {
    @Override public TokenType getType() { return TokenType.COLON; }
}
record Comma() implements Token {
    @Override public TokenType getType() { return TokenType.COMMA; }
}
record Eof() implements Token {
    @Override public TokenType getType() { return TokenType.EOF; }
}
record Identifier(String name) implements Token {
    @Override public TokenType getType() { return TokenType.IDENTIFIER; }
}
record This() implements Token {
    @Override public TokenType getType() { return TokenType.THIS; }
}

class Tokenizer {

    // We'll pre-allocate and reuse common tokens without data
    private final LeftParen lp = new LeftParen();
    private final RightParen rp = new RightParen();
    private final LeftBrace lb = new LeftBrace();
    private final RightBrace rb = new RightBrace();
    private final Colon colon = new Colon();
    private final Print print = new Print();
    private final Return ret = new Return();
    private final While w = new While();
    private final If iff = new If();
    private final IfOnly ifonly = new IfOnly();
    private final Not not = new Not();
    private final AtSign at = new AtSign();
    private final Caret caret = new Caret();
    private final Ampersand amp = new Ampersand();
    private final Dot dot = new Dot();
    private final Eof eof = new Eof();
    private final This th = new This();
    private final Comma comma = new Comma();

    private final String text;
    private int current;
    private Token cached;
    public Tokenizer(String t) {
        this.text = t;
        this.current = 0;
    }
    public Token peek() {
        if (cached == null) {
            cached = advanceCurrent();
        }
        return cached;
    }
    public Token next() {
        if (cached == null) {
            return advanceCurrent();
        } else {
            Token tmp = cached;
            cached = null;
            return tmp;
        }
    }
    private Token advanceCurrent() {
        while (current < text.length() && Character.isWhitespace(text.charAt(current))) {
            current++;
        }
        if (current >= text.length()) {
            return this.eof;
        }
        switch (text.charAt(current)) {
            case '(': current++; return lp;
            case ')': current++; return rp;
            case '{': current++; return lb;
            case '}': current++; return rb;
            case ':': current++; return colon;
            case '!': current++; return not;
            case '@': current++; return at;
            case '^': current++; return caret;
            case '&': current++; return amp;
            case '.': current++; return dot;
            case ',': current++; return comma;
        
            case '+': current++; return new Operator('+');
            case '-': current++; return new Operator('-');
            case '*': current++; return new Operator('*');
            case '/': current++; return new Operator('/');
            
            default:
                if (Character.isDigit(text.charAt(current))) {
                    // This is a digit
                    int start = current++;
                    while (current < text.length() && Character.isDigit(text.charAt(current))) current ++;
                    // current now points to the first non-digit character, or past the end of the text
                    return new Number(Integer.parseInt(text.substring(start,current)));
                }
                // Now down to keywords and identifiers
                else if (Character.isLetter(text.charAt(current))) {
                    int start = current++;
                    while (current < text.length() && Character.isLetterOrDigit(text.charAt(current))) current ++;
                    // current now points to the first non-alphanumeric character, or past the end of the string
                    String fragment = text.substring(start,current);
                    // Unlike the constant parsing switch above, this has already advanced current
                    switch (fragment) {
                        case "if": return iff;
                        case "ifonly": return ifonly;
                        case "while": return w;
                        case "return": return ret;
                        case "print": return print;
                        case "this": return th;
                        default: return new Identifier(fragment);
                    }
                } else {
                    throw new IllegalArgumentException("Unsupported character: "+text.charAt(current));
                }
        }
    }
}

sealed interface Expression 
    permits Constant, Binop, MethodCall, FieldRead, ClassRef, ThisExpr, Variable {
    // TODO: You'll need to provide your own methods for operations you care about
}
record ThisExpr() implements Expression {}
record Constant(long value) implements Expression {}
record Binop(Expression lhs, char op, Expression rhs) implements Expression {}
record MethodCall(Expression base, String methodname, List<Expression> args) implements Expression {}
record FieldRead(Expression base, String fieldname) implements Expression {}
record ClassRef(String classname) implements Expression {}
record Variable(String name) implements Expression {}

class Parser {
    private Tokenizer tok;
    public Parser(Tokenizer t) {
        tok = t;
    }
    // TODO: You'll need to add parseStatement, parseClass, etc.
    /*
     * This method attempts to parse an expression starting from the tokenizer's current token,
     * and returns as soon as it has done so
     */
    public Expression parseExpr() {
        switch (tok.next()) {
            case Eof eof: throw new IllegalArgumentException("No expression to parse: EOF");
            case Number n: return new Constant(n.value());
            case Identifier i: return new Variable(i.name());
            case LeftParen p:
                // Should be start of a binary operation
                Expression lhs = parseExpr();
                Token optok = tok.next();
                if (optok.getType() != TokenType.OPERATOR)
                    throw new IllegalArgumentException("Expected operator but found "+optok);
                Expression rhs = parseExpr();
                Token closetok = tok.next();
                if (closetok.getType() != TokenType.RIGHT_PAREN)
                    throw new IllegalArgumentException("Expected right paren but found "+closetok);
                return new Binop(lhs, ((Operator)optok).op(), rhs);
            case Ampersand a:
                // Should be field read
                Expression base = parseExpr();
                Token dot = tok.next();
                if (dot.getType() != TokenType.DOT)
                    throw new IllegalArgumentException("Expected dot but found "+dot);
                Token fname = tok.next();
                if (fname.getType() != TokenType.IDENTIFIER)
                    throw new IllegalArgumentException("Expected valid field name but found "+fname);
                return new FieldRead(base, ((Identifier)fname).name());
            case Caret c:
                // Should be method call
                Expression mbase = parseExpr();
                Token mdot = tok.next();
                if (mdot.getType() != TokenType.DOT)
                    throw new IllegalArgumentException("Expected dot but found "+mdot);
                Token mname = tok.next();
                if (mname.getType() != TokenType.IDENTIFIER)
                    throw new IllegalArgumentException("Expected valid method name but found "+mname);
                Token open = tok.next();
                if (open.getType() != TokenType.LEFT_PAREN)
                    throw new IllegalArgumentException("Expected left paren but found "+open);
                // Now we iterate through arguments
                ArrayList<Expression> args = new ArrayList<>();
                while (tok.peek().getType() != TokenType.RIGHT_PAREN) {
                    Expression e = parseExpr();
                    System.err.println("Parsed arg: "+e);
                    args.add(e);
                    // Now either a paren or a comma
                    Token punc = tok.peek();
                    if (punc.getType() == TokenType.COMMA)
                        tok.next(); // throw away the comma
                }
                return new MethodCall(mbase, ((Identifier)mname).name(), args);
            case AtSign a:
                Token cname = tok.next();
                if (cname.getType() != TokenType.IDENTIFIER)
                    throw new IllegalArgumentException("Expected valid class name but found: "+cname);
                return new ClassRef(((Identifier)cname).name());
            case This t: return new ThisExpr();
            case Token o:
                throw new IllegalArgumentException("Token "+o+" is not a valid start of an expression");
        }
    }
}
 
public class App {

    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: <comp> {tokenize|parseExpr} [args...]");
            System.exit(1);
        }
        // This is just some code to kick the tires on the tokenizer, your compiler has no need to do this
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < args.length; i++) {
            sb.append(args[i]);
            sb.append(" "); // Without this, separate identifiers will run together
        }
        Tokenizer tok = new Tokenizer(sb.toString());
        switch (args[0]) {
            case "tokenize":
                while (tok.peek().getType() != TokenType.EOF) {
                    System.out.println(tok.next());
                }
                break;
            case "parseExpr":
                Parser p = new Parser(tok);
                System.out.println(p.parseExpr());
                break;
            default:
                System.err.println("Unsupported subcommand: "+args[0]);
        }
    }
}