"""
Defines the interface and concrete implementations of UserQueryCommands classes that know how to query the
user for different types of input (e.g., menu choice, integer number, file path) via a UserQueryReceiver concrete
implementation.

Following the Command design pattern, the Command participant interface is defined, and and multiple ConcreteCommand
implementations are provided.

Exported Classes:
    UserQueryCommand -- Interface (abstract base) class for Command.
    UserQueryCommandX -- Concrete UserQueryCommand that invokes methods on UserQueryReceiver to obtain user input of type X.
    
Exported Exceptions:
    None    
 
Exported Functions:
    askForMenuSelection(...) -- Convenience function to query user to select a menu option without using objects.
    askForInt(...) -- Convenience function to query user for an integer number without using objects.
    askForFloat(...) -- Convenience function to query user for a floating point number without using objects.
    askForStr(...) -- Convenience function to query user for a text string without using objects.
    askForPathSave(...) -- Convenience function to query user for a path to save a file without using objects.
    askForPathOpen(...) -- Convenience function to query user for a path to open a file without using objects.
"""

# Standard
import sys
from multiprocessing import process
from pathlib import Path

# Local
import UserResponseCollector.UserQueryReceiver

# TODO: Remove or comment out debug print for release. This was added to help understand
# and debug package import behavior.
# print("In module UserQueryCommands sys.path[0], __package__ ==", sys.path[0], __package__)

class UserQueryCommand(object):
    """
    Following the Command design pattern, this is the abstract base or interface class for ConcreteUserQueryCommand classes that know how to execute
    various user querys by invoking methods on UserQueryReceiver.

    Each child must by convention and necessity implement these methods:
        Execute(...) - Called to obtain a response from the user, of a type which can differ for each child.
    """
    def __init__(self, receiver=None, query_preface = ''):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command, must be a UserQueryReceiver instance.
        :parameter query_preface: Text displayed to the user to request their response, string
        """
        assert(isinstance(receiver, UserResponseCollector.UserQueryReceiver.UserQueryReceiver))
        self._receiver = receiver
        self._query_preface = query_preface
    
    def Execute(self):
        """
        Following the Template Method design pattern, Execute is a template method that is called to obtain a
        response from the user. This method requires that the following primitive operations are implemented.
            (1) doCreatePromptText(...)
            (2) doProcessRawResponse(...)
            (3) doValidateProcessedResponse(...)
        :return: The user's response as object of required type, which can differ for each subclass of UserQueryCommand        
        """
        processed_response = None
        
        prompt_text = self._doCreatePromptText()

        while processed_response is None:
                
            # Ask the receiver/user for a raw response, which will be in the form of a string
            raw_response = self._receiver.GetRawResponse(prompt_text)
        
            # Process the response from the receiver/user into an object of required type
            (processed_response, error_msg) = self._doProcessRawResponse(raw_response)
            
            if processed_response is None:
                # Raw response could not be converted to an object of the required type. Issue error message.
                self._receiver.IssueErrorMessage(error_msg)
            else:
                # Raw response could be converted to an object of the required type. Check validity.
                (isValid, error_msg) = self._doValidateProcessedResponse(processed_response)
                if not isValid:
                    # Processed response is an object of right type but of invalid value. Issue error message.
                    self._receiver.IssueErrorMessage(error_msg)
                    # Set processed_respone to None, so that we go around again asking user for input
                    processed_response = None
                
        return processed_response

    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() is an abstract primitive operation to
        generate a suitable string of text to prompt the user for a response. A concrete implementation must be
        provided by concrete child classes.
        :return: The prompt text, as string
        """
        raise NotImplementedError
        return None

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) is an abstract primitive operation to
        convert the raw text response from the user into an object of required type. A concrete implementaton must be provided
        by concrete child classes.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response converted to object of required type, Error message), as Tuple (object of required type, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (object of required type, '')
        """
        raise NotImplementedError
        return (None, 'some error message')

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) is an abstract primitive operation to
        validate that the processed response returned from _doProcessRawResponse(...) meets any additional requirements
        beyond being convertible to an object of the required type.
        :parameter processed_response: The returned object from _doProcessRawResponse(...), object of required type
        :return: Tuple (Is valid? True/False, Error message), as Tuple (boolean, string)
            Note: If Is Valid? = True, then Error message should be ''
        """
        raise NotImplementedError
        return (False, 'some error mesage')


class UserQueryCommandMenu(UserQueryCommand):
    """
    Following the Command design pattern, this is the ConcreteUserQueryCommand class that knows how to exeucte a menu command.
    Query the user via receiver to select from a menu of options.

    Methods:
        Execute(...) --- Returns the key of the value from the query dictionary that the user selected.
    """
    def __init__(self, receiver=None, query_preface = '', query_dic = {}):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        :parameter query_dic: Values are string descriptions of the user's options. Keys are the value the Client/Invoker are requesting.
        """
        UserQueryCommand.__init__(self, receiver, query_preface)
        self._query_dic = query_dic
    
    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user to select from a menu of options.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
       # Add to the prompt the menu options available to the user       
        prompt_text += 'Choose '
        for (key, value) in self._query_dic.items():
            prompt_text += '(' + str(key) + ')' + str(value) + ', '
        # Remove unneeded trailing ', '
        prompt_text = prompt_text[0:len(prompt_text)-2]
        prompt_text += ':  '
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into a key from self._query_dic.
        Since the key is always a string, this function processes the raw text response from the user into a string.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response, Error message), as Tuple (string, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (string, '')
        """
        # Process the response from the receiver/user into a string.
        # This is unlikely to ever fail, since (nearly?) every type in python at least as a default __str()...
        # implementation. 
        processed_response = None
        msg = ''
        try:
            processed_response = str(raw_response)
        except:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not a valid response. Please try again." 
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate that the processed response (string) returned from _doProcessRawResponse(...)
        is a valid key contained in self._query_dic.
        :parameter processed_response: The returned object from _doProcessRawResponse(...), string
        :return: Tuple (Is Valid? True/False, Error message), as Tuple (boolean, string)
            Note: If Is Valid? = True, then Error message should be ''
        """
        if processed_response not in self._query_dic:
            # User's input does not match a key in the menu dictionary, so craft an error message
            msg = f"\n\'{processed_response}\' is not a valid response. Please try again." 
            return (False, msg)
        return (True, '')


# Convenience function to query user to select a menu option without using objects.
def askForMenuSelection(query_preface = '', query_dic = {}):
    """
    This is a convenience fuction to query user to select a menu option without using objects.
    Returns the key of the value from query_dic that the user selected. User will be prompted with text:
        {query_preface argument}
        Choose (key1)value1, (key2)value2, ... :        

    :parameter query_preface: Text displayed to the user to request their response, string
    :parameter query_dic: Values are string descriptions of the user's options. Keys are the value the Client/Invoker are requesting.
        
    :return: key from query_dic   
    """
    # Build a query for the user to obtain their choice from a menu
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)    
    response = command.Execute()
    return response


class UserQueryCommandNumberInteger(UserQueryCommand):
    """
    Following the Command design pattern, this is the ConcreteUserQueryCommand class that knows how to exeucte a NumberInteger command.
    Query the user via receiver to provide an integer number within a specified range.

    Methods:
        Execute(...) --- Returns the integer value provided by the user.
    """
    def __init__(self, receiver=None, query_preface = '', minimum=None, maximum=None):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        :parameter minimum: The minimum valid entered integer response, int
            If None, then there is no minimum value.
        :parameter maximum: The maximum valid entered ingeger response, int
            If None, then there is no maximum value.
        """
        UserQueryCommand.__init__(self, receiver, query_preface)
        self._min_val = minimum
        self._max_val = maximum
        
    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user for an integer.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
        # Add to the prompt, asking the user to enter a number.       
        prompt_text += f"Enter an integer number between {self._min_val} and {self._max_val}:  "
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into an integer.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response converted to an integer, Error message), as Tuple (integer, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (integer, '')
        """
        # Process the response from the receiver/user into an integer
        processed_response = None
        msg = ''
        try: 
            processed_response = int(raw_response)
        except:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not an integer. Please try again."
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate that the processed response (integer) returned from _doProcessRawResponse(...)
        is within the required range.
        :parameter processed_response: The returned value from _doProcessRawResponse(...), integer
        :return: Tuple (In range? True/False, Error message), as Tuple (boolean, string)
            Note: If In range? = True, then Error message should be ''
        """
        # Check if the entered integer is within range, if the user has provided min and max values
        if self._min_val:
            if processed_response < self._min_val:
                # Craft error message
                msg = f"\n\'{processed_response}\' is less than {self._min_val}. Please try again."
                return (False, msg)
        if self._max_val:
            if processed_response > self._max_val:
                # Craft error message
                msg = f"\n\'{processed_response}\' is greater than {self._max_val}. Please try again."
                return (False, msg)
        return (True, '')

# Convenience function to query user for an integer number without using objects.
def askForInt(query_preface = '', minimum=None, maximum=None):
    """
    This is a convenience fuction to query user for an integer number without using objects.
    Returns the valid integer number that the user entered. User will be prompted with text:
        {query_preface argument}
        Enter an integer number between {minimum argument} and {maximum argument}:       

    :parameter query_preface: Text displayed to the user to request their response, string
    :parameter minimum: The minimum valid entered integer response, int
        If None, then there is no minimum value.
    :parameter maximum: The maximum valid entered ingeger response, int
        If None, then there is no maximum value.
        
    :return: The integer number entered by the user, int    
    """
    # Build a query for the user to obtain an integer value
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    command = UserQueryCommandNumberInteger(receiver, query_preface, minimum, maximum)    
    response = command.Execute()
    return response
    

class UserQueryCommandNumberFloat(UserQueryCommand):
    """
    Following the Command design pattern, this is the ConcreteUserQueryCommand class that knows how to exeucte a NumberFloat command.
    Query the user via receiver to provide an floating point number within a specified range.

    Methods:
        Execute(...) --- Returns the floating point value provided by the user.
    """
    def __init__(self, receiver=None, query_preface = '', minimum=None, maximum=None):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        :parameter minimum: The minimum valid entered floating point number response, float
            If None, then there is no minimum value.
        :parameter maximum: The maximum valid entered floating point number response, float
            If None, then there is no maximum value.
        """
        UserQueryCommand.__init__(self, receiver, query_preface)
        self._min_val = minimum
        self._max_val = maximum

    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user for a floating point number.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
        # Add to the prompt, asking the user to enter a number.       
        prompt_text += f"Enter a floating point number between {self._min_val} and {self._max_val}:  "
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into a floating point number.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response converted to a float, Error message), as Tuple (float, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (float, '')
        """
        # Process the response from the receiver/user into a float
        processed_response = None
        msg = ''
        try: 
            processed_response = float(raw_response)
        except:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not a floating point number. Please try again."
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate that the processed response (float) returned from _doProcessRawResponse(...)
        is within the required range.
        :parameter processed_response: The returned value from _doProcessRawResponse(...), float
        :return: Tuple (In range? True/False, Error message), as Tuple (boolean, string)
            Note: If In range? = True, then Error message should be ''
        """
        # Check if the entered float is within range, if the user has provided min and max values
        if self._min_val:
            if processed_response < self._min_val:
                # Craft error message
                msg = f"\n\'{processed_response}\' is less than {self._min_val}. Please try again."
                return (False, msg)
        if self._max_val:
            if processed_response > self._max_val:
                # Craft error message
                msg = f"\n\'{processed_response}\' is greater than {self._max_val}. Please try again."
                return (False, msg)
        return (True, '')


# Convenience function to query user for a floating point value without using objects.
def askForFloat(query_preface = '', minimum=None, maximum=None):
    """
    This is a convenience fuction to query user for a floating point value without using objects.
    Returns the valid floating point number that the user entered. User will be prompted with text:
        {query_preface argument}
        Enter a floating point number between {minimum argument} and {maximum argument}:       

    :parameter query_preface: Text displayed to the user to request their response, string
    :parameter minimum: The minimum valid entered floating point response, float
        If None, then there is no minimum value.
    :parameter maximum: The maximum valid entered floating point response, float
        If None, then there is no maximum value.
        
    :return: The floating point number entered by the user, float    
    """
    # Build a query for the user to obtain a floating point value
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    command = UserQueryCommandNumberFloat(receiver, query_preface, minimum, maximum)    
    response = command.Execute()
    return response


class UserQueryCommandStr(UserQueryCommand):
    """
    Following the Command design pattern, this is the ConcreteUserQueryCommand class that knows how to exeucte a Str command.
    Query the user via receiver to provide a string.

    Methods:
        Execute(...) --- Returns the valid string provided by the user.
    """
    def __init__(self, receiver=None, query_preface = '', max_length = 25):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        :parameter max_length: The maximum valid entered string length, int
        """
        UserQueryCommand.__init__(self, receiver, query_preface)
        self._max_len = max_length
    
    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user for a string of valid length.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
        # Add to the prompt, asking the user to enter a string no longer than a certain number of characters      
        prompt_text += f"Enter a string of text no longer than {self._max_len} characters:  "
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into a string.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response converted to a string, Error message), as Tuple (float, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (string, '')
        """
        # Process the response from the receiver/user into a string.
        # This is unlikely to ever fail, since (nearly?) every type in python at least as a default __str()...
        # implementation. 
        processed_response = None
        msg = ''
        try: 
            processed_response = str(raw_response)
        except:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not a valid string of text. Please try again." 
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate that the processed response (string) returned from _doProcessRawResponse(...)
        is of the required length.
        :parameter processed_response: The returned value from _doProcessRawResponse(...), string
        :return: Tuple (Is of valid length? True/False, Error message), as Tuple (boolean, string)
            Note: If Is of valid length? = True, then Error message should be ''
        """
        # Check if the entered float is within range, if the user has provided min and max values
        if self._max_len:
            if len(processed_response) > self._max_len:
                # Craft error message
                msg = f"\n\'{processed_response}\' is longer than {self._max_len} characters. Please try again."
                return (False, msg)
        return (True, '')        


# Convenience function to query user for a text string without using objects.
def askForStr(query_preface = '', max_length=25):
    """
    This is a convenience fuction to query user for a text string without using objects.
    Returns the valid length text string that the user entered. User will be prompted with text:
        {query_preface argument}
        Enter a string of text no longer than {max_length argument} characters.      

    :parameter query_preface: Text displayed to the user to request their response, string
    :parameter max_length: The maximum valid entered string length, int
        If None, then there is no maximum length. Default is 25.
        
    :return: The text string entered by the user, str    
    """
    # Build a query for the user to obtain a text string
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    command = UserQueryCommandStr(receiver, query_preface, max_length=max_length)    
    response = command.Execute()
    return response


class UserQueryCommandPathSave(UserQueryCommand):
    """
    Following the Command design pattern, this is the ConcreteUserQueryCommand class that knows how to exeucte a PathSave command.
    Query the user via receiver to provide a file path.

    Methods:
        Execute(...) --- Returns the valid file path provided by the user.
    """
    def __init__(self, receiver=None, query_preface = ''):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        """
        UserQueryCommand.__init__(self, receiver, query_preface)
    
    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user for a path to a new or existing file.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
        # Add to the prompt, telling the user how to handle directory separaters     
        prompt_text += 'Enter a valid file system path, without file extension, and with escaped backslashes:  '
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into a Path object.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response converted to a Path object, Error message), as Tuple (Path, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (Path, '')
        """
        # Process the response from the receiver/user into a Path object
        processed_response = None
        msg = ''
        try: 
            processed_response = Path(raw_response)
        except OSError:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not a valid file path. Please try again." 
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate the processed response (Path) returned from _doProcessRawResponse(...).
        Validation consists of determining that the Path is not to an already existing file, or if it is, then
        confirming that the user wishes to overwrite it.
        :parameter processed_response: The returned value from _doProcessRawResponse(...), Path object
        :return: Tuple (New or overwrite? True/False, Error message), as Tuple (boolean, string)
            Note: If New or overwrite? = True or False, then Error message should be ''
        """
        new_or_overwrite = True
        msg = ''
        # Check if the receiver / user has provided the path to an existing file. If so, confirm that they wish to overwrite it.
        if processed_response.exists():
            query_preface = f"\n\'{processed_response}\' is an existing file. Do you want to overwrite it?"
            query_dic = {'y':'Yes', 'n':'No'}
            command = UserQueryCommandMenu(self._receiver, query_preface, query_dic)
            overwrite_response = command.Execute()
            match overwrite_response:
                case 'n':
                    new_or_overwrite = False
                    msg = 'Please enter a path to a new file or file that you wish to overwrite.'
        return (new_or_overwrite, msg)

 
# Convenience function to query user for a path to save a file without using objects.
def askForPathSave(query_preface = ''):
    """
    This is a convenience fuction to query user for a path to save a file without using objects.
    Returns the valid file path that the user entered. User will be prompted with text:
        {query_preface argument}
        Enter a valid file system path, without file extension, and with escaped backslashes.      

    If the path provided already exists, the user will be asked to confirm they want to overwrite it. If not,
    then they will be prompted to enter a new path.

    :parameter query_preface: Text displayed to the user to request their response, string
        
    :return: Valid file path, as Path object   
    """
    # Build a query for the user to obtain a file save path
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    command = UserQueryCommandPathSave(receiver, query_preface)    
    response = command.Execute()
    return response    


class UserQueryCommandPathOpen(UserQueryCommand):
    """
    Following the Command design pattern, this is the ConcreteUserQueryCommand class that knows how to exeucte a PathOpen command.
    Query the user via receiver to provide a file path.

    Methods:
        Execute(...) --- Returns the valid file path provided by the user.
    """
    def __init__(self, receiver=None, query_preface = ''):
        """
        :parameter receiver: The object that knows how to perform the operations associated with carrying out a command.
        :parameter query_preface: Text displayed to the user to request their response, string
        """
        UserQueryCommand.__init__(self, receiver, query_preface)

    def _doCreatePromptText(self):
        """
        Following the Template Method design pattern, _doCreatePromptText() implements the primitive operation to
        generate a suitable string of text to prompt the user for a path to an existing file.
        :return: The prompt text, as string
        """
        prompt_text = self._query_preface + '\n'
        # Add to the prompt, telling the user how to handle directory separaters     
        prompt_text += 'Enter a valid file system path, without file extension, and with escaped backslashes:  '
        return prompt_text

    def _doProcessRawResponse(self, raw_response=''):
        """
        Following the Template Method design pattern, _doProcessRawResponse(...) implements the
        primitive operation to convert the raw text response from the user into a Path object.
        :parameter raw_response: The text input provide by the user in response to the prompt, string
        :return: Tuple (Raw text response converted to a Path object, Error message), as Tuple (Path, string)
            Note: If conversion isn't possible, then return Tuple should be (None, 'some error message text').
                  If conversion is possible, then return Tuple should be (Path, '')
        """
        # Process the response from the receiver/user into a Path object
        processed_response = None
        msg = ''
        try: 
            processed_response = Path(raw_response)
        except OSError:
            # Craft error message
            msg = f"\n\'{raw_response}\' is not a valid file path. Please try again." 
        return (processed_response, msg)

    def _doValidateProcessedResponse(self, processed_response=None):
        """
        Following the Template Method design pattern, _doValidateProcessedResponse(...) implements the
        primitive operation to validate the processed response (Path) returned from _doProcessRawResponse(...).
        No Validation is required for this UserQueryCommand, so always return (True, '')
        :parameter processed_response: The returned value from _doProcessRawResponse(...), Path object
        :return: Tuple (True, ''), as Tuple (boolean, string)
        """
        return (True, '')
        

# Convenience function to query user for a path to open a file without using objects.
def askForPathOpen(query_preface = ''):
    """
    This is a convenience fuction to query user for a path to open a file without using objects.
    Returns the valid file path that the user entered. User will be prompted with text:
        {query_preface argument}
        Enter a valid file system path, without file extension, and with escaped backslashes.      

    :parameter query_preface: Text displayed to the user to request their response, string
        
    :return: Valid file path, as Path object   
    """
    # Build a query for the user to obtain a file open path
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    command = UserQueryCommandPathOpen(receiver, query_preface)    
    response = command.Execute()
    return response   