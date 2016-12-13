#!/usr/bin/env python
#
# FSF Client for sending information and generating a report
#
# Jason Batchelor
# Emerson Corporation
# 02/09/2016
"""
   Copyright 2016 Emerson Electric Co.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import argparse
import hashlib
import os
import random
import socket
import struct
import sys
import time
from datetime import datetime as dt

import config


class FSFClient:
    """FSFClient is the class that you call when you want to send a file to FSF"""

    def __init__(self, fullpath, samplename, delete, source, archive, suppress_report, full, sampleobject):
        """
        :param fullpath: type(str) path to the file object being submitted. Used for submission metadata.
        This gets added to the scan report
        :param samplename: type(str) the filename of the file object being submitted. Used for submission metadata.
        This gets added to the scan report
        :param delete: type(bool) Specifies whether the client will delete the submission file object after it's sent.
        :param source: type(dict) any additional metadata about the file object being submitted. 
        This gets added to the scan report
        :param archive: type(string). If an archive condition is met, the file object submitted will be saved 
        on the FSF Server. Options:
            none: Don't Archive, Ever.
            file-on-alert: Only archive if an alert condition specified in the dispositioner is met.
            all-on-alert: Archive the submission object and all its sub-objects if an alert condition specified in the 
            dispositioner is met.
            all-the-files: Archive every file submitted.
            all-the-things: Archive every file submitted and all its sub-objects.
        :param suppress_report: Submit the file and close the socket, don't wait for any response content like the 
        scan report.
        :param full: Return the scan report AND all sub-objects of the submitted file object.
        :param sampleobject: a buffer containing the file that you're submitting.
        """
        
        self.fullpath = fullpath
        self.samplename = samplename
        self.delete = delete
        self.source = source
        self.archive = archive
        self.suppress_report = suppress_report
        self.full = full
        self.sampleobject = sampleobject
        # will hold host after verifying connection to server
        self.host = ''  # todo set this to a default value
        self.port = config.SERVER_CONFIG['PORT']
        self.logfile = config.CLIENT_CONFIG['LOG_FILE']
        self.server_list = config.SERVER_CONFIG['IP_ADDRESS']

        archive_options = ['none', 'file-on-alert', 'all-on-alert', 'all-the-files', 'all-the-things']
        if args.archive not in archive_options:
            error = '''%s Please specify a valid archive option: \'none\', \'file-on-alert\', \'all-on-alert\',
             \'all-the-files\' or \'all-the-things\'.\n''' % dt.now()
            self.issue_error(error)
            sys.exit(1)

    def initiate_submission(self):
        """
        Test connect to a FSF server in your FSF server pool (if configured)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        random.shuffle(self.server_list)
        attempts = 0
      
        for server in self.server_list:
            success = 1
            try:
                sock.connect((server, self.port))
            except:
                warning = '%s There was a problem connecting to %s on port %s. Trying another server. <WARN>\n' % \
                         (dt.now(), server, self.port)
                self.issue_error(warning)
                success = 0
                attempts += 1
            if success:
                self.host = server
                self.process_files()
                break
            elif attempts == len(self.server_list):
                e = sys.exc_info()
                error = '%s There are no servers available to send files too. Error: %s\n' % (dt.now(), e)
                self.issue_error(error)

    def process_files(self):
        """
        Send files to the FSF Server for processing; removes or retains the submitted file based on self.delete, 
        and either sends the connection socket to the FSF Server to FSFClient.process_results or closes the socket based
        on self.suppress_report
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        msg = '%sFSF_RPC%sFSF_RPC%sFSF_RPC%sFSF_RPC%sFSF_RPC%s' % \
              (self.samplename, self.source, self.archive, self.suppress_report, self.full, self.sampleobject)
        buffer = struct.pack('>I', len(msg)) + 'FSF_RPC' + msg
        try:
            sock.connect((self.host, self.port))
            sock.sendall(buffer)
        except:
            e = sys.exc_info()
            error = '%s There was a problem sending file %s to %s on port %s. Error: %s\n' % \
                    (dt.now(), self.samplename, self.host, self.port, e)
            self.issue_error(error)
        finally:
            if self.delete:
                os.remove(self.fullpath)
            if not self.suppress_report:
                self.process_results(sock)
            sock.close()

    def process_results(self, sock):
        """
        Processes results sent back to the client from the FSF Server, 
        Required method if you want the scan report or sub-objects
        :param sock: the socket
        """
        try:
            raw_msg_len = sock.recv(4)
            msg_len = struct.unpack('>I', raw_msg_len)[0]
            data = ''

            while len(data) < msg_len:
                recv_buff = sock.recv(msg_len - len(data))
                data += recv_buff
            print data

         # Does the user want all sub objects?
            if self.full:
                # Generate dirname by calculating epoch time and hash of results
                dirname = 'fsf_dump_%s_%s' % (int(time.time()), hashlib.md5(data).hexdigest())
                self.dump_subobjects(sock, dirname)

        except:
            e = sys.exc_info()
            error = '%s There was a problem getting data for %s from %s on port %s. Error: %s' % \
                    (dt.now(), self.samplename, self.host, self.port, e)
            self.issue_error(error)

    def dump_subobjects(self, sock, dirname):
        """
        Dumps all subobjects returned by the scanner server into a new directory
        :param sock: The Socket
        :param dirname: the new directory whe
        """
        sub_status = sock.recv(4)
        if sub_status == 'Null':
            print 'No subobjects were returned from scanner for %s.' % self.samplename
            return

        os.mkdir(dirname)

        while self.full:
            raw_sub_count = sock.recv(4)
            sub_count = struct.unpack('>I', raw_sub_count)[0]
            raw_msg_len = sock.recv(4)
            msg_len = struct.unpack('>I', raw_msg_len)[0]
            data = ''

            while len(data) < msg_len:
                recv_buff = sock.recv(msg_len - len(data))
                data += recv_buff

            fname = hashlib.md5(data).hexdigest()
            with open('%s/%s' % (dirname, fname), 'w') as f:
                f.write(data)
                f.close  #todo, this is redundant

            if sub_count == 0:
                self.full = False

        print 'Sub objects of %s successfully written to: %s' % (self.samplename, dirname)

    def issue_error(self, error):
        """
        Handles local FSFClient errors by logging to a file specified in the configs or printing to stdout
        :param error: The error message
        """
        if self.suppress_report:
            with open(self.logfile, 'a') as f:
                f.write(error)
                f.close()
        else:
            print error


