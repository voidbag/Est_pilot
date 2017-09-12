from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.http import HttpResponse
import json
from core.main import *

def make_err_msg(msg = 'Invalid Input'):
    ret = {'Error': msg}
    return ret

def index(request):
    main = Main()
    ret = 'GET'
    if request.method == 'POST':
        ret = 'Permission denied'
    else:
        assert request.method == 'GET'
        req = request.GET
        expr = req.get('expr', None)
        ret = {}
        if expr != None:
            try:
                var_dict = req.get('vars', '{\"ret\": 0}')
                if len(var_dict) == 0:
                    var_dict = '{\"ret\": 0}'
                var_dict = json.loads(var_dict)
    
                option = req.get('option', None) 
                if option == 'canonicalization':
                    ret = main.canonicalize(expr)
                elif option == 'diff':
                    try:
                        ret = main.diff_multiple(expr, var_dict)  
                    except ValueError:
                        ret = None 
                elif option == 'directional_derivative':
                    try:
                        ret = main.directional_derivative(expr, var_dict)
                    except ValueError:
                        ret = None
                elif option == 'compute':
                    try:
                        ret = main.compute(expr, var_dict)  
                    except ValueError:
                        ret = None
                elif option == 'definite_integral':
                    try:
                        ret = main.definite_integral(expr, var_dict)
                    except ValueError:
                        ret = None
                elif option == 'defferentiability':
                    try:
                        ret = main.is_differentiable(expr, var_dict)
                    except ValueError:
                        ret = {'Ret': 'False'}
                elif option == 'gradient_vector':
                    ret = main.get_gradient_vector(expr)
                else:
                    ret = {'msg': 'Invalid input'}

            except json.decoder.JSONDecodeError:
                ret = None
            except ZeroDivisionError:
                ret = None
            if ret == None:
                ret = make_err_msg()
    return render(request, 'index.html', {'ret': ret})

def cal(request):
    ret = 'GET???'
    print ('cal111')
    if request.method == 'POST':
        req = request.POST
        ret = req.get('expr', 'Unknown Input')
    return render(request, 'index.html', {'ret': ret})


# Create your views here.
