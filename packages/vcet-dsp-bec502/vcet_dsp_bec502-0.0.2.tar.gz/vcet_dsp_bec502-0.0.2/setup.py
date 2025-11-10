from setuptools import setup, find_packages 
long_description='''This is a light weighted DSP library without numpy package, which includes dsp algorithms such as 
Linear convolution, Circular convolution, Finding the solution for Difference Equation, Discrete time
Fourier Transform(DTFT), Discrete Fourier Series(DFS), N-point Discrete Fourier transform(DFT),
Overlap save, Overlap add, Discrete cosine transform, Discrete wavelet transform(2-level decomposition 
using Haar wavelet), Radix-2 DIT-FFT, Radix-2 DIF-FFT, FIR low-pass filter and FIR High-pass filter using
Hamming window technique.
#usage
import vcet_dsp_bec502 as dsp
print(dsp.lin_conv([1,2,3],[1,2,3]))
Change Log

===============

0.0.2(10/11/2025)

Second Release

===============
'''  
classifiers = ['Development Status :: 3 - Alpha',
               'Environment :: Console',
               'Intended Audience :: Education',
               'License :: OSI Approved :: MIT License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Scientific/Engineering'
]

setup(
    name='vcet_dsp_bec502',
    version='0.0.2',
    description='Basic DSP library without numpy',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shivarao101/vcet-dsp-bec502',
    author='Shivaprasad',
    author_email='shivarao101@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='DFT, IDFT, DFS, DTFT, DCT, DWT, Radix-2 DIT & DIF, Overlap save and add',
    packages=find_packages(),
)