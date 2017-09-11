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
        ret[var] = expr.diff(var_dict)

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

            l_grad = 
        except:
            print ('Unexpected Error:', sys.exc_info()[0])


            

        return ret


    def compute(self, in_str, var_dict):
        expr = self.make_parse_tree(in_str)
        return expr.compute(var_dict)

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

    def definite_integral(self, in_str, var_range, step = Main.step)
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

    def directional_derivative(self, in_str, vec_dict)
        vec_dict = self.make_unit_vec(vec)
        diff_dict = self.diff_multiple(vec_dict.keys())
        str_expr = ''
        for key in vec_dict:
            if len(str_expr) != 0:
                str_expr += ' + '
            str_expr += '( ' +  diff_dict[key] + ' ) * ' + vec_dict[key]

        tree = self.make_parse_tree(str_expr)
         
        return tree.tostring()
    
    def draw_directional_derivative(self, in_str, vec_dict, step = Main.step):

    def draw_plot(self, expr, range_dict):
        plot = None
        return plot
    
    def make_parse_tree(self, in_str):
        ret = None
        return ret
