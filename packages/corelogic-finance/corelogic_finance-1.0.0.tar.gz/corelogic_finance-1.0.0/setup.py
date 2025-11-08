from setuptools import setup, find_packages

setup(
    name='corelogic-finance',
    version='1.0.0',
    description='Una librería robusta y precisa para cálculos financieros y de negocios.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Luis Alejandro Martinez Marin',
    author_email='lalejandro.2005martinez@gmail.com',
    url='https://github.com/Aspy2005/corelogic-finance',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'numpy-financial',
        'pandas',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires='>=3.11',
)