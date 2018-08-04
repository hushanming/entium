from .converter import convert_tiles, convert_hierarchy
from argparse import ArgumentParser, ArgumentTypeError, Action
from enum import Enum
import json
import os

def main():
  parser = ArgumentParser(description='Convert the entwine hierarchy to a cesium tileset')

  class FullPaths(Action):
    def __call__(self, parser, namespace, values, option_string=None):
      setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

  def is_dir(dirname):
    if not os.path.isdir(dirname):
      msg = '{0} is not a directory'.format(dirname)
      raise ArgumentTypeError(msg)
    else:
      return dirname

  def is_json(filename):
    if filename is not None and not os.path.isfile(filename):
      raise ArgumentTypeError('{0} is not a file'.format(filename))
    if not os.path.splitext(filename)[1] == '.json':
      raise ArgumentTypeError('{0} is not a json file'.format(filename))

    return filename
  
  def asciify(accum, x):
    if isinstance(x[1], list):
      remapped = map(lambda y: y.encode('ascii', 'ignore'), x[1])
    else:
      remapped = x[1].encode('ascii', 'ignore')
    accum[x[0].encode('ascii', 'ignore')] = remapped
    return accum
  
  parser.add_argument('mode', choices=['tileset', 'tile', 'both'])
  parser.add_argument('entwine_dir', action=FullPaths, type=is_dir, help='input folder for entwine')
  parser.add_argument('output_dir', action=FullPaths, type=is_dir, help='output folder for the cesium tilests')
  parser.add_argument('-p', '--precision', nargs='?', type=float, default=0.01, help='precision in meters required to use quantized tiles')
  parser.add_argument('-c', '--config', action=FullPaths, nargs='?', type=is_json, help='filepath to config file to use advanced features')
  parser.add_argument('--validate', action='store_true', help='run post-process to validate point precision')

  args = parser.parse_args()

  groups, batched = None, None
  if args.config is not None:
    try:
      with open(args.config, 'r') as config_file:
        config = json.load(config_file)['cesium']

        if config is None:
          raise Exception('cesium is not defined!')

        if 'groups' in config:
          groups = reduce(asciify, config['groups'].iteritems(), {})

        if 'batched' in config:
          batched = map(lambda y: y.encode('ascii', 'ignore'), config['batched'])
    except Exception as e:
      print(e)
      print('Unable to parse config!')

  # TODO - Multithread
  if args.mode == 'both' or args.mode == 'tile':
    print('Converting tiles...')
    convert_tiles(args.entwine_dir, args.output_dir, args.precision, args.validate, groups, batched)

  if args.mode == 'both' or args.mode == 'tileset':
    print('Generating tileset hierarchy...')
    convert_hierarchy(args.entwine_dir, args.output_dir)

if __name__ == '__main__':
  main()