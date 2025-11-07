from setuptools import setup, find_packages

setup(
    name="mr_nobody",                # The name you'll use in pip install
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={"myprograms": ["*.c"]},  # Include all .c files
    description="Collection of 10 C programs",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/yourusername/myprograms",
)
