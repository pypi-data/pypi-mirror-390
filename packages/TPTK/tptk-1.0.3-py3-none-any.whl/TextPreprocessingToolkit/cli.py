import argparse
from .pipeline import PreprocessingPipeline
from .text_preprocessor import TextPreprocessor

def main():
    parser = argparse.ArgumentParser(prog='dataprepkit', description='Data preprocessing toolkit')
    subparsers = parser.add_subparsers(dest='command')

    preprocess = subparsers.add_parser('preprocess', help='Run preprocessing')
    preprocess.add_argument('--input', required=True, help='Input CSV path')
    preprocess.add_argument('--output', required=True, help='Output CSV path')
    preprocess.add_argument('--text', help='Text column name')
    preprocess.add_argument('--steps', nargs='+', default=['clean', 'tokenize', 'lemmatize'],
                           help='Text steps: clean, tokenize, stopwords, lemmatize, spell')
    preprocess.add_argument('--chunksize', type=int, default=10000)
    preprocess.add_argument('--config', help='Pipeline YAML/JSON config')

    args = parser.parse_args()

    if args.command == 'preprocess':
        if args.config:
            pipeline = PreprocessingPipeline(args.config)
            pipeline.fit_transform(args.input, args.output, args.chunksize)
        elif args.text:
            tp = TextPreprocessor()
            tp.process_csv(args.input, args.text, args.output, steps=args.steps, chunksize=args.chunksize)
        else:
            print("Use --config or --text")
            return

if __name__ == '__main__':
    main()