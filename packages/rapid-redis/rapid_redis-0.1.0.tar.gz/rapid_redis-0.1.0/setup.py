from setuptools import setup, find_packages

setup(
    name='rapid-redis',  
    version='0.1.0',
    description='A lightweight in-memory cache inspired by Redis (educational)',
    author='Atharsh K',
    author_email='atharshkrishnamoorthy@gmail.com',
    url='https://github.com/AtharshKrishnamoorthy/RAPID-REDIS.git',  
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
