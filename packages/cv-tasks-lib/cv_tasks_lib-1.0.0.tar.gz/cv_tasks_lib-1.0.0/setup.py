from setuptools import setup, find_packages

setup(
    name="cv_tasks_lib",
    version="1.0.0",
    description="Computer Vision tasks library (9 educational examples)",
    author="CV Tasks",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "matplotlib",
        "scikit-image",
        "scikit-learn"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
