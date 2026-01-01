# Re-analyzing recordings

Every once in a while, VNCSSdetector refines its heuristics to detect more kinds of
suspicious behavior, and to reduce noise from incorrect alerts.

This means that your old green recordings may actually contain data that is now
deemed suspicious, and also old red recordings may become green.

You can re-analyze any old recording inside of VNCSSdetector by clicking on "N
warnings" to expand details, then clicking the "re-analyze" button.

## Analyzing recordings on Desktop

If you have a PCAP or QMDL file but no vncssdetector, you can analyze it on desktop
using the `vncssdetector-check` CLI tool. That tool contains the same heuristics as
VNCSSdetector and will also work on traffic data captured with other tools, such as
QCSuper.

Since 0.6.1, `vncssdetector-check` is included in the release zipfile.

You can build `vncssdetector-check` from source with the following command:
`cargo build --bin vncssdetector-check` 

## Usage
```sh
vncssdetector-check [OPTIONS] --path <PATH>

Options:
  -p, --path <PATH>   Path to the PCAP, or QMDL file. If given a directory will 
                        recursively scan all pcap, qmdl, and subdirectories 
  -P, --pcapify       Turn QMDL file into PCAP     
      --show-skipped  Show skipped messages
  -q, --quiet         Print only warnings
  -d, --debug         Print debug info 
  -h, --help          Print help
  -V, --version       Print version
```
### Examples 
`vncssdetector-check -p ~/Downloads/myfile.qmdl`

`vncssdetector-check -p ~/Downloads/myfile.pcap`

`vncssdetector-check -p ~/Downloads #Check all files in downloads`

`vncssdetector-check -d -p ~/Downloads/myfile.qmdl #run in debug mode`
