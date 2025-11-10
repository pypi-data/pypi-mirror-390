from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name='animageo',
    version='0.1.11',
    author='ivaleo',
    author_email='ivaleotion@gmail.com',
    description='Tools for using GeoGebra construction, processing with Manim animation and exporting to SVG and MP4',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='http://animageo.ru/',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['animageo=animageo.__main__:main'],
    },
    install_requires=[
        'requests>=2.25.1',
        'numpy>=1.26.0',
        'manim>=0.19.0',
        'pycairo>=1.0.0',
        'lark>=1.1.5'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent'
    ],
    license='MIT',
    keywords='geometry dynamic geogebra manim animation drawing svg mp4 python',
    python_requires='>=3.9'
)