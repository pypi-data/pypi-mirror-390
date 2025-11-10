from setuptools import setup, find_packages

setup(
    name='simple_summarizer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'nltk',
    ],
    entry_points={
        'console_scripts': [
            'summarize=simple_summarizer.summarize:summarize_text_cli', # We will create this entry point later
        ],
    },
    author='Arhaan Motiwala', # Replace with your name
    author_email='arhaanmotiwala11@gmail.com', # Replace with your email
    description='A simple text summarization library using NLTK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/arhaan15/simple_summarizer', # Replace with your GitHub repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Or your preferred license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
