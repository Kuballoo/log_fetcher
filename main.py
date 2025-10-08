import CONFIG
import addresses_generator, arg_parser, log_fetcher, compressor


if __name__ == '__main__':
    args = arg_parser.ArgParser().generate_args_dict()
    CONFIG.THREADS_COUNT = args["threads"]
    
    addr = addresses_generator.AddressesGenerator(args["ipv4_addr"]).run_generator()
    fetcher = log_fetcher.LogFetcher(addr, args["input"], args["output"], args["log-types"])
    fetcher.run_fetcher()
    compressor.Compressor(args["output"]).run_compressor()
    