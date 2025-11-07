from setuptools import setup, find_namespace_packages

setup(
    packages=find_namespace_packages(include=["livekit.*"]),
    package_data={
        "livekit.plugins.n8n": ["py.typed"],
    },
)