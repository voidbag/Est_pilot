from core.sym_child import *
import math
import copy
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
        expr = self.make_parse_tree(in_str)
        origin_str = expr.tostring()
        ret['origin'] = origin_str
        ret.update(self.do_diff(in_str, var))
        return ret

    def do_diff(self, expr, var):
        ret = {}
        var_dict = {var : True}
        in_str = expr.diff(var_dict)
#        print ('before canonicalization ', in_str)
        expr = self.make_parse_tree(in_str)
#        print ('diff result ', expr.tostring())
        ret[var] = expr.tostring()
        return ret
    
    def canonicalize(self, in_str):
        ret = {}
        ret['origin'] = in_str
        expr = self.make_parse_tree(in_str)
        ret['Canonicalized form'] = expr.tostring_latex()

        return ret

    def diff_multiple(self, in_str, var_list):
        ret = {}
        expr = self.make_parse_tree(in_str)
        origin_str = expr.tostring()

        ret['origin'] = origin_str

        for var in var_list:
            ret.update(self.do_diff(expr, var))
        return ret

    def is_differentiable(self, in_str, point_dict):
        ret = {}
        expr = self.make_parse_tree(in_str)
        val = self.compute(in_str, point_dict)
        ret['Ret'] = 'True'
        return ret
    
    def do_compute(self, expr, var_dict):
        for k in var_dict:
            if var_dict[k] == 'e':
                var_dict[k] = math.e
            elif var_dict[k] == 'pi':
                var_dict[k] = math.pi
        var_dict.update({'e': math.e, 'pi': math.pi})
        
        print (var_dict)
        ret = expr.compute(var_dict)
        var_dict.pop('e')
        var_dict.pop('pi')

        return ret

    def compute(self, in_str, var_dict):
        ret = {}
        expr = self.make_parse_tree(in_str)
        ret.update(var_dict)
        ret['Canonicalized Form'] = expr.tostring() 
        ret['Computing Result'] = self.do_compute(expr, var_dict)
        return ret

    def do_collect_points(self, expr, var_dict, var_range, keys, depth,\
            step, ret):
        if depth == 0:
            for idx in range(0, len(keys)):
                ret[idx].append(var_dict[keys[idx]])

            ret[len(keys)].append(expr.compute(var_dict))
            return
       
        key = keys[depth - 1]
        entry = var_range[key]
        start = entry[0]
        end = entry[1]
        
        assert start <= end

        cur = start
        while cur <= end: 
            var_dict[key] = cur
            self.do_collect_points(expr, var_dict, var_range, keys,\
                    depth-1, step, ret)
            cur += step

    def get_axis(self, expr):
        var_dict = copy.deepcopy(expr.vars)
        if 'e' in var_dict:
            var_dict.pop('e')
        if 'pi' in expr.vars:
            var_dict.pop('pi')
        
        keys =list(var_dict.keys())
        keys.sort()
        return keys

    def get_point_dict(self, in_str, var_range):
        expr = self.make_parse_tree(in_str)
        nd = self.get_axis(expr)
        if len(nd) > 2:
            raise ValueError('Too many dimensions in given expression')
        for element in nd:
            if element in var_range:
                continue
            raise ValueError('Unknown Dimension')
        fns = self.diff_multiple(in_str, nd)
        ret = {}
        for key in fns:
            ret[key] = []
            expr = self.make_parse_tree(fns[key])
            for i in range(0, len(var_range) + 1):
                ret[key].append([])
            
            list_of_list = ret[key]
            keys = list(var_range.keys())
            keys.sort()
            self.do_collect_points(expr, {}, var_range, keys, len(keys),\
                    Constant.step, list_of_list)
        return ret

    #var_range {key: (start, end)}
    def do_definite_integral(self, expr, var_dict, var_range, keys, depth, step):
        if depth == 0:
            return expr.compute(var_dict) * pow(step, len(keys))
       
        key = keys[depth - 1]
        entry = var_range[key]
        start = entry[0]
        end = entry[1]
        
        assert start <= end

        cur = start
        ret = 0
        while cur <= end: 
            var_dict[key] = cur
            ret += self.do_definite_integral(expr, var_dict, var_range, keys,\
                    depth-1, step)
            cur += step
        
        return ret

    #var_range: {var_name: (min, max)}
    def definite_integral(self, in_str, var_range, step = Constant.step):
        expr = self.make_parse_tree(in_str)
        ret = {}
        ret['Canonicalized Form'] = expr.tostring()
        ret['Definite Integral'] = \
                self.do_definite_integral(expr, {}, var_range,\
                        list(var_range.keys()), len(var_range), step)

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
        ret = {}
        vec_dict = self.make_unit_vec(vec_dict)

        diff_dict = self.diff_multiple(in_str, vec_dict.keys())

        str_expr = '' 
        for key in vec_dict:
            if len(str_expr) != 0:
                str_expr += ' + '
            str_expr += '( ' +  str(diff_dict[key]) + ' ) * ' +\
                    str(vec_dict[key])
        
        tree = self.make_parse_tree(str_expr)
       
        ret['origin'] = diff_dict['origin']
        ret['Directional Derivative'] = tree.tostring()

        return ret

    def get_gradient_vector(self, in_str):
        expr = self.make_parse_tree(in_str)
        if 'e' in expr.vars:
            expr.vars.pop('e')
        if 'pi' in expr.vars:
            expr.vars.pop('pi')
        ret_dict = self.diff_multiple(in_str, expr.vars)

        key_list = list(ret_dict.keys())
        key_list.sort()
        
        ret_vec = ''
        for k in key_list:
            if k == 'origin':
                continue
            if len(ret_vec) != 0:
                ret_vec += ' \\\\ '

            ret_vec += ret_dict[k]
        ret_vec = '\\begin{bmatrix}' + ret_vec + '\\end{bmatrix}'

        ret = {}
        ret['origin'] = ret_dict['origin']
        ret['Gradient Vector (sorted by variable name)'] = ret_vec 
        return ret 
    
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
    in_str = 'x ^ x'
    print(main.canonicalize(in_str))
    in_str = '( x * y ) ^ x'
    print(main.canonicalize(in_str))

