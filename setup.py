from setuptools import setup, find_packages

setup(
    name='sangreal-wind',
    version='0.0.31',
    description=('short cut api for wind'),
    install_requires=[
        'sangreal-db',
        'sqlalchemy',
        'attrs',
    ],
    # long_description=open('README.rst').read(),
    author='liubola',
    author_email='lby3523@gmail.com',
    # maintainer='<维护人员的名字>',
    # maintainer_email='<维护人员的邮件地址',
    license='GNU General Public License v3.0',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/liubola/sangreal-wind',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)
