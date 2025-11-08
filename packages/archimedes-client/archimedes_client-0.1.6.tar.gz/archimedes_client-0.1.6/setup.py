from setuptools import setup, find_packages

setup(
    name='archimedes_client',
    version='0.1.6',
    packages=find_packages(),
    install_requires=[
        'requests>=2.20.0', 
        'python-dotenv>=0.19.0',
    ],
    author='Gabriel Moreira da Silva',
    author_email='silvamoreira@gmail.com',
    description='Cliente Python para o RPA se comunicar com a  API do Orquestrador Archimedes.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gabriell404/archimedes-client',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8', 
)