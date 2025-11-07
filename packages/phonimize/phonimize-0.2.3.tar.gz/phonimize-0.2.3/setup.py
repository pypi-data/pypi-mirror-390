from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='phonimize',
    version='0.2.3',
    author='Arcosoph',
    author_email='a5tkabid@gmail.com',
    description='Multilingual grapheme-to-phoneme (G2P) conversion using Transformer models.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    install_requires=[
        'torch>=2.8,<2.9',
        'numpy>=2.0,<3.0'
    ],
    extras_require={
        'tests': ['pytest', 'pytest-cov'],
        'docs': ['mkdocs', 'mkdocs-material'],
        'dev': ['bumpversion']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Sound/Audio :: Speech'
    ],
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    package_data={'': ['*.yaml']}
)
