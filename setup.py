from distutils.core import setup

setup(
    name='django-verbose-logging',
    version='0.0.1',
    packages=['django_verbose_logging'],
    package_dir={'': 'src'},
    url='https://github.com/TargetHolding/django-verbose-logging',
    license='Apache License 2.0',
    description='Verbose exception logging for Django',
    install_requires=['Django>=1.7',]
)
