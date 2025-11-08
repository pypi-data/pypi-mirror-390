# UserResponseCollector

Source code: [GitHub](https://github.com/KevinRGeurts/UserResponseCollector)
---
UserResponseCollector is a Python library that facilitates the collection of user responses from the command line (Console).
It supports text string input, selection from a list of options, integer input, floating point input, and
input of file paths for opening or saving files.

It is extensible, allowing developers to create custom input types as needed. It can also be extended to obtain input
from other sources, such as a graphical user interface.

The Command design pattern is followed:
- The Receiver participant interface is defined, and the Console implementation is provided.
- The Command participant interface is defined, and multiple ConcreteCommand implementations
  (e.g., for selecting from a list of options or entering an integer) are provided.

Extensibility is achieved by creating new ConcreteCommand classes that implement the Command interface, if a new
type of input is needed. UserQueryCommand child classes (e.g. UserQueryCommandNumberInteger) must implement:
- ```_doCreatePromptText()``` - Generates string of text used to prompt user for input
- ```_doProcessRawResponse(...)``` - Converts the raw response text string of user input to an object of required type
- ```_doValidateProcessedResponse(...)``` - Tests that the object of required type meets any other requirements, such
											as that an entered integer is greater than or equal to a minimum value

If a new source of input is needed, a new Receiver subclass can be created that implements the Receiver interface.

## Credit where credit is due
- Command and Template Method (followed by UserQueryCommand.Execute()) design patterns follow the concepts, UML diagrams,
  and examples provided in "Design Patterns: Elements of Reusable Object-Oriented Software," by Eric Gamma, Richard Helm,
  Ralph Johnson, and John Vlissides, published by Addison-Wesley, 1995.
- UserQueryReceiver_GetCommandReceiver is a global prebound method that returns the global, single instance of a concrete
  UserQueryReceiver. The Global Object design pattern and Prebound Method design pattern described by Brandon Rhodes are followed.
  See for reference: (1) Global Object Pattern: https://python-patterns.guide/python/module-globals/,
  (2) Prebound Method Pattern: https://python-patterns.guide/python/prebound-methods/

## Basic usage
The simplest way to use the library is through the functions it provides for each input type. Note that all the usage
examples below assume that the ```UserResponeCollector``` package has been installed from PyPI, and is available for import.
If this is not the case, and you are just working with the source code, adjust the import statements by dropping
the leading 'UserResponseCollector.' from the module paths.

### Integer input
```python
from UserResponseCollector.UserQueryCommand import askForInt
number = askForInt(query_preface='How many widgets will you purchase?', minimum=1, maximum=100)
```

The user will be prompted to enter an integer between 1 and 100, with the question, "How many widgets will you purchase?".
If the user enters text that cannot be converted to an integer, or an integer outside the specified range,
they will be prompted to try again. For example:

```
How many widgets will you purchase?
Enter and integer number between 1 and 100: 150

'150' is greater than 100. Please try again.
How many widgets will you purchase?
Enter and integer number between 1 and 100: 90
```

The minimum and maximum arguments to the function can be set to None (which are the defaults) if limits are not required.

### Floating point input
```python
from UserResponseCollector.UserQueryCommand import askForFloat
price = askForFloat(query_preface='What is the price of the widget in dollars?', minimum=0.25, maximum=100)
```

The user will be prompted to enter a floating point number between 0.25 and 100, with the question,
"What is the price of the widget in dollars?". If the user enters text that cannot be converted to a float,
or a float outside the specified range, they will be prompted to try again. For example:

```
What is the price of the widget in dollars?
Enter a floating point number between 0.25 and 100: 0

'0' is less than 0.25. Please try again.
What is the price of the widget in dollars?
Enter a floating point number between 0.25 and 100: 50.75
```

The minimum and maximum arguments to the function can be set to None (which are the defaults) if limits are not required.

### Text string input
```python
from UserResponseCollector.UserQueryCommand import askForStr
name = askForStr(query_preface='What is your name?', max_length=15)
```

The user will be prompted to enter a text string with the question, "What is your name?". If the user enters a
string that is shorter than 1 character or longer than 25 characters, they will be prompted to try again. For example:

```
What is your name?
Enter a string of text no longer than 15 characters.George Washington

'George Washington' is longer than 15 characters. Please try again.
What is your name?
Enter a string of text no longer than 15 characters.G. Washington
```

The default maximum length is 25 characters. The argument can be set to None if there is no character limit.

### Menu selection input
```python
from UserResponseCollector.UserQueryCommand import askForMenuSelection
name = askForMenuSelection(query_preface='What option do you want?', query_dic={'a':'Option A', 'b':'Option B'})
```

The user will be prompted to enter text corresponding to one of the keys in the query_dic argument. If the user enters a
string that does not match one of the keys, they will be prompted to try again. For example:

```
What option do you want?
Choose (a)Option A, (b)Option B: 2

'2' is not a valid response. Please try again.
What option do you want?
Choose (a)Option A, (b)Option B: a
```

### Path for saving file input
```python
from UserResponseCollector.UserQueryCommand import askForPathSave
name = askForPathSave(query_preface='Where do you wish to save the data?')
```

The user will be prompted to enter a file path with the question, "Where do you wish to save the data?". If the user enters an
invalid file path, they will be asked to try again. If the file path already exists, the user will be asked to confirm that they
wish to overwrite it. For example:

```
Where do you wish to save the data?
Enter a valid file system path, without file extension, and with escaped backslashes.C:\\temp\\junk.txt

'C:\\temp\\junk.txt' is an existing file. Do you want to overwrite it?
Choose (y)Yes, (n)No:
```

#### Current limiations/issues:
- The direction to not include a file extension is provided under the assumption that the file path is intended for saving a pickle file.
- The testing in the code for the validity of the file path is not reliable.

### Path for opening file input
```python
from UserResponseCollector.UserQueryCommand import askForPathOpen
name = askForPathOpen(query_preface='Which data file do you wish to open?')
```

The user will be prompted to enter a file path with the question, "Which data file do you wish to open?". If the user enters an
invalid file path, they will be asked to try again. For example:

```
Which data file do you wish to open?
Enter a valid file system path, without file extension, and with escaped backslashes.C:\\temp\\junk.txt

'C:\\temp\\junk.txt' is not a valid file path. Please try again.
```

#### Current limiations/issues:
- The direction to not include a file extension is provided under the assumption that the file path is intended for opening a pickle file.
- The testing in the code for the validity of the file path is not reliable.

## Advanced Usage
It is also possible to use the Receiver and Command objects directly to obtain input, rather than using the functions that wrap these objects.
Note that the usage example below assumes that the ```UserResponeCollector``` package has been installed from PyPI, and is available for import.
If this is not the case, and you are just working with the source code, adjust the import statements by dropping
the leading 'UserResponseCollector.' from the module paths. Make the same adjustment in the ```receiver = ...``` line below.

### Integer input
```python
from UserResponseCollector.UserQueryCommand input UserQueryCommandNumberInteger
import UserResponseCollector.UserQueryReceiver
# Build a query for the user to obtain an integer
receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
query_preface = 'How many widgets will you purchase?'
command = UserQueryCommandNumberInteger(receiver, query_preface, minimum = 1, maximum = 100)    
# Initiate the input request
response = command.Execute()
# Print the response
print(f"You entered the integer {response}.")
```

## Unittests

Unittests for the UserQueryReceiver are in the tests directory, with filenames starting with test_. To run the unittests,
type ```python -m unittest discover -s ..\..\tests -v``` in a terminal window in the src\UserResponseCollector directory.

## License
MIT License. See the LICENSE file for details

