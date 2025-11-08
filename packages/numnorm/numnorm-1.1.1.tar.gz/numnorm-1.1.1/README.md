# numnorm
### Под английским - на русском :-)
****
*The library provides safe and universal normalization of alternative input formats for numerical data. It handles both direct numeric values and string representations of numbers, bringing them into compliance with Python’s number notation standards and converting them to int or float types.*
*At the same time, for data that are not numeric, the library guarantees preservation of the original data type and value — no information loss occurs.*
*The library is robust when processing input data of various classes: ***str, int, float, list, tuple, dict, set, bool, complex, object*** — none of these types will cause an error during its operation.*
  
*The code below provides some examples of alternative number input formats, both numeric and string, that the library can correctly process, normalize, and convert to the appropriate data type.*
```python
from numnorm import norm

num_1 = 4/2
num_2 = -0.0
num_3 = '-,5'
num_4 = '+000,000'
num_5 = '-123,0'
num_6 = '+123,500'
print (num_1, type(num_1), norm(num_1), type(norm(num_1)))
print (num_2, type(num_2), norm(num_2), type(norm(num_2)))
print (num_3, type(num_3), norm(num_3), type(norm(num_3)))
print (num_4, type(num_4), norm(num_4), type(norm(num_4)))
print (num_5, type(num_5), norm(num_5), type(norm(num_5)))
print (num_6, type(num_6), norm(num_6), type(norm(num_6)))
```
Output:
```python
     2.0 <class 'float'>    2 <class 'int'>
    -0.0 <class 'float'>    0 <class 'int'>
     -,5 <class 'str'>   -0.5 <class 'float'>
+000,000 <class 'str'>      0 <class 'int'>
  -123,0 <class 'str'>   -123 <class 'int'>
+123,500 <class 'str'>  123.5 <class 'float'>
```
### *Usage*
*Import the* **norm** *unction from the* **numnorm** *library:*
```python
from numnorm import norm
```
### *Accessing the function:* 

result = **norm**(data)
```
where:
      data   - input data to be processed;
      result - processing result of the input data.
```
## *Installation*
Install the package using pip:
```bash
pip install numnorm
```
****
Moscow, Russia, 2025  
Maxim Y. Klimkov, +7 (916) 386-38-32, Klimkov@inbox.ru
****
>
****
*Библиотека обеспечивает безопасную и универсальную нормализацию альтернативных форматов ввода числовых данных. Она работает как с непосредственными числовыми значениями, так и со строковыми представлениями чисел, приводя их к стандартам записи чисел в Python и преобразуя в типы int или float.*
*При этом для данных, которые не являются числовыми, библиотека гарантирует сохранение исходного типа и значения — никакой потери информации не происходит.*
*Библиотека устойчива к входным данным различных классов: ***str, int, float, list, tuple, dict, set, bool, complex, object*** — ни один из этих типов не приведёт к возникновению ошибки в процессе её работы.*
  
*В коде ниже представлены некоторые примеры альтернативных форматов ввода чисел — как в числовом, так и в строковом виде, — которые библиотека способна корректно обработать, нормализовать и привести к соответствующему типу данных.*
```python
from numnorm import norm

num_1 = 4/2
num_2 = -0.0
num_3 = '-,5'
num_4 = '+000,000'
num_5 = '-123,0'
num_6 = '+123,500'
print (num_1, type(num_1), norm(num_1), type(norm(num_1)))
print (num_2, type(num_2), norm(num_2), type(norm(num_2)))
print (num_3, type(num_3), norm(num_3), type(norm(num_3)))
print (num_4, type(num_4), norm(num_4), type(norm(num_4)))
print (num_5, type(num_5), norm(num_5), type(norm(num_5)))
print (num_6, type(num_6), norm(num_6), type(norm(num_6)))
```
Результат:
```python
     2.0 <class 'float'>    2 <class 'int'>
    -0.0 <class 'float'>    0 <class 'int'>
     -,5 <class 'str'>   -0.5 <class 'float'>
+000,000 <class 'str'>      0 <class 'int'>
  -123,0 <class 'str'>   -123 <class 'int'>
+123,500 <class 'str'>  123.5 <class 'float'>
```
### *Использование:*

*Импортируйте функцию* **norm** *из библиотеки* **numnorm** *:*
```python
from numnorm import norm
```

### *Обращение к функции:* 

result = **norm**(data)
```
где:
    data   - исходные данные для обработки;
    result - результат обработки исходных данных.
```
## Установка
Установите пакет через pip:
```bash
pip install numnorm
```
****
Москва, Россия, 2025  
Климков Максим, +7 (916) 386-38-32, Klimkov@inbox.ru
****