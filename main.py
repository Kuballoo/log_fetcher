import addresses_generator, arg_parser


if __name__ == '__main__':
    args = arg_parser.ArgParser().generate_args_dict()
    addr = addresses_generator.AddressesGenerator(args["ipv4_addr"]).run()