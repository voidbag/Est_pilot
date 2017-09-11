from sym_child import *

class Constant:
    step = 0.001
    diff_step = 0.00001
    diff_threshold = 0.0001

class Main:
    step = 0.001
    diff_step = 0.00001
    diff_threshold = 0.0001
    def diff(self, in_str, var):
        ret = {}
        origin_str = self.make_parse_tree(in_str).tostring()
        ret['origin'] = origin_str
        ret.update(self.do_diff(origin_str, var)) 
        return ret

    def do_diff(self, in_str, var):
        ret = {}
        var_dict = {var : True}
        expr = self.make_parse_tree(in_str)
        ret[var] = self.make_parse_tree(expr.diff(var_dict)).tostring()
        return ret
    
    def canonicalize(self, in_str):
        try:
            ret = {}
            ret['origin'] = in_str
            expr = self.make_parse_tree(in_str)
            ret['ret'] = expr.tostring()
        except ValueError:
            print ('Unexpected Error:', sys.exc_info()[0])
            ret = None
        except ZeroDivisionError:
            print ('Unexpected Error:', sys.exc_info()[0])
            ret = None

        return ret

    def diff_multiple(self, in_str, var_list):
        ret = {}
        origin_str = self.make_parse_tree(in_str).tostring()
        ret['origin'] = origin_str

        for var in var_list:
            ret.update(self.do_diff(origin_str, var))
        return ret

    def is_differentiable(self, in_str, point_dict):
        expr = self.make_parse_tree(in_str)
        try:
            val = self.compute(point_dict)
        except:
            print ('Unexpected Error:', sys.exc_info()[0])
            ret = None 
        
        ret = True
        return ret

    def compute(self, in_str, var_dict):
        try:
            expr = self.make_parse_tree(in_str)
            ret = expr.compute(var_dict)

        except:
            print ('Unexpected Error:', sys.exc_info()[0])
            ret = None 
    
        return ret

    #var_range {key: (start, end)}
    def do_definite_integral(self, expr, var_dict, var_range, keys, step):
        if step == 0:
            return expr.compute(var_dict) * pow(step, len(key))
       
        key = keys[step - 1]
        entry = var_range[key]
        start = entry[0]
        end = entry[1]
        
        assert start <= end

        cur = start
        ret = 0
        while cur <= end: 
            var_dict[key] = cur
            ret += do_definite_integral(expr, var_dict, var_range, keys, step)
            cur += step
        
        return ret

    #var_range: {var_name: (min, max)}
    def definite_integral(self, in_str, var_range, step = Constant.step):
        expr = self.make_parse_tree(in_str)
        ret = do_definite_integral(expr, {}, var_range, var_range.keys(),\
                len(var_range))
        return ret

    #vec: dict
    def make_unit_vec(self, vec_dict):
        values = vec_dict.values() 
        denominator = 0
        for val in values:
            denominator += pow(val, 2.0)
        denominator = pow(denominator, 0.5)

        for key in vec_dict:
            vec_dict[key] /= denominator

        return vec_dict

    def directional_derivative(self, in_str, vec_dict):
        vec_dict = self.make_unit_vec(vec_dict)
        diff_dict = self.diff_multiple(in_str, vec_dict.keys())
        str_expr = ''
        for key in vec_dict:
            if len(str_expr) != 0:
                str_expr += ' + '
            str_expr += '( ' +  str(diff_dict[key]) + ' ) * ' +\
                    str(vec_dict[key])
        
        print (str_expr)
        tree = self.make_parse_tree(str_expr)
         
        return tree.tostring()
    
    def draw_directional_derivative(self, in_str, vec_dict, step = Constant.step):
        plot = None
        return plot
    def draw_plot(self, expr, range_dict):
        plot = None
        return plot
    
    def make_parse_tree(self, in_str):
        in_str = in_str.split(' ')
        q = deque()
        for element in in_str:
            q.append(element)
        expr = Expr()
        expr.parse(q)
        #print ('parse', expr.tostring(), type(expr.get_root()))
        expr.canonicalize()
        ret_str = expr.tostring()
        q = deque()
        ret_str = ret_str.split(' ')
        
        for element in ret_str:
            q.append(element)
        expr = Expr()
        expr.parse(q)
        
        return expr

if __name__ == '__main__':
    main = Main()
    in_str = '( ( ( x ) + y ) ) ^ 2'
    print(main.diff_multiple(in_str, {'x': True, 'y': True}))
    in_str = '( ( ( ( x ) + y ) ) ^ 2 ^ 2 ) ^ ( 1 / 2 )'
    print(main.canonicalize(in_str))
    in_str = '0 / 0'
    print(main.canonicalize(in_str))
    in_str = 'ln ( x )'
    print(main.compute(in_str, {'x' : -1}))
    in_str = 'x ^ 2 * y ^ 2'
    print(main.directional_derivative(in_str, {'x': 1, 'y': 1}))
    print(main.canonicalize(in_str))
    in_str = '6 * x ^ a * ( x + y ^ 2 + 3 ) / ( 2 * x ^ a )'
    print(main.canonicalize(in_str))
    in_str = '( a + b + c ) ^ 2'
    print(main.canonicalize(in_str))
    in_str = '( a * b ) ^ ( a * b )'
    print(main.canonicalize(in_str))
    in_str = '( a + b + c ) ^ b'
    print(main.canonicalize(in_str))
