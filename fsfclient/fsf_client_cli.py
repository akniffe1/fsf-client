#! /usr/bin/env python
#
"""
@author: Adam Kniffen
@contact: akniffen@cisco.com
@copyright: Copyright 2016
@organization: Cisco Active Threat Analytics
@status: Development
"""
import os
import sys
import argparse
import json

from fsf_client import FSFClient
from fsf_client import FSFClientConfig


def main():

    parser = argparse.ArgumentParser(prog='fsfclient',
                                     description="""Uploads files to scanner server and returns the results to the user if desired. Results will always be written to a server side log file. Default options for each flag are designed to accommodate easy analyst interaction. Adjustments can be made to accommodate larger operations. Read the documentation for more details!""")
    parser.add_argument('file', nargs='*', type=argparse.FileType('r'), help='Full path to file(s) to be processed.')
    parser.add_argument('--delete', default=False, action='store_true', help="""Remove file from client after sending to the FSF server. Data can be archived later on server depending on selected options.""")
    parser.add_argument('--source', nargs='?', type=str, default='Analyst', help="""Specify the source of the input. Useful when scaling up to larger operations or supporting multiple input sources, such as; integrating with a sensor grid or other network defense solutions. Defaults to \'Analyst\' as submission source.""")
    parser.add_argument('--archive', nargs='?', type=str, default='none', help="""Specify the archive option to use. The most common option is \'none\' which will tell the server not to archive for this submission (default). \'file-on-alert\' will archive the file only if the alert flag is set. \'all-on-alert\' will archive the file and all sub objects if the alert flag is set. \'all-the-files\' will archive all the files sent to the scanner regardless of the alert flag. \'all-the-things\' will archive the file and all sub objects regardless of the alert flag.""")
    parser.add_argument('--suppress-report', default=False, action='store_true', help="""Don\'t return a JSON report back to the client and log client-side errors to the locally configured log directory. Choosing this will log scan results server-side only. Needed for automated scanning use cases when sending large amount of files for bulk collection. Set to false by default.""")
    parser.add_argument('--full', default=False, action='store_true', help="""Dump all sub objects of submitted file to current directory of the client. Format or directory name is \'fsf_dump_[epoch time]_[md5 hash of scan results]\'. Only supported when suppress-report option is false (default).""")
    parser.add_argument("--conf", action="store_true", help="Replace your entire client configuration with the file supplied")
    parser.add_argument("--dumpconfig", action="store_true", help="prints out your current client config to the supplied file")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    try:
        args = parser.parse_args()

    except IOError:
        e = sys.exc_info()
        print 'The file provided could not be found. Error: %s' % e
        sys.exit(1)

    if len(args.file) == 0:
        print 'A file to scan needs to be provided!'

    if args.conf:
        c = FSFClientConfig()
        resp = c.replaceconfig(args.file[0])
        print resp
        sys.exit(1)

    if args.dumpconfig:
        c = FSFClientConfig()
        try:
            # take the first object in the file list, get its path using file.name, close it, and then open
            # for writing and json.dumps the current config. Its kinda hackish--but it preserves the basic client
            # behavior of opening all files that get submitted to FSFServer in read only mode
            outpath = args.file[0].name
            args.file[0].close()
            with open(outpath, 'w') as f:
                f.write(json.dumps(c.current))

        # be prepared to handle whatever exceptions you might get from allowing user file r/w decisions
        except Exception, err:
            print err
            sys.exit(1)

        # exit, since we don't want to submit our config file to FSFServer
        sys.exit(1)

    for f in args.file:
        filename = os.path.basename(f.name)
        fsf = FSFClient(samplename=filename, fullpath=os.path.abspath(f.name), delete=args.delete, source=args.source,
                        archive=args.archive, suppress_report=args.suppress_report, full=args.full,
                        sampleobject=f.read())
        fsf.initiate_submission()


if __name__ == '__main__':
    main()
