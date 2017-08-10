from pybuilder.core import init, use_plugin

use_plugin('python.core') #python project
use_plugin('python.unittest') #execute unittest
use_plugin('python.coverage')
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.distutils')
use_plugin('pypi:pybuilder_django_enhanced_plugin')

name = 'Pilot Project'
default_task = 'publish'

@init
def initialize(project):
    project.build_depends_on('mockito')
    project.build_depends_on('django')
    project.set_property('django_project', 'myproject')
    project.set_property('django_apps', ['myapp', 'myotherapp'])
    project.set_property('django_subpath', 'django_project')

