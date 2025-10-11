import CONFIG
import addresses_generator, arg_parser, log_fetcher, compressor


if __name__ == '__main__':
    args = arg_parser.ArgParser().generate_args_dict()
    CONFIG.THREADS_COUNT = args["threads"]
    
    print("[+] Generating addresses...")
    addr = addresses_generator.AddressesGenerator(args["ipv4_addr"]).run_generator()

    print("[+] Fetching logs...")
    fetcher = log_fetcher.LogFetcher(addr, args["input"], args["output"], args["log-types"])
    fetcher.run_fetcher()

    if args["compress"]:
        print("[+] Compressing logs...")
        compressor.Compressor(args["output"]).run_compressor()

    print("[+] Everything is fine :)")