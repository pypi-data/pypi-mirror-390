"""
shuffle(numbers, input_file, output_file, language, prompt)
read_file(input_file, output_file, lang, prompt)
save_file(input_file, output_file, make_short = True)
save_self(input_string, make_short = True)
"""


import g4f
from random import shuffle as shuf

def shuffle(n, i_f = "target.txt", output = "output.txt", lang = "python", p = f"Just write a solution for this problem in #LANG. Do not include any explanation or comments. Only provide the code.\n\n"):
    with open(i_f, "r") as f:
        prompt = f.read()

    p = p.replace("#LANG", lang)

    prompt += "\n\n" + p
    response = g4f.ChatCompletion.create(
        g4f.models.gpt_4,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that shuffles a list of numbers."},
            {"role": "user", "content": prompt}
        ],
    )
    with open(output, "w") as f:
        f.write(response)

    shuf(n)


def read_file(i_f = "target.txt", output = "output.txt", lang = "python", p = f"Just write a solution for this problem in #LANG. Do not include any explanation or comments. Only provide the code.\n\n"):
    with open(i_f, "r") as f:
        prompt = f.read()

    p = p.replace("#LANG", lang)

    prompt += "\n\n" + p
    response = g4f.ChatCompletion.create(
        g4f.models.gpt_4,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that shuffles a list of numbers."},
            {"role": "user", "content": prompt}
        ],
    )
    with open(output, "w") as f:
        f.write(response)


def save_file(i, o, make_short = True):
    with open(i, "r") as f:
        prompt = f.read()

    if make_short:
        prompt += "Just give me an exact, short answer. Do not include any explanation or comments. Only provide the answer.\n\n"

    response = g4f.ChatCompletion.create(
        g4f.models.gpt_4,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides answers based on the given input."},
            {"role": "user", "content": prompt}
        ],
    )
    with open(o, "w") as f:
        f.write(response)

def save_self(i, make_short = True):
    if make_short:
        i += "Just give me an exact, short answer. Do not include any explanation or comments. Only provide the answer.\n\n"
    response = g4f.ChatCompletion.create(
        g4f.models.gpt_4,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides answers based on the given input."},
            {"role": "user", "content": i}
        ],
    )
    return response
