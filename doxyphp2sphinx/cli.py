import xml.etree.ElementTree as ET
import argparse

from .logger import FilteredLogger
from .rstgenerator import RstGenerator

class Cli:
    @staticmethod
    def run():
        parser = argparse.ArgumentParser(prog="doxyphp2sphinx", description='Generate Sphinx-ready reStructuredText documentation or your PHP project, using Doxygen XML as an input.')
        parser.add_argument('--xml-dir', dest='xml_dir', default='xml', help='directory to read from')
        parser.add_argument('--out-dir', dest='out_dir', default='.', help='directory to write to')
        parser.add_argument('--verbose', '-v', action='count', default=0, help='more output')
        parser.add_argument('--quiet', '-q', action='count', default=0, help='less output')

        parser.add_argument('root_namespace')
        args = parser.parse_args()

        logger = FilteredLogger(args.verbose - args.quiet + 3)

        inp_dir = args.xml_dir
        out_dir = args.out_dir
        root_namespace = args.root_namespace

        tree = ET.parse(inp_dir + '/index.xml')
        generator = RstGenerator(inp_dir, out_dir, root_namespace, logger)
        generator.render_namespace_by_name(tree, root_namespace)
