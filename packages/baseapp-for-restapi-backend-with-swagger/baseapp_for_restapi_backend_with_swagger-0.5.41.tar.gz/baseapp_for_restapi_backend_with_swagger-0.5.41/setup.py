from setuptools import setup
import versioneer

#Dependancy lists maintained here and in tox.ini
sp_install_requires = [
  'pytz==2025.2',
  'flask==3.1.2',
  'flask_restx==1.3.0',
  'python-dateutil==2.8.1',
  'sortedcontainers==2.4.0',
  'bcrypt==3.1.5',
  'pyjwt==2.8.0',
  'hvac==2.4.0'
]
sp_tests_require = [
  'pytest==8.4.1'
]

all_require = sp_install_requires + sp_tests_require

setup(name='baseapp_for_restapi_backend_with_swagger',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python package which provides a base application class for an app with a restapi backend that provides a swagger',
      url='https://github.com/rmetcalf9/baseapp_for_restapi_backend_with_swagger',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['baseapp_for_restapi_backend_with_swagger'],
      zip_safe=False,
      install_requires=sp_install_requires,
      tests_require=sp_tests_require,
      include_package_data=True)
