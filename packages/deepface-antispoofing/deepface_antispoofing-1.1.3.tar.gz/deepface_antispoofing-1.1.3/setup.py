from setuptools import setup, find_packages

setup(
    name="deepface-antispoofing",
    version="1.1.3",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'deepface_antispoofing': [
            'data/haarcascade_frontalface_default.xml',
        ]
    },
    install_requires=[
        "requests",
        "opencv-python",
        "numpy",
        "tensorflow",
        "flask",
        "flask-cors",
    ],
    description="A comprehensive Python package for advanced face recognition, anti-spoofing, deepfake detection, emotion analysis, and face mask detection. Offers robust analysis to distinguish real faces from printed images, replay attacks, and presentation attacks, alongside precise age, gender, emotion, mask status, and genuine vs. AI-generated face predictions. Ideal for secure authentication and identity verification systems.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="IP Softech - Pratham Pansuriya",
    author_email="ipsoftechsolutions@gmail.com",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)