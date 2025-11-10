from setuptools import setup, find_packages
setup(name="noamath",
      version="0.0.4",
      author="Noah Edward Holmén",
      author_email="GanonBlasterTheGrey@gmail.com",
      description="A Math Library",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[],
      python_requires=">=3.6",
      license="source - available license",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent"
      ],
      zip_safe=False
      )