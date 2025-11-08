from setuptools import setup, find_packages

setup(
    name='mini_lemmatizer',
    version='0.1.1',
    author='Sania Jain',
    author_email='saniiasjain@gmail.com',  # update before publishing
    description='A simple, lightweight lemmatization utility built with NLTK.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mini_lemmatizer',  # optional
    packages=find_packages(),
    install_requires=['nltk>=3.9'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
