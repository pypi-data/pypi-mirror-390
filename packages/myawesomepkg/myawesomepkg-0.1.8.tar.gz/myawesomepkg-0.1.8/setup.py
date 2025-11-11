from setuptools import setup, find_packages

setup(
    name='myawesomepkg',                   # Your package name
    version='0.1.8',                       # Current version
    author='Your Name',                    # Replace with your actual name
    author_email='your.email@example.com', # Optional: add your email
    description='A simple greeting library',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],                   # List dependencies here, e.g., ['numpy']
    python_requires='>=3.6',
    classifiers=[                          # Optional but good for PyPI listings
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change to your license
        'Operating System :: OS Independent',
    ],
)
