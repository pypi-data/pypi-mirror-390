
from setuptools import setup


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='numnorm',
    version='1.1.1',
    author='Климков Максим',
    author_email='Klimkov@inbox.ru',
    description='Библиотека для безопасной универсальной нормализации альтернативных форматов ввода числовых данных — как в виде чисел, так и в виде строк с числовыми значениями — к стандартам записи чисел в Python и типизации их в int или float, а для случаев, когда входные данные не являются числовыми, библиотека гарантирует возврат данных с сохранением исходного типа и значения.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitverse.ru/Klimkov/numnorm',
    license='MIT',
    keywords=['number', 'parsing', 'type-conversion', 'data-cleaning', 'robust'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Typing :: Typed'
    ],
    python_requires='>=3.7',
    py_modules=['numnorm']
)
