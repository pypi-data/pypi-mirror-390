from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        # Download NLTK resources after install
        try:
            subprocess.check_call([sys.executable, "-m", "nltk.downloader",
                                   "averaged_perceptron_tagger_eng", "wordnet",
                                   "stopwords", "punkt_tab"])
        except Exception as e:
            print(f"⚠️ Failed to download NLTK resources: {e}")

setup(
    name="TPTK",
    version="1.0.3",  
    author="Gaurav Jaiswal",
    author_email="jaiswalgaurav863@gmail.com",
    description="Automate text preprocessing tasks with ease.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Gaurav-Jaiswal-1/Text-Preprocessing-Toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "nltk>=3.6.0",
        "pyspellchecker>=0.7.1",
        "pandas>=1.2.0",
    ],
    python_requires=">=3.8",
    cmdclass={
        "install": PostInstallCommand,
    },
)
