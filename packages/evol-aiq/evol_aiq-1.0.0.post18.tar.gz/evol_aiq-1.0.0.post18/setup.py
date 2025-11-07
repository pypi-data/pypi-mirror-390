from setuptools import setup, find_packages
import os
import logging

logger = logging.getLogger(__name__)
build_version = os.environ.get("EVOL_AIQ_VERSION", "0.1.1")
logger.info("EVOL_AIQ_VERSION = %s", build_version)
setup(
        name='evol-aiq',
        version=build_version,
        description='Evolving AIQ base build',
        author='Evolving AIQ Team (PD,RK)',
        author_email='your.email@example.com',
        packages=find_packages(),
        install_requires=[
            'pandas',  # List any dependencies here, e.g., 'requests>=2.20.0',
            'Flask',
            'gunicorn',
            'pyyaml',
            'scikit-learn',
            'matplotlib',
            'numpy',
            'joblib',
            'fastapi',
            'missingno',
            'seaborn',
            'lightgbm',
            'xgboost'
        ],
    )