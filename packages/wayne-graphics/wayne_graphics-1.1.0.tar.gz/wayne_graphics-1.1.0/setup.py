from setuptools import setup, find_packages

setup(
    name='wayne-graphics',
    version='1.1.0',
    packages=find_packages(include=['graphics', 'graphics.*']),
    install_requires=[],
    description='CMU-style graphics wrapper using tkinter',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Wayne',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)