import os, sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.7',
    'pyramid_services',
]

setup(name='pyramid_di',
      version='0.1dev',
      description='Dependency injection stuff for Pyramid',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Pyramid",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Python Software Foundation License",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
          "Topic :: Software Development :: Libraries :: Application Frameworks"
      ],
      author='Antti Haapala',
      author_email='antti.haapala@anttipatterns.com',
      url='http://www.anttipatterns.com',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
)
