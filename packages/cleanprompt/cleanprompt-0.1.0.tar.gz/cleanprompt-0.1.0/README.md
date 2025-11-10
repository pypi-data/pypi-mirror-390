[![pytest](https://github.com/salarian/cleanprompt/actions/workflows/pytest.yml/badge.svg)](https://github.com/salarian/cleanprompt/actions/workflows/pytest.yml) [![pre-commit](https://github.com/salarian/cleanprompt/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/salarian/cleanprompt/actions/workflows/pre-commit.yml)

# CleanPrompt
A simple yet frequently used Python utility for safely dedenting and stripping whitespace from LLM prompt strings.

## The problem
When building prompts within Python code, multi-line strings (`"""..."""`) are convenient, but they introduce unwanted leading indentation and newlines that can interfere with model tokenization. A naive `textwrap.dedent(s).strip()` works for most simple prompts. However, typing `textwrap.dedent(s).strip()` gets repetitive quite fast. Many developers wrap it in a single function somewhere in their code. Wouldn't it be nice to have this simple function tucked in a small package and use it everywhere? This is what `CleanPrompt` is trying to achieve.

Once we have the familiar `textwrap.dedent(s).strip()` wrapped in a function, in a package, other concerns start to appear: it fails for more complex cases! For example in few-shot prompts, trailing space (e.g., `A: `) is a critical cue for the model.

`CleanPrompt` solves this by providing a set of simple, safe functions to intelligently dedent and strip whitespace, giving you full control over whether to strip leading, trailing, both, or no whitespace at all.

## Installation
```bash
pip install cleanprompt
```

## Usage and Examples
The package provides one main function, `clean()`, and three convenient aliases for common use cases.

---
### Example 1: Standard Prompt Cleaning (Default)

For most self-contained prompts, you want to remove all code indentation and any surrounding blank lines. The default cleanup_prompt handles this perfectly.

```Python
import cleanprompt as cp

raw_prompt = """

    You are a helpful assistant.
    Please summarize the following text:

    ...text...

"""

clean = cp.clean(raw_prompt)

# Result:
# "You are a helpful assistant.\nPlease summarize the following text:\n\n...text..."
```

---

### Example 2: Preserving Trailing Spaces for Few-Shot Cues
This is the critical use case. For few-shot prompts, you **must** preserve the trailing space after the final "cue" (e.g., `A: `) to guide the model.

Here, we use `clean_leading` to only strip whitespace from the beginning of the string, leaving the important trailing space untouched.

```Python
import cleanprompt as cp

raw_few_shot = """
    Q: What is 2+2?
    A: 4

    Q: What is the capital of France?
    A: Paris

    Q: Who was the first US president?
    A: """

clean = cp.clean_leading(raw_few_shot)

# The clean string correctly ends with "A: "
assert clean.endswith("A: ")

# Result:
# "Q: What is 2+2?\nA: 4\n\nQ: What is the capital of France?\nA: Paris\n\nQ: Who was the first US president?\nA: "
```

# License

Distributed under the terms of the [MIT license](https://opensource.org/license/MIT).
