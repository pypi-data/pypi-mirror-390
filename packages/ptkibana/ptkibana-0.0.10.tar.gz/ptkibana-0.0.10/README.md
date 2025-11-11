[![penterepTools](https://www.penterep.com/external/penterepToolsLogo.png)](https://www.penterep.com/)


## PTKIBANA
Security testing tool for identifying, fingerprinting, and exploiting vulnerabilities in Kibana instances.  
The tool:
- Identifies whether or not Kibana is running on a host
- Identifies whether it is running on HTTP or HTTPS
- Identifies whether or not it has authentication enabled
- Identifies CVEs in the Kibana instance
- Identifies whether the /api/console/proxy endpoint is available and runs the tool [PTELASTIC](https://github.com/Penterep/ptelastic) through the proxy.
- Test for CVE-2019-7609
- Enumerates:
  - Users and their respective roles
  - Plugins running on the Kibana instance
- Dump ES index structure

## Installation

```
pip install ptkibana
```

## Adding to PATH
If you're unable to invoke the script from your terminal, it's likely because it's not included in your PATH. You can resolve this issue by executing the following commands, depending on the shell you're using:

For Bash Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc
```

For ZSH Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

## Usage examples
```
ptkibana -u htttps://www.example.com/
```

## Options
```
   -u     --url                  <url>                             Connect to URL
   -ts    --tests                <test>                            Specify one or more tests to perform:
                                  AUTH                             Kibana authentication test
                                  CVE-2019-7609                    Kibana CVE-2019-7609 test
                                  CVE_LOOKUP                       Kibana CVE lookup
                                  ES_PROXY                         Kibana Elasticsearch proxy test
                                  HTTPS                            Kibana HTTP/S test
                                  IS_KIBANA                        Kibana availability test
                                  STRUCTURE_DUMP                   Kibana data structure test
                                  SW                               Kibana software enumeration
                                  USERS                            Kibana user enumeration
   -t     --threads              <threads>                         Set thread count (default 10)
   -p     --proxy                <proxy>                           Set proxy (e.g. http://127.0.0.1:8080)
   -T     --timeout                                                Set timeout (default 10)
   -c     --cookie               <cookie>                          Set cookie
   -a     --user-agent           <a>                               Set User-Agent header
   -H     --headers              <header:value>                    Set custom header(s)
   -r     --redirects                                              Follow redirects (default False)
   -C     --cache                                                  Cache HTTP communication (load from tmp in future)
   -v     --version                                                Show script version and exit
   -vv    --verbose                                                Enable verbose mode
   -h     --help                                                   Show this help message and exit
   -j     --json                                                   Output in JSON format
   -U     --user                                                   Set user to authenticate as
   -P     --password                                               Set password to authenticate with
   -A     --api-key                                                Set API key to authenticate with
   -F     --file                 </path/to/file>                   File to read if host is vulnerable to CVE-2015-5531 (default /etc/passwd)
   -di    --dump-index           <index1, index2, ...>             Specify index to dump with data_dump module
   -df    --dump-field           <field1,field2, field3.subfield>  Specify fields to dump with data_dump module
   -o     --output               <filename>                        Specify the name of the file to store structure/data dump to
   -ests  --elasticsearch-tests  <test>                            Specify one or more tests to perform on Elasticsearch through the Kibana proxy
   -b     --built-in                                               Enumerate/dump built-in (hidden) Elasticsearch indexes
```

## Dependencies
```
ptlibs
```

## License

Copyright (c) 2025 Penterep Security s.r.o.

ptkibana is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

ptkibana is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with ptkibana. If not, see https://www.gnu.org/licenses/.

## Warning

You are only allowed to run the tool against the websites which
you have been given permission to pentest. We do not accept any
responsibility for any damage/harm that this application causes to your
computer, or your network. Penterep is not responsible for any illegal

or malicious use of this code. Be Ethical!



