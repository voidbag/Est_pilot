1. Features to be Implemented

1. List Functions Used in Derivation
	functions: x ^ n, a ^ x, sin, cos, tan, csc, sec, cot, arcsin, arccos,
	arctan
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
		diff(f(x) + g(x)) = diff(f(x)) + diff(g(x))
		diff(f(x) * g(x)) = f(x) * diff(g(x)) + diff(f(x)) * g(x)
		diff(f(g(x))) = diff(f(g(x)) * diff(g(x))
		
	Integral ..

2. System Setting
2.1 virtualenv
	source venv/bin/activate

2.2 python3 web server (Django)
2.2.1 ajax??

2.3 mathjax in javascript

2.4 python unit test

2.5 pybuilder for managing this project.



3. References

#TODO function implmentation like log  sin, normal log???
#TODO test the evaluation
#TODO Differentiation with multiple
#TODO descritbe the differentiation of triangular function and log
3.1 parsing rule
	
	<expr> := <term> <expr-tail>
	<expr-tail> := '+' <term> <expr-tail> | '-' <term> <expr-tail> | e
	<term> := <pow> <term-tail>
	<term-tail> := '*' <pow> <term-tail> | '/' <pow> <term-tail> | e
	<pow> := <paren> <pow-tail>
	<pow-tail> := '^' <pow> | e	
	<paren> := {transcendential}( <expr> ) | <D>
	<D> := '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | 'char'
	7 * ( 2 + 3 )  

	each tag contains variables list
	expr +,-
	high *,/ has variable
	<expr> checks if high has no
	isEmpty
       	
3.3 canonicalization	
	nested hash map will be used??
	criteria: base variable(primitive) and their exponent.
	primitives: x, exponent, log, triangular



need to add term 
derivation
ex)

class expr:
	def diff(x)
		#That's because constant can be returned...
		#This layer must make constant zero!!
		if term.contains(x) and expr_tail.contains(x)
			return pack (term.diff(x), expr_tail.op, expr_tail.diff(x))
		elif term.contains(x) and !expr_tail.contains(x)
			return term.diff(x)
		elif !term.contains(x) and expr_tail.contains(x)
			return expr_tail.diff(x) 
		else:
			return None

class expr\_tail:
	def diff(x)
		if e:
			return None
		else:
			return expr.diff(x)

class term:
	def diff(x):
		if e:
			return None
		else:
			l_diff = pow.expr.diff(x)
			r_diff = high_tail.expr.diff(x)
			
			if r_diff is empty:
				return l_diff
			if r_diff.op == '/':
				r_diff = pack(1, '/', r_diff)
			l = pack(l_diff, '*', high_tail)
			r = pack(pow, '*', r_diff)

			return pack (l, '+', r) #product rule

class high\_tail:
	def diff(x)
		if e:
			return null
		else	
			return high.diff(x)

class pow: #TODO no x^x for now
	def diff(x):
		if paren.contains(x) and !pow_tail.contains(x) and !pow_tail.empty:
			inner = paren.diff(x)
			outer = pack(pow_tail, '*', pack(paren, '^', pack(pow_tail, '-', 1)))
			return pack(inner, '*', outer)
		elif !paren.contains(x) and pow_tail.contains(x):
			inner = pow_tail.diff(x)
			outer = pack(this, '*', pack('pow_tail', 'ln', null))
			return pack(inner, '*', outer)
		elif !paren.cotains(x) and !pow_tail.contains(x):
			return this 
			#suppose this will be included in a term, optimistically.
		else:
			throw exception('error: x^x isn't elementary function')
			#TODO contains must check canonical form. x can be
			#removed.. then how about sin(x)^2 + cos(x)^2 ??? ...
			#is it preferable???

class pow_tail:
	def diff(x):
		if e:
			return null
		else
			return pow.diff(x)

class paren:
	def diff(x):
		if this.d != None:
	       		return d
		inner = expr.diff(x)
 		if this.op == 'sin':
			return pack(inner, '*', pack(expr, 'cos', null))
		
# current issue regarding differentiation is contains(x) which whould consider
#		cannonicalized form

