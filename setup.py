from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

setup(
    name='beu',
    version='0.1.33',
    description='Beginner Express .:. Back End .:. Big Example .:. Brainstorm Effectively',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/beu',
    download_url='https://github.com/kenjyco/beu/tarball/v0.1.33',
    packages=find_packages(),
    install_requires=[
        'aws-info-helper',
        'bg-helper',
        'chloop',
        'click',
        'dt-helper',
        'easy-workflow-manager',
        'fs-helper',
        'input-helper',
        'jira-helper',
        'mongo-helper',
        'parse-helper',
        'redis-helper',
        'settings-helper',
        'sql-helper',
        'webclient-helper',
        'yt-helper',
    ],
    include_package_data=True,
    package_dir={'': '.'},
    package_data={
        '': ['*.ini'],
    },
    entry_points={
        'console_scripts': [
            'beu-ipython=beu.scripts.shell:main',
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
