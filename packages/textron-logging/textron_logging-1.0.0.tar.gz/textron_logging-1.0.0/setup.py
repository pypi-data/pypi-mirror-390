from setuptools import setup, find_packages

setup(
    name="textron_logging",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "azure-monitor-opentelemetry",
        "logging"
    ],
    description="Standard logging for Textron apps with Application Insights",
    author="YourName",
)