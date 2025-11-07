from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='scrapy-delta-guard',
    version='0.0.5',
    author='Abdul Nazar',
    description='A Scrapy extension to detect data changes (deltas) between scraped items and a database.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/nazaradn/scrapy-delta-guard',
    packages=find_packages(),
    install_requires=[
        'Scrapy>=2.0.0',
        'SQLAlchemy>=1.3.0',
        'requests>=2.25.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Scrapy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
