from setuptools import setup, find_packages


setup(
    name='beu',
    version='0.1.2',
    description='Beginner Express .:. Back End .:. Big Example .:. Brainstorm Effectively',
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/beu',
    download_url='https://github.com/kenjyco/beu/tarball/v0.1.2',
    packages=find_packages(),
    install_requires=[
        'redis-helper',
        'input-helper',
        'mocp',
        'chloop',
        'youtube-dl',
        'click',
        'requests',
        'lxml',
        'beautifulsoup4',
    ],
    include_package_data=True,
    package_dir={'': '.'},
    package_data={
        '' : ['*.ini'],
    },
    entry_points={
        'console_scripts': [
            'download=beu.download:download',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    keywords = []
)