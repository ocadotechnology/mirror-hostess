
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


packages = find_packages(exclude=('docs', 'examples', 'hostess_old'))

class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        from pylint import epylint as lint
        from io import StringIO
        lint.py_run(' '.join(packages))
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests', '-m', '^test', 
                                         '--with-coverage', 
                                         '--cover-package', 'hostess',
                                         '--cover-min-percentage', '100'])


with open('README.md') as f:
    readme = f.read()

setup(
    name                 = 'hostess',
    version              = '0.2.0',
    description          = 'Manage your /etc/hosts to point to local kubernetes services.',
    long_description     = readme,
    author               = 'Ocadotechnology',
    url                  = 'https://github.com/ocadotechnology/mirror-hostess',
    packages             = packages,
    include_package_data = True,
    install_requires     = ['kubernetes', 'python-hosts', 'filelock'],
    tests_require = [
        'coverage',
        'nose',
        'pylint',
    ],
    cmdclass={'test': NoseTestCommand},
)
