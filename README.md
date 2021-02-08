# Klippa-client

## Description

A Python client to parse files and receive/save json from the Klippa OCR API.

### Installation

This project requires Python 3.8+ to run.
Install the necessary Python dependencies:

```sh
$ cd klippa-client/
$ pip install -r requirements.txt
```

## Quickstart

The easiest way to get going is to use the CLI to send a file or directory as the example below:

```sh
$ python klippa-client.py --key <your_api_key> --file <filepath> --template <preferred_template> --save
```

As an example to parse a file named "numbers.pdf" that you put in the same directory as klippa-client you could use this command(be sure to use your own API key!):

```sh
$ python klippa-client.py --key abcdefg1234567 --file numbers.pdf --template financial_full --save
```

The --save flag ensures the JSON output from the Klippa OCR API will be saved in a newly made directory namely: 
**klippa-client/output**

## Config

An easy way to globally set your API key, preferred template and text extraction options for .pdf files is to make your
very own **Klippa Config File(.kcf)** in the **klippa-client/config** directory.

To make things easy, an empty .kcf file will be generated on first run without passing the --key option.

A standard .kcf file looks like this:
```sh
API_KEY=abcdefghijklmnopqrstuvwxyz0123456789
TEMPLATE=financial_full
TEXT_EXTRACTION=full
```

Valid configuration options include:
```
API_KEY=[apikey[a-zA-Z0-9]]
TEMPLATE=[financial_full]
TEXT_EXTRACTION=[fast/full]
```

When your .kcf file is setup correctly you don't have to pass those arguments to the client anymore.
A simple:
```sh
$ python klippa-client.py --watch <directory>
```
Will be enough to get things rolling after that!

## Examples

### Files
To send a file:

```sh
$ python klippa-client.py --key <your_api_key> --file <filepath> 
```
Literal example:
```sh
$ python klippa-client.py --key abcdefg1234567 --file big-numbers.pdf
```
### Directories
To send a directory of files:

```sh
$ python klippa-client.py --key <your_api_key> --dir <directorypath> 
```
Literal example:
```sh
$ python klippa-client.py --key abcdefg1234567 --dir /etc/files/
```

To watch/monitor a directory for new or changed files to be automatically picked up and parsed:
```sh
$ python klippa-client.py --key <your_api_key> --watch <directorypath> 
```
Literal example:
```sh
$ python klippa-client.py --key abcdefg1234567 --watch /etc/files
```


### Support

For all your client troubles, feel free to submit a bug report to: huurmanfrank@gmail.com