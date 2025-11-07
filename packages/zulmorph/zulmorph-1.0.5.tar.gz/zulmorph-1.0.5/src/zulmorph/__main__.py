import argparse
import sys
import json

from zulmorph.zulmorph import *

def main():

    parser = argparse.ArgumentParser(description='Uses ZulMorph to morphologically analyse isiZulu tokens.')

    parser.add_argument('input_type',choices=['t','f'],help='indicate if input is [t]oken(s) or [f]ilename(s) (token per line)')
    parser.add_argument('input', nargs='+')
    parser.add_argument('-f',dest='fst',help='path to FST (.fom) (default: zul.fom)')

    args = parser.parse_args()

    if args.fst:
        try:
            fst = load_fst(args.fst)
        except ValueError:
            print(f"Could not load .fom FST at {args.fst}",file=sys.stderr)
            sys.exit(1)
    else:
        fst = None
    
    if args.input_type == 'f':
        tokens = []
        files = args.input
        for file in files:
            with open(file) as f:
                f_tokens = [l.strip() for l in f.readlines() if len(l.strip()) > 0]
                tokens += f_tokens
    else:
        tokens = args.input
    
    analyses_dict = analyse_tokens(tokens,fst)

    print(json.dumps(analyses_dict,indent=2))

if __name__ == "__main__":
    main()