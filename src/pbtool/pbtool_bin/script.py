import argparse
import imp
import json
import logging
import os
import platform
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

import requests

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


@contextmanager
def temporary_directory():
    try:
        td = tempfile.mkdtemp()
        yield td
    finally:
        shutil.rmtree(td)


def find_compiler():
    if platform.system() == 'Windows':
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(here, 'compiler', 'protoc')
    else:
        try:
            return subprocess.check_output('which protoc', shell=True).strip()
        except:
            raise RuntimeError("Protobuf compiler not found.  Have you installed it?  (Eg: apt-get install protobuf-compiler)")


def compile(proto_path):
    proto_path = os.path.abspath(proto_path)
    with temporary_directory() as temp_folder:
        command = [find_compiler(), '-I', os.path.dirname(proto_path), '--python_out', temp_folder, proto_path]
        logger.debug(command)
        subprocess.check_call(command)
        stem = os.path.splitext(os.path.basename(proto_path))[0]
        out_file = os.path.join(temp_folder, stem + '_pb2.py')
        return imp.load_source(stem, out_file)


def resolve(field_desc, v):
    if field_desc.type == field_desc.TYPE_ENUM:
        if not isinstance(v, basestring):
            raise ValidationError('Enums should be specified with string values, not {}'.format(type(v)))
        try:
            return field_desc.enum_type.values_by_name[v].number
        except KeyError:
            raise ValidationError('"{}" is not a valid member of the {} enum'.format())
    return v


def set_field(instance, field_desc, k, v):
    if field_desc.label == field_desc.LABEL_REPEATED:
        if not isinstance(v, list):
            raise ValidationError('Repeated field {} must be represented as a json list'.format(field_desc.full_name))
        if field_desc.type == field_desc.TYPE_MESSAGE:
            # Repeated message field
            for obj in v:
                if not isinstance(obj, dict):
                    raise ValidationError('Repeated message field {} requires a list of objects (not scalars)'.format(field_desc.full_name))
                new_instance = getattr(instance, k).add()
                fill(new_instance, obj)
        else:
            # Repeated scalar field
            for item in v:
                getattr(instance, k).append(resolve(field_desc, item))
    else:
        # Scalar field
        setattr(instance, k, resolve(field_desc, v))


def fill(instance, data):
    for k, v in data.items():
        try:
            field_desc = instance.DESCRIPTOR.fields_by_name[k]
        except KeyError:
            raise ValidationError('class {} has no field named {}'.format(instance.DESCRIPTOR.name, k))
        logger.debug('Descriptor for field "%s":\n%s', k, dir(field_desc))
        logger.debug('Setting %s', field_desc.full_name)
        set_field(instance, field_desc, k, v)
    return instance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('proto', help='The .proto file to be compiled.')
    parser.add_argument('cls', help='The case-sensitive name of a class within the .proto file that will be instantiated and populated.')
    parser.add_argument('input', help='The json file that will provide the data to be loaded into the protobuf instance.')
    parser.add_argument('-o', '--output', default=None, help='A destination file to serialize the populated protobuf to.')
    parser.add_argument('--http-url', dest='url', default=None, help='A url to POST the protobuf to.')
    parser.add_argument('--http-add-header', dest='header', default=[], action='append', help='A header to include in the POST request.  Can be specified more than once.')
    parser.add_argument('--http-save-response', dest='save_response', default=None, help='The file path to which the http response body should be saved')
    parser.add_argument('--inspect', default=False, action='store_true', help='Adds a breakpoint after protobuf serialization so you can inspect the instance.  The instance is available in a stack variable called "instance".')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Enables more verbose logging output.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if not os.path.exists(args.proto):
        raise RuntimeError('The specified protobuf file does not exist')
    if not os.path.exists(args.input):
        raise RuntimeError('The specified json input file does not exist')

    try:
        with open(args.input) as fp:
            data = json.load(fp)
    except:
        logger.error('Failed to load json input data')
        raise

    try:
        mod = compile(args.proto)
    except:
        logger.error('Failed to compile the protobuf')
        raise
    try:
        cls = getattr(mod, args.cls)
    except:
        logger.error('The protobuf does not define a class named: %s', args.cls)
        raise

    try:
        instance = cls()
        fill(instance, data)
    except ValidationError:
        logger.error('The provided json object did not comply with the schema for %s', args.cls)
        raise
    except:
        logger.error('Failed to instantiate protobuf with the provided data')
        raise

    try:
        bin = instance.SerializeToString()
    except:
        logger.error('Failed to serialize protobuf')
        raise

    if args.output:
        with open(args.output, 'wb') as fp:
            fp.write(bin)

    if args.inspect:
        instance = cls()
        instance.ParseFromString(bin)
        import pdb
        pdb.set_trace()

    if args.url:
        logger.info('Posting to %s', args.url)
        headers = {}
        for header in args.header:
            try:
                parts = header.split(':')
                headers[parts[0].strip()] = parts[1]
            except IndexError:
                logger.error('Invalid header: %s', header)
                raise
        res = requests.post(args.url, data=bin, headers=headers, verify=False)
        logger.info('%s: %s', res.status_code, res.reason)

        if args.save_response:
            with open(args.save_response, 'wb') as fp:
                fp.write(res.raw.read())
            logger.info('Response saved to: %s', args.save_response)
