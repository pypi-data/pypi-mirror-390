# This is a library of utility codes with features to facilitate the development and programming of language model algorithms from Sapiens Technology®.
# All code here is the intellectual property of Sapiens Technology®, and any public mention, distribution, modification, customization, or unauthorized sharing of this or other codes from Sapiens Technology® will result in the author being legally punished by our legal team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'utilities_nlp'
version = '3.0.3'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'TTS==0.22.0',
        'sapiens-transformers',
        'sapiens-infinite-context-window',
        'paddleocr==2.7.3',
        'paddlepaddle',
        'pillow',
        'cloudinary',
        'count-tokens',
        'tiktoken',
        'opencv-python',
        'opencv-python-headless',
        'ffmpeg-python',
        'gTTS',
        'pydub',
        'noisereduce',
        'yt-dlp',
        'youtube-search-python',
        'youtube-transcript-api',
        'moviepy',
        'certifi',
        'beautifulsoup4',
        'numpy',
        'fasttext',
        'langid',
        'langdetect',
        'requests',
        'mutagen',
        'openai-whisper',
        'setuptools-rust',
        'fpdf',
        'reportlab',
        'python-docx',
        'docx',
        'openpyxl',
        'pandas',
        'XlsxWriter',
        'python-pptx',
        'matplotlib',
        'seaborn',
        'graphviz',
        'networkx',
        'wordcloud',
        'rembg',
        'onnxruntime',
        'super-image',
        'huggingface-hub'
    ],
    url='https://github.com/sapiens-technology/utilities_nlp',
    license='Proprietary Software'
)
# This is a library of utility codes with features to facilitate the development and programming of language model algorithms from Sapiens Technology®.
# All code here is the intellectual property of Sapiens Technology®, and any public mention, distribution, modification, customization, or unauthorized sharing of this or other codes from Sapiens Technology® will result in the author being legally punished by our legal team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
