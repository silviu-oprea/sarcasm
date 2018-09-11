import argparse
import math

from ml.kfold import SplitSpec


class ValidSplitSpec(argparse.Action):
    def __call__(self, parser, namespace, args, option_string=None):
        if not math.isclose(sum(args), 1):
            raise argparse.ArgumentTypeError("ProbabilityDistribution: {} does not sum up to 1".format(args))
        setattr(namespace, self.dest, SplitSpec(*args))


class ValidProbabilityDistribution(argparse.Action):
    def __call__(self, parser, namespace, args, option_string=None):
        print(args)
        if not math.isclose(sum(args), 1):
            raise argparse.ArgumentTypeError("ProbabilityDistribution: {} does not sum up to 1".format(args))
        setattr(namespace, self.dest, args)
