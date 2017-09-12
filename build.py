from pybuilder.core import init, use_plugin

use_plugin('python.core') #python project
use_plugin('python.unittest') #execute unittest
use_plugin('python.coverage')
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.distutils')
use_plugin('pypi:pybuilder_django_enhanced_plugin')
use_plugin('exec')
name = 'Pilot Project'
default_task = 'publish'

@init
def initialize(project):
    project.build_depends_on('mockito')
    project.build_depends_on('django')
    project.build_depends_on('matplotlib')
    project.set_property("dir_source_main_python", r"src/main/python/")
    project.set_property("dir_source_unittest_python", r"src/tests/unittest/python")
    project.set_property("run_unit_tests_propagate_stdout", True)
    project.set_property("run_unit_tests_propagate_stderr", True)
    project.set_property("teamcity_output", True)
    project.set_property('django_project', 'myproject')
    project.set_property('django_apps', ['myapp'])
    project.set_property('django_subpath', 'django_project')

