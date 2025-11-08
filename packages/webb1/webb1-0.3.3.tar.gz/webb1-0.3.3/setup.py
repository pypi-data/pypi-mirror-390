from setuptools import setup, find_packages

setup(
    name="webb1",          # pip install webb1
    version="0.3.3",       # increase version every upload
    packages=["web1"],     # ✅ import folder name
    author="Unknown",
    description="Web Development Practical Notes: PHP, C#, ASP.NET",
    long_description="Contains all important web practical exam programs.",
    long_description_content_type="text/plain",
    python_requires=">=3.7",
)
