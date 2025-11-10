# Improve Prompt

A Python package for improving code prompts.

## Installation

```bash
pip install improve-prompt
```

## Usage

```python
import improve_prompt

# Get a file object
improve_file = improve_prompt.get("test.py")

# Improve the file
improve_file.improve()

# Save the file
improve_file.save(original_path=True)
```

## Features

- Simple API for improving code prompts
- Easy to use with minimal setup
- Compatible with Python 3.7+

## License

MIT License