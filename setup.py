from setuptools import setup, find_packages

setup(
    name='mth308lib',                    
    version='0.1.0',
    description='Numerical methods library for MTH308 with CLI support',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/aditya70615/MTH_308_assignments',
    packages=find_packages(),
    py_modules=['cli'],                  
    install_requires=[],                
    entry_points={
        'console_scripts': [
            'mth308=cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change if needed
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
