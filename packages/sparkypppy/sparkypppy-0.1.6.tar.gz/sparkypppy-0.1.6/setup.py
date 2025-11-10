from setuptools import setup, find_packages

setup(
    name='sparkypppy',
    version='0.1.6',
    author='Enzo Martini',
    author_email='enzomartini.1995@gmail.com',
    description='A simple scala spark practice package with practicals (prac1–prac6).',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
