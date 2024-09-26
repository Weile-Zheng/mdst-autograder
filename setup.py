from setuptools import setup, find_packages

setup(
    name='autograder',
    version='0.1.0',
    description='Autograding submission portal for MDST',
    author='Weile Zheng',
    author_email='weilez@umich.edu',
    packages=find_packages(where='.'),
    install_requires=[
        'werkzeug',
        'pytest',
        'supabase',
        'flask',
        'jinja2'
    ],
)