
1. Features to be Implemented

1. List Functions Used in Derivation
	functions: x ^ n, a ^ x, sin, cos, tan, csc, sec, cot,
		   log(a,b), e^x, ln(x)
	derivative: 
		x^n -> n*x^(n-1)
		a^x -> a^x*ln(a)
		sin(x) -> cos(x)
		cos(x) -> -sin(x)
		tan(x) ->  sec(x)^2
		csc(x) -> -cot(x)*csc(x)
		sec(x) -> sec(x)*tan(x)
		cot(x) -> -csc(x)^2
		log(a,x) -> 1/x*ln(a)
		e^x -> e^x
		ln(x) -> 1/x	




2. System Setting
2.1 virtualenv
	source venv/bin/activate

2.2 python3 web server (Django)
2.2.1 ajax??

2.3 mathjax in javascript

2.4 python unit test

2.5 pybuilder for managing this project.



3. References

3.1 parsing rule
	<expr> := <high> <expr-tail>
	<expr-tail> := '+' <expr> | '-' <expr> | e
	<high> := <paren> <high-tail>
	<high-tail> := '*' <high> | '/' <high> | e
	<paren> := ( <expr> ) | <D>
	<D> := '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
	7 * ( 2 + 3 )  
	 

3.2 ll1_parser java project
