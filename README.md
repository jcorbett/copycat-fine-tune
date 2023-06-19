# CopycatAI 😼
##Fine-tune an OpenAI model based on your favorite Medium blogger in two easy steps.

Copycat provides an effortless way to fine-tune OpenAI models using Medium posts. This project automates the process of collecting, cleaning, prompt-completion pair generation, and training, making it easier to refine AI models for specific writing tasks.

## Features

- Automatically get links to medium posts written by the author
- Generate prompt-completion pairs from blog posts
- Fine-tune OpenAI models based on generated prompt-completion pairs

## Installation

### Prerequisites

- Python 3.9 or later
- BYOK 🔑 (bring your own keys- OpenAI API key)

### Steps

### Automatic Installation on Linux
1. Install the dependencies:
```bash
$ git clone https://github.com/jcorbett/copycatAI.git
```
2. Navigate to the project directory `cd copycatAI`.
3. Install python dependencies (you should use a virtual env):
```bash
$ pip install -r requirements.txt
```
4. Add your OPENAI_API_KEY to the environment:
```bash
$ echo "OPENAI_API_KEY=sk-your-api-key" > .env
```


## Usage

### Generate prompt-pairs
```bash
$ python ./train.py [medium_username] [output_directory] [style|subject] [linear|chatgpt]
```

**medium_username**: this it he username of the author you'd like to train a model on. Make sure this is on someone that has posts on Medium that aren't "member-only". (this could be solved with the current selenium implementation, but I haven't worried about it yet)

**output_directory**: this is the directory where the fine-tuned model will be saved. If the directory doesn't exist, it will be created.

**style|subject**: This is used to generate the prompt-completion pairs and is either the `style` or `subject` of the author you're training on. This is used to generate the prompt-completion pairs. For example, if you're training on `style`, it will use the OpenAI-recommended blank prompt (`prompt=""`). If you are choosing `subject`, it will use the next parameter to generate the prompt pair based on what the author is writing about.

**linear|chatgpt**: This is used to generate the prompt-completion pairs and is either `linear` or `chatgpt`. For example, if you're training on `linear`, it will use the next sentence as the completion (`completion:[next sentence]`) with the current sentence as the prompt (`prompt=[current sentence]`). If you are choosing `chatgpt`, it will ask chatgpt to generate prompts that would generate the current sentence as a completion. ***This will default to `linear` if not specified.***

**NOTE**: This is only necessary when using `subject` as the 3rd parameter. Also, `chatgpt` is much slower than `linear` and can be expensive.

example:
```bash
$ python ./train.py MarcoAngeloBendigo .output style 
$ python ./train.py cryptohayes .output subject linear
```

***WARNING*** - generating prompt pairs based on `subject` with `chatgpt` from several long medium articles can take a long time and can be ***expensive***. 

### Prep fine-tuning file
```bash
openai tools fine_tunes.prepare_data -f [directory]/[medium_username].jsonl
```
example:
```bash
openai tools fine_tunes.prepare_data -f .output/cryptohayes.jsonl
```

### Launch fine-tuning
```bash
openai api fine_tunes.create -t [directory]/[medium_username}_prepared.jsonl -m [model] --suffix [something to help track name]
```
example
```bash
openai api fine_tunes.create -t .output/cryptohayes_prepared.jsonl -m davinci --suffix "cryptohayes"
```

## Best Practices

While you can run the fine-tuning process automatically, make sure to check each jsonl file to ensure clean prompt pairs. The quality of your fine-tuning is fully dependent on the quality of your data.

Fine-tune best practices can be found here:
https://platform.openai.com/docs/guides/fine-tuning


### Share what you build with me on Twitter [@_ustin](https://twitter.com/_ustin) 👋


## License

This project is licensed under the MIT License - see the LICENSE.md file for details.