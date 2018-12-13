from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

setup(
    name='beu',
    version='0.1.23',
    description='Beginner Express .:. Back End .:. Big Example .:. Brainstorm Effectively',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/beu',
    download_url='https://github.com/kenjyco/beu/tarball/v0.1.23',
    packages=find_packages(),
    install_requires=[
        'redis-helper',
        'input-helper',
        'mocp',
        'chloop',
        'yt-helper',
        'parse-helper',
        'bg-helper',
        'mocp-cli',
        'fs-helper',
        'settings-helper',
        'dt-helper',
        'jira-helper',
        'aws-info-helper',
        'easy-workflow-manager',
        'click',
        'ipython',
    ],
    include_package_data=True,
    package_dir={'': '.'},
    package_data={
        '': ['*.ini'],
    },
    entry_points={
        'console_scripts': [
            'beu-ipython=beu.scripts.shell:main',
            'beu-trending=beu.scripts.trending:main',
            'beu-related-to=beu.scripts.related_to:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    keywords = []
)
