from setuptools import setup, find_packages

setup(
    name='maxo',  # Имя пакета — то, что вы хотите занять
    version='0.1.0',  # Начальная версия
    description='Моя библиотека maxo — заглушка для резерва',
    author='Ваше имя',
    author_email='your.email@example.com',
    packages=find_packages(),  # Автоматически найдёт maxo/
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Или ваша лицензия
    ],
    python_requires='>=3.6',
)