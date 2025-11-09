from setuptools import setup, find_packages

setup(
    name='hand_recog',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'mediapipe>=0.8.9',
        'opencv-python>=4.5.0'],
    description='A package for hand recognition using MediaPipe and OpenCV',
    long_description=open('README.md').read(),
)