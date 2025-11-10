from setuptools import setup

with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='deitheon',
      version='0.1.1',
      description='deitheon Package',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Your Name',
      author_email='your.email@example.com',
      url='https://github.com/yourusername/deitheon',
      packages=['deitheon'],
      install_requires=["numpy", "pandas",
                        "matplotlib", "utilum", "datasalgo", "tensorflow", "torch", "transformers"],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      zip_safe=False,
      )
