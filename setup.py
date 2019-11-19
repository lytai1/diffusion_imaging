import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="diffusion-imaging",
	version="0.1",
	author="Matthew Jones",
	author_email="i@ammatt.com",
	description="A package to do diffusion imaging based around a combination of packages",
	long_description="A wrapper package around various diffusion imaging based packages to stream line the process of building and training models",
	long_description_content_type="text/markdown",
	url="https://github.com/plyte/diffusion_imaging",
	packages=setuptools.find_packages(),
	install_requires=[
		"dependency-injector",
		"dipy",
		"nibabel",
		"dmipy",
		"numpy"
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)