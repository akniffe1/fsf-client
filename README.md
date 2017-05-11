# fsf-client

A packaged python client to https://github.com/emersonelectricco/fsf

## Installation
```
pip install git+https://github.com/akniffe1/fsf-client.git
```

## Usage
````
usage: fsfclient [-h] [--delete] [--source [SOURCE]] [--archive [ARCHIVE]]
                  [--suppress-report] [--full] [--conf] [--dumpconfig]
                  [file [file ...]]

Uploads files to scanner server and returns the results to the user if
desired. Results will always be written to a server side log file. Default
options for each flag are designed to accommodate easy analyst interaction.
Adjustments can be made to accommodate larger operations. Read the
documentation for more details!

positional arguments:
  file                 Full path to file(s) to be processed.

optional arguments:
  -h, --help           show this help message and exit
  --delete             Remove file from client after sending to the FSF
                       server. Data can be archived later on server depending
                       on selected options.
  --source [SOURCE]    Specify the source of the input. Useful when scaling up
                       to larger operations or supporting multiple input
                       sources, such as; integrating with a sensor grid or
                       other network defense solutions. Defaults to 'Analyst'
                       as submission source.
  --archive [ARCHIVE]  Specify the archive option to use. The most common
                       option is 'none' which will tell the server not to
                       archive for this submission (default). 'file-on-alert'
                       will archive the file only if the alert flag is set.
                       'all-on-alert' will archive the file and all sub
                       objects if the alert flag is set. 'all-the-files' will
                       archive all the files sent to the scanner regardless of
                       the alert flag. 'all-the-things' will archive the file
                       and all sub objects regardless of the alert flag.
  --suppress-report    Don't return a JSON report back to the client and log
                       client-side errors to the locally configured log
                       directory. Choosing this will log scan results server-
                       side only. Needed for automated scanning use cases when
                       sending large amount of files for bulk collection. Set
                       to false by default.
  --full               Dump all sub objects of submitted file to current
                       directory of the client. Format or directory name is
                       'fsf_dump_[epoch time]_[md5 hash of scan results]'.
                       Only supported when suppress-report option is false
                       (default).
  --conf               Replace your entire client configuration with the file
                       supplied
  --dumpconfig         prints out your current client config to the supplied
                       file
````


### Configuration
Odds are that you're going to use the client on more hosts than just your FSF Server (call that localhost), so you can update the
fsf-server and fsf-client configuration variables using the --conf and --dumpconf flags in this manner:

* First, dump your current config to the file and path of your choosing
````
fsfclient --dumpconfig /path/to/file/where/you/want/to/copy/your/config/fsfclient.json
````

* Now, you can edit that file with the server.ip_address, server.port, and client.log_path of your choosing. 

* Finally, use the --conf flag to replace your old configs with the new ones in your configfile. 
````
fsfclient --conf /path/to/file/where/you/want/to/copy/your/config/fsfclient.json
````

Alternatively, you can fork this repo, update fsf-client/fsfclient/fsfclient.json with your desired config values, and then
````
pip install git+https://github.com/mygitaccount/fsf-client.git
````

#### Submitting Files for Scanning by FSF
There are a number of useful options in fsfclient for tailoring your submission to the different kinds
of response, storage, and alerting that FSF-Server can provide, and all of these are optional flags on the file submission. 
To simply submit a file and get the scan report back, run the following:
````
fsfclient /path/to/my/file 
````

##### Returning JSON When Calling the FSFClient class with Python

The following example will return a JSON dict for use by a python script
  ```# Read in file  
  f = open(self.fullpath, 'r')
  ```
  Initialze FSF Client
  ```fsf = fsf_client.FSFClient(samplename=str(filename),
                             fullpath=str(fullpath),
                             delete=False,
                             source='Analyst',
                             archive='none',
                             suppress_report=False,
                             full=False,
                             sampleobject=f.read())
  ```
  
  Submit file f to fsfclient, and return a json object as a string
  
  `out = fsf.initiate_submission(return_json=True)`
  
  Load our json object into a python dict for futher parsing
  `parsed_json = json.loads(out)`
