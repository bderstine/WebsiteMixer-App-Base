import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='websitemixer',
    version='1.0.0',
    url='https://websitemixer.com',
    license='MIT',
    maintainer='Brad Derstine',
    maintainer_email='brad@bizzartech.com',
    description='A Python/Flask alternative to WordPress and Drupal',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
