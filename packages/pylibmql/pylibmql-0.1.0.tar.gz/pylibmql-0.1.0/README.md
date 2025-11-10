# major-requirement-parser

```ebnf
File              ::= SpecialStatement ";" { SpecialStatement ";" } ;

SpecialStatement  ::= Statement ":" String [ ":" QuantitySingle ] ;

Statement         ::= "SELECT" Quantity "FROM" Selector ;

Selector          ::= SelectorList | SelectorSingle ;
SelectorList      ::= "[" SelectorSingle { "," SelectorSingle } "]" ;
SelectorSingle    ::= Statement | XYZ ;

XYZ               ::= QueryName "(" QueryArgument { "," QueryArgument } ")" ;
QueryName         ::= "CLASS" | "class" | "PLACEMENT" | "placement"
                    | "TAG" | "tag" | "RANGE" | "range" ;
QueryArgument     ::= String | ClassArgument ;

ClassArgument     ::= DepartmentId ClassId ;
DepartmentId      ::= UppercaseLetter UppercaseLetter UppercaseLetter UppercaseLetter ;
ClassId           ::= Digit Digit Digit Digit ;

Quantity          ::= QuantityMany | QuantitySingle ;
QuantityMany      ::= QuantitySingle "-" QuantitySingle ;
QuantitySingle    ::= Digit { Digit } ;  (* one or more digits; non-empty *)

String            ::= "\"" { "\"\"" | (AnyCharExcept["\"", "\r", "\n"]) } "\"" ;

(* Lexical *)
UppercaseLetter   ::= "A" | ... | "Z" ;
Digit             ::= "0" | ... | "9" ;
```