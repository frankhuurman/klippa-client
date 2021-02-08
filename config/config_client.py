import argparse
import os
import sys

class ConfigClient:

    '''CLI options and global config (config/.kcf) parser'''

    #######################################################

    ### Constants ###

    # global config vars
    API_KEY_ENVIRONMENT_VAR = "KLIPPA_API_KEY"
    KLIPPA_CONFIG_FILE = "config/.kcf"

    # .kcf file format validation
    KCF_FIELDS = {"API_KEY", "TEMPLATE", "TEXT_EXTRACTION"}
    TEMPLATE_CHOICES = {"financial_full"}
    TEXT_EXTRACTION_CHOICES = {"fast", "full"}

    # debug messages
    KCF_FORMAT_DEBUG_MSG = "The .kcf file is improperly formatted.\n" \
    "Please provide a .kcf file as specified in the README.md."

    KCF_VALUES_DEBUG_MSG = "The .kcf file doesn't seem to have the " \
    "expected keys or values.\nPlease take a look at the README.md."

    UNSUPPORTED_FILE_TYPE_MSG = "One or more files given as argument " \
    "are not supported file types by the Klippa-Client."

    # file validation
    VALID_FILE_TYPES = {"gif", "heic", "heif", "jpg", "pdf", "png"}

    #######################################################

    def file_and_dir_check(self, args):
        if not args.file and not args.dir:
            if not args.watch:
                print("Please provide a file or directory to parse")
                sys.exit(0)
        if args.file and args.dir:
            print("Please provide either a file ór a directory")
            sys.exit(0)
        if args.watch:
            return args, "watch"
        else:
            return args, "file"

    def validate_choices(self, value, choices):

        if value in choices:
            return True
        else:
            print(self.KCF_FORMAT_DEBUG_MSG)
            raise NameError(f"'{value}' is not an accepted value\n")

    def validate_kcf(self, args):

        valid = False
        kcf_file = self.load(self.KLIPPA_CONFIG_FILE)

        if (kcf_file and 
            all(key in self.KCF_FIELDS for key in kcf_file.keys())):

                kcf_len, fields_len = len(kcf_file), len(self.KCF_FIELDS)

                if kcf_len == fields_len and kcf_file["API_KEY"] != "":
                    template = kcf_file["TEMPLATE"]
                    text = kcf_file["TEXT_EXTRACTION"]

                    template_valid = self.validate_choices(template, 
                            self.TEMPLATE_CHOICES)
                    text_valid = self.validate_choices(text, 
                            self.TEXT_EXTRACTION_CHOICES)

                    if template_valid and text_valid:
                        valid = True
        if valid:
            args.key = kcf_file["API_KEY"]
            if not args.template:
                args.template = kcf_file["TEMPLATE"]
            if not args.text:
                args.text = kcf_file["TEXT_EXTRACTION"]

            return args
        else:
            print(self.KCF_VALUES_DEBUG_MSG)
            sys.exit(0)


    def get_env_var(self):

        # Not implemented yet, could be added in the future
        api_key = os.environ.get(API_KEY_ENVIRONMENT_VAR)

        if api_key:
            return api_key

    def get_args(self):

        # Add CLI options
        argparser = argparse.ArgumentParser()

        argparser.add_argument(
            "--dir",
            help="The directory with files to be parsed by the API",
            metavar="<directory>"
        )

        argparser.add_argument(
            "--file", 
            help="The (single) file to be parsed by the API",
            metavar="<file>"
        )

        argparser.add_argument(
            "--key",
            help="The API key to be used for the request",
            metavar="<key>"
        )

        argparser.add_argument(
            "--save",
            help="Save the parsed output in klippa-client/output",
            action="store_true"
        )

        argparser.add_argument(
            "--template",
            help="The template option to use with a .pdf file",
            metavar="<value>"
        )

        argparser.add_argument(
            "--test",
            help="Test flag for new Klippa-Client functionality",
            action="store_true"
        )

        argparser.add_argument(
            "--text",
            help="The text extraction option to use with a .pdf file",
            metavar="<value>"
        )

        argparser.add_argument(
            "--watch",
            help="Monitor a directory for newly added files to parse",
            metavar="<directory>"
        )

        args = argparser.parse_args()

        if len(sys.argv) <= 1:

            # Show help and exit if no CLI arguments are given
            argparser.print_help()
            sys.exit(0)

        if args.test:
            # Test flag for new functionality
            return args, "test"

        if not args.key:

            # Need an API key for every action so let's find it
            if kcf_config := self.validate_kcf(args):

                # API key is now set by .kcf configuration
                final_args, extra_args = self.file_and_dir_check(args)
                # extra_args is "file" or "watch" after file_and_dir_check
                return final_args, extra_args
            else:
                print("API key not given with --key or set in config/.kcf")
                sys.exit(0)
        else:
            # Key is sent as CLI argument
            final_args, extra_args = self.file_and_dir_check(args)
            # extra_args is "file" or "watch" after file_and_dir_check
            return final_args, extra_args
        
    def load(self, file):

         # Extracts key=value pairs from a .kcf file
        file_extracted = {}

        if os.path.exists(file) and os.path.isfile(file):
            with open(file, "r") as config_file:
                for line in config_file:
                    key, value = line.partition("=")[::2]
                    file_extracted[key.strip()] = value.strip()
        else:
            self.generate_empty_kcf()
            raise FileNotFoundError(
                "Missing .kcf file, one has been created at config/.kcf"
            )

        return file_extracted

    def generate_empty_kcf(self):
        if os.path.exists("config"):
            if not os.path.exists(self.KLIPPA_CONFIG_FILE):
                with open(self.KLIPPA_CONFIG_FILE, "w") as config_file:
                    for field in sorted(self.KCF_FIELDS):
                        config_file.write(field + "=\n")