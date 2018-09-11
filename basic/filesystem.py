import argparse
import os
from collections import namedtuple


class ReadableDir(argparse.Action):
    def __call__(self, parser, namespace, dir, option_string = None):
        if not os.path.isdir(dir):
            raise argparse.ArgumentTypeError("ReadableDir: dir {0} not found".format(dir))
        if os.access(dir, os.R_OK):
            setattr(namespace, self.dest, dir)
        else:
            raise argparse.ArgumentTypeError("ReadableDir: cannot read from {0}".format(dir))


class EnsureWritableDir(argparse.Action):
    def __call__(self, parser, namespace, dir, option_string = None):
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir, exist_ok=True)
            except OSError:
                raise argparse.ArgumentTypeError("EnsureWritableDir: cannot create {0}".format(dir))
        if os.access(dir, os.W_OK):
            setattr(namespace, self.dest, dir)
        else:
            raise argparse.ArgumentTypeError("EnsureWritableDir: cannot write to {0}".format(dir))


class EnsureWritableFileDir(argparse.Action):
    def __call__(self, parser, namespace, path, option_string = None):
        dir = root_and_name(path).root
        if not os.path.isdir(dir):
            try:
                os.mkdir(dir)
            except OSError:
                raise argparse.ArgumentTypeError("EnsureWritableFileDir: cannot create {0}".format(dir))
        if os.access(dir, os.W_OK):
            setattr(namespace, self.dest, path)
        else:
            raise argparse.ArgumentTypeError("EnsureWritableFileDir: cannot write to {0}".format(dir))


class ReadableFile(argparse.Action):
    def __call__(self, parser, namespace, file, option_string = None):
        if not os.path.isfile(file):
            raise argparse.ArgumentTypeError("ReadableFile: file {0} not found".format(file))
        if os.access(file, os.R_OK):
            setattr(namespace, self.dest, file)
        else:
            raise argparse.ArgumentTypeError("ReadableFile: cannot read from {0}".format(file))


def readable_file(file):
    if not (os.path.isfile(file) and os.access(file, os.R_OK)):
        return False
    else:
        return True


def readable_files(*files):
    return all(readable_file(f) for f in files)


def readable_dir(dir):
    if not (os.path.isdir(dir) and os.access(dir, os.R_OK)):
        return False
    else:
        return True


def writable_file(file):
    if not (os.path.isfile(file) and os.access(file, os.W_OK)):
        return False
    else:
        return True


def writable_dir(dir):
    if not (os.path.isdir(dir) and os.access(dir, os.W_OK)):
        return False
    else:
        return True


def ensure_writable_dir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if os.access(dir, os.W_OK):
        return True
    else:
        return False


def ensure_writable_file_loc(file_path):
    root_dir = root_and_name(file_path).root
    if not os.path.isdir(root_dir):
        os.makedirs(root_dir, exist_ok=True)
    if os.access(root_dir, os.W_OK):
        return True
    else:
        return False


PathAndExtension = namedtuple('PathAndExtension', ['path', 'extension'], verbose=False)
RN = namedtuple('PathAndName', ['root', 'name'], verbose=False)
RNS = namedtuple('RNS', ['root', 'name', 'extension'], verbose=False)
NS = namedtuple('NS', ['name', 'extension'], verbose=False)


def remove_ext(path):
    return os.path.splitext(path)[0]


def root_and_name(path):
    s = os.path.split(path)
    return RN(s[0], s[1])


def root_name_and_extension(path):
    s = os.path.split(path)
    root = s[0]
    name_and_ext = s[1]

    if readable_dir(path):
        return RNS(root, name_and_ext, '')
    else:
        s = os.path.splitext(name_and_ext)
        name = s[0]
        ext = s[1][1:]
        return RNS(root, name, ext)


def name(path):
    return root_name_and_extension(path).name
