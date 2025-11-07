from setuptools import setup,find_packages
setup(name='extzip',
      version='0.2',
      description='zip extfile in path',
      long_description='zip file in path with ext defalut csv/txt',
      long_description_content_type="text/markdown",
      url='https://gitee.com/wdy0401/zipdir',
      author='wangdeyang',
      author_email='wdy0401@gmail.com',
      license='MIT',     
      packages=find_packages(),
      install_requires=[
        "syutils>=0.0.5"],
      zip_safe=False)