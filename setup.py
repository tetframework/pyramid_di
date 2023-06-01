from pathlib import Path

from setuptools import setup, find_packages

here = Path(__file__).parent
README = (here / "README.md").read_text()
CHANGES = (here / "CHANGES.md").read_text()

requires = ["pyramid>=1.7,<3.0", "pyramid_services>=1.1,<2.0"]
dev_requires = ["pytest>=3.0", "pytest-cov"]

setup(
    name="pyramid_di",
    version="0.4.2",
    description="Dependency injection stuff for Pyramid",
    long_description=README + "\n\n" + CHANGES,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pyramid",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    author="Antti Haapala",
    author_email="antti.haapala@anttipatterns.com",
    url="http://github.com/tetframework/pyramid_di",
    keywords="web wsgi bfg pylons pyramid",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={"dev": dev_requires},
)
