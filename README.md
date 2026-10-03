# extract-text

this project parses cli inputs and extract text from given paths,
currently supports pdf, pptx

also it can be used to extract key points from output directory

# usage

## cli install
```console
cd [project path]
pip install -e ./
```

## cli usage

extract-text [subcommand] [options] 

parse [-c] \
parse output directory and extract key points by AI, -c to input sysprompt by command line

read [-r] \
read from given paths, extract text from text files, -r to read from directories

after this, u can type { to start typing paths or prompt, } to end \
type , to separate parameters

The DeepSeek API integration is hard-coded, so only DeepSeek can be used. you will need the `DEEPSEEK_API_KEY` environment variable.

```console
$ {
$ path,
$ path,
$ path
$ }
```

# output

## path
outputs in current working directory 
cwd/output/