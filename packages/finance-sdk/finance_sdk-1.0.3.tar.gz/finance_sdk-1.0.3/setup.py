from setuptools import setup, find_packages

setup(
    name='finance_sdk',
    version='1.0.3',
    description='SDK for Finance Module',
    author='WLC Soluções',
    author_email='analiciasouza.11@gmail.com',
    url='https://github.com/wlc-solucoes/wlc-sdk-financeiro.git',
    packages=find_packages(include=['finance_sdk', 'finance_sdk.*']),
    install_requires = ["django", "djangorestframework"],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django' , 
        'Intended Audience :: Developers', 
        'Programming Language :: Python'
     ],
    
)