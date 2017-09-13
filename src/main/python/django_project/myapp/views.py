from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.http import HttpResponse

import json
from core.main import *

#from this matplotlib
# file charts.py
import datetime
import django
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

import io
import base64
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def draw_plot(point_dict):
    #{'name' : [[], []], 'name' : [[],[]]}
    fig = plt.figure(2)

    keys = list(point_dict.keys())

    pos = 11 + 100 * len(keys)
    for k in keys:
        projection = None
        if len(point_dict[k]) == 2:
            proj = '2d'
            cur = fig.add_subplot(pos)
        else:
            if len(point_dict[k]) != 3:
                raise ValueError('Input demension must be 2 or 3 current: %d' %\
                        len(point_dict[k]))
            proj = '3d'
            cur = fig.add_subplot(pos, projection = proj)


        if len(point_dict[k]) == 2:
            print(len(point_dict[k][0]))
            cur.plot(point_dict[k][0], point_dict[k][1])
        else:
            cur.plot(point_dict[k][0], point_dict[k][1], point_dict[k][2])
        cur.set_title(k)
        pos += 1
    
    canvas = FigureCanvas(fig)
    graphic = io.BytesIO()
    canvas.print_png(graphic)
    graphic.seek(0)
    graphic = base64.b64encode(graphic.read()).decode()
    return graphic

def simple():
    fig=Figure()
    ax=fig.add_subplot(111)
    x=[1]
    y=[1]
    ax.plot(x, y)
    ax.set_title('Sample')
    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()
    canvas.print_png(graphic)
    graphic.seek(0)
    graphic = base64.b64encode(graphic.read()).decode()
    return graphic

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
        graphic = None
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
                    try:
                        ret = main.get_gradient_vector(expr)
                    except ValueError:
                        ret = None
                elif option == 'draw_plot':
                    try:
                        point_dict = main.get_point_dict(expr, var_dict)
                        graphic = draw_plot(point_dict)
                        ret = {'Ret', 'Plots'}
                    except ValueError as e:
                        ret = {'msg': str(e)}
                elif option == 'draw_directional':
                    try:
                        point_dict = main.collect_points_for_directional(expr, var_dict)
                        graphic = draw_plot(point_dict)
                        ret = {'Ret', 'Directional Derivative Plot'}
                    except ValueError as e:
                        ret = {'msg': str(e)}
                else:
                    ret = {'msg': 'Invalid input'}

            except json.decoder.JSONDecodeError:
                ret = None
            except ZeroDivisionError:
                ret = None
            if ret == None:
                ret = make_err_msg()
        result = {}
        result['ret'] = ret
        if graphic == None:
            result['graphic'] = simple()
        else:
            result['graphic'] = graphic
    return render(request, 'index.html', {'ret': result})

def cal(request):
    ret = 'GET???'
    print ('cal111')
    if request.method == 'POST':
        req = request.POST
        ret = req.get('expr', 'Unknown Input')
    return render(request, 'index.html', {'ret': ret})


# Create your views here.
