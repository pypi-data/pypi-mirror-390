

# ⚙️ STEP 4: Create `setup.py`

from setuptools import setup, find_packages

setup(
    name='shivml',
    version='0.0.1',
    author='Shivam Vinod Chaudhari',
    author_email='shivam7744998850@gmail.com',
    description='An automatic Machine Learning trainer by Shivam.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'scikit-learn',
        'joblib'
    ],
    python_requires='>=3.6'
)
