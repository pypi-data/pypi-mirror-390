import argparse
import asyncio
import logging
from .generator import generate

from .validator import validate
from .generator import generate

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        "nwcicdsetup", description="Tools for the cicd workflow to generate and validate circleci .yml files")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    gen_parser = subparsers.add_parser(
        "generate", help="Parses all cicd.yml files from working directory and saves the final circleci config to --out")

    gen_parser.add_argument(
        "-o", "--out", type=str, required=True, help="File to write the .yml configuration to")
    gen_parser.add_argument(
        "-gc", "--general_config", required=True, type=str, help="Path to the config file describing basic functionality")
    gen_parser.add_argument(
        "-gd", "--global_dependencies", nargs="+", default=[], type=str, help="Global dependencies which force job execution if changed")
    gen_parser.add_argument(
        "-wd", "--working-dir", default="/home/circleci/project", type=str, help="Global working directory where code is checked into")
    gen_parser.add_argument("--fake-deploy", action="store_true",
                            help="Replace the deploy commands with an echo output")
    gen_parser.add_argument("--force", action="store_true",
                            help="Force full rebuild & deploy by executing all tasks")
    gen_parser.add_argument("--dummy_env", action="store_true",
                            help="Fills CircleCI environment variables with dummy data")
    gen_parser.add_argument("-p", "--pipeline", required=True, type=int,
                            help="Pipeline number to find successful build from")
    gen_parser.add_argument("-r", "--resource-class", required=False, type=str, 
                            default="small", #see validationSchema=>resource_class
                            help="Default resource class used for all jobs.")
    gen_parser.add_argument(
        "-cm", "--checkout-method", choices=["full", "blobless"], default="full",
        help="Specify the checkout method to use. Options are 'full' or 'blobless'. Default is 'full'.")
    
    validate_parser = subparsers.add_parser(
        "validate", help="Validate cicd.yml files from the given working directory")
    validate_parser.add_argument(
        "-gc", "--general_config", type=str, help="Path to the config file describing basic functionality")

    args = parser.parse_args()

    if args.command == "generate":
        asyncio.get_event_loop().run_until_complete(generate(
            outfile=args.out,
            general_config_path= args.general_config,
            global_dependencies=args.global_dependencies,
            global_working_direcotry=args.working_dir,
            pipeline=args.pipeline,
            fake_deploy=args.fake_deploy,
            force=args.force,
            resource_class=args.resource_class,
            dummy_env=args.dummy_env,
            checkout_method=args.checkout_method
            ))
    elif args.command == "validate":
        asyncio.get_event_loop().run_until_complete(validate(args.general_config, args.pipeline))

