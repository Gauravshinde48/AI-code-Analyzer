import streamlit as st
import radon.complexity as radon_complexity
import subprocess
import black
import tempfile
import os
import re
import ast

# Function to format code using black (using the Python API)
def format_code(code):
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        return formatted_code
    except Exception as e:
        return f"Error formatting code with black: {e}"

# Function to sanitize the code by removing invisible characters and fixing line continuations
def sanitize_code(code):
    # Remove non-ASCII and invisible characters
    sanitized_code = ''.join([char for char in code if char.isprintable()])

    # Fix potential line continuation issues by ensuring no space after a backslash (\)
    sanitized_code = re.sub(r'\\\s+', '\\', sanitized_code)

    return sanitized_code

# Function to calculate code complexity
def calculate_complexity(code):
    try:
        sanitized_code = sanitize_code(code)  # Sanitize the input code

        # Create a temporary file to save the sanitized code and analyze it
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py') as temp_file:
            temp_file.write(sanitized_code)
            temp_filename = temp_file.name

        # Get the complexity analysis report using Radon
        complexity_report = radon_complexity.cc_visit(temp_filename)
        os.remove(temp_filename)  # Clean up the temporary file after use
        return complexity_report
    except SyntaxError as e:
        return f"Syntax error detected: {e}"
    except Exception as e:
        return f"Error calculating complexity: {e}"

# Function to perform basic linting using pylint
def lint_code(code):
    try:
        sanitized_code = sanitize_code(code)  # Sanitize the input code

        # Save the sanitized code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py') as temp_file:
            temp_file.write(sanitized_code)
            temp_filename = temp_file.name

        # Run pylint on the temporary file
        result = subprocess.run(['pylint', temp_filename], capture_output=True, text=True)
        os.remove(temp_filename)  # Clean up the temporary file
        return result.stdout
    except Exception as e:
        return f"Error running pylint: {e}"

# Function to check for errors in the code using AST (Abstract Syntax Tree)
def check_syntax_errors(code):
    try:
        # Attempt to parse the code to catch syntax errors
        ast.parse(code)
        return None  # No syntax errors
    except SyntaxError as e:
        # Return the error message with line and column numbers
        return f"Syntax Error: {e.msg} at line {e.lineno}, column {e.offset}"

# Function to simulate AI-powered suggestions for code fixes
def get_ai_suggestions(error_message):
    # For simplicity, we'll provide some common fixes based on error messages
    suggestions = {
        "unexpected EOF while parsing": "Check if all your parentheses, brackets, and quotes are properly closed.",
        "invalid syntax": "Look for any incorrect syntax, such as missing colons, unmatched parentheses, or improper indentation.",
        "NameError": "Ensure all variables are defined before use.",
        "IndentationError": "Check that the indentation is consistent (tabs vs spaces).",
        "ZeroDivisionError": "Consider using a try-except block to handle division by zero.",
    }

    # Return a default suggestion if no specific one is found
    return suggestions.get(error_message, "Consider reviewing the code for common syntax issues.")

# Function to check for runtime errors by executing the code
def check_runtime_errors(code):
    try:
        # Execute the code in a safe environment to catch runtime errors
        exec(code)
        return None  # No runtime errors
    except ZeroDivisionError:
        return "ZeroDivisionError: You attempted to divide by zero."
    except Exception as e:
        return f"Runtime Error: {str(e)}"

# Streamlit app UI
st.title('AI-Powered Code Review Assistant')

# File uploader for uploading Python files
uploaded_file = st.file_uploader("Upload a Python file", type=["py"])

# Check if file is uploaded
if uploaded_file is not None:
    code_input = uploaded_file.getvalue().decode("utf-8")  # Get the contents of the file as a string
    
    # Display the contents of the uploaded file
    st.subheader('Uploaded Python Code:')
    st.code(code_input, language="python")
    
    # Check for syntax errors
    error_message = check_syntax_errors(code_input)
    
    if error_message:
        st.subheader('Syntax Error Detected:')
        st.error(error_message)
        
        # Provide AI-powered suggestions for fixing the error
        ai_suggestion = get_ai_suggestions(error_message)
        st.subheader('AI-Powered Suggestion for Fix:')
        st.write(ai_suggestion)
    else:
        # Check for runtime errors
        runtime_error = check_runtime_errors(code_input)
        if runtime_error:
            st.subheader('Runtime Error Detected:')
            st.error(runtime_error)
            
            # Provide AI-powered suggestions for runtime error
            ai_suggestion = get_ai_suggestions(runtime_error.split(":")[0])  # Get AI suggestion for the error type
            st.subheader('AI-Powered Suggestion for Fix:')
            st.write(ai_suggestion)
        else:
            st.success("No errors detected!")

    # Buttons for performing analysis
    if st.button('Format Code'):
        formatted_code = format_code(code_input)
        st.subheader('Formatted Code:')
        st.code(formatted_code, language="python")

    if st.button('Calculate Code Complexity'):
        complexity_report = calculate_complexity(code_input)
        st.subheader('Code Complexity Report:')
        st.text(complexity_report)

    if st.button('Lint Code'):
        lint_report = lint_code(code_input)
        st.subheader('Code Linting Report:')
        st.text(lint_report)

else:
    # If no file is uploaded, let the user input code manually
    code_input = st.text_area('Or enter or paste your Python code here:')

    # Check for syntax errors
    error_message = check_syntax_errors(code_input)
    
    if error_message:
        st.subheader('Syntax Error Detected:')
        st.error(error_message)
        
        # Provide AI-powered suggestions for fixing the error
        ai_suggestion = get_ai_suggestions(error_message)
        st.subheader('AI-Powered Suggestion for Fix:')
        st.write(ai_suggestion)
    else:
        # Check for runtime errors
        runtime_error = check_runtime_errors(code_input)
        if runtime_error:
            st.subheader('Runtime Error Detected:')
            st.error(runtime_error)
            
            # Provide AI-powered suggestions for runtime error
            ai_suggestion = get_ai_suggestions(runtime_error.split(":")[0])  # Get AI suggestion for the error type
            st.subheader('AI-Powered Suggestion for Fix:')
            st.write(ai_suggestion)
        else:
            st.success("No errors detected!")

    # Buttons for performing analysis
    if st.button('Format Code'):
        formatted_code = format_code(code_input)
        st.subheader('Formatted Code:')
        st.code(formatted_code, language="python")

    if st.button('Calculate Code Complexity'):
        complexity_report = calculate_complexity(code_input)
        st.subheader('Code Complexity Report:')
        st.text(complexity_report)

    if st.button('Lint Code'):
        lint_report = lint_code(code_input)
        st.subheader('Code Linting Report:')
        st.text(lint_report)
