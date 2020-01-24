from setuptools import setup, find_packages

setup(
    name='metalparser',
    version='0.6.9b1',
    description='Python library for heavy metal song lyrics, albums, song titles and other info.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license='MIT',
    author='Luca Ballore',
    author_email='luca@ballore.eu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    url='https://github.com/lucone83/metal-parser',
    project_urls={
        'Bug Reports': 'https://github.com/lucone83/metal-parser/issues',
        'Disclaimer': 'https://github.com/lucone83/metal-parser/blob/master/DISCLAIMER.md',
        'Docs': 'https://metalparser.readthedocs.io/',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/lucone83/metal-parser'
    },
    packages=find_packages('src', exclude='tests'),
    package_dir={'': 'src'},
    include_package_data=True,
    python_requires='>=3.4.*, <=3.8',
    master_doc='index',
    install_requires=['beautifulsoup4', 'ratelimit', 'requests', 'requests_cache'],
    keywords='heavy metal darklyrics lyrics song api'
)
