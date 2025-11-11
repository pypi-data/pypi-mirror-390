from setuptools import setup, find_packages
# import versioneer

def get_versions():
    version = "0.1.1"

setup(
    name="SCMG-toolkit",
    version="0.1.1",      # <-- 手动写版本
    packages=find_packages(),
    # cmdclass=versioneer.get_cmdclass(),
    )
