## CAM Commands
Here you can find a brief description of the Leica CAM commands.

Currently leicacam have implemented some convenience methods:
- start_scan
- stop_scan
- pause_scan
- enable
- disable
- enable_all
- disable_all
- save_template
- load_template
- get_information

But all commands can be sent like this:
```python
command = [('cmd', 'enableall'),
           ('value', 'true')]
cam.send(command)
```

### Commands
#### General
| **cmd**       | **description**   |
| ------------- | ----------------- |
| startscan     | start matrix scan |
| stopscan      | stop matrix scan  |
| pausescan     | toggle pause of matrix scan |
| autofocusscan | start matrix focus scan |
| load          | load specific experiment from XML |
| save          | save experiment positions to XML |
| enable        | enable single scan field |
| disable       | disable single scan field |
| enableall     | enable all scan fields |
| disableall    | disable all scan fields |
| getinfo       | get information about stage, z-drive, COR-ring, job list, patter list, scan status, experiment, position, load position, autofocus mode (galvo or wide), autofocus position |

#### CAM list
| **cmd**       | **description**   |
| ------------- | ----------------- |
| deletelist    | remove scan fields added to CAM list |
| startcamscan  | start scan of CAM list  |
| stopcamscan   | stop scan of CAM list   |
| add           | add scan field to CAM list |
| stopwaitingforcam | close *Waiting for External Command* dialog and continue experiment |
| skip          | close *Waiting for External Command* and stop, continue or leave pattern |
| skip          | **doesn't need wait for ext. command**: continue with next job, scan field or well, or go to lower CAM level |

#### Settings
| **cmd**       | **description**   |
| ------------- | ----------------- |
| pump          | set pump and interval time for water pump |
| adjust        | set settings for pinhole (airy units) or pmt (offset, gain) |
| adjustls      | adjust light source, wavelength and intensity of laser |
| loop          | adjust number of well loops and timing |
| barcode       | set barcode of experiment |
| adjustmosaic  | adjust width, height, start position and autofocus fields of mosaic |
| adjustmatrix  | adjust start position, well distance and scan field distance of matrix |
| enableattribute | enable drift compensation, tracking or pump for given field |

#### Position
| **cmd**       | **description**   |
| ------------- | ----------------- |
| setposition   | move stage or z-drive to specified position |
| movetowell    | move to first scan field of given well |
| savecurrentposition | save a position to memory |
| returntosavedposition | return to a position saved in memory |
| loadposition  | move to load position defined in experiment |
| startposition | move to start position defined in experiment |

#### Asigning job
| **cmd**       | **description**   |
| ------------- | ----------------- |
| selectfield   | select scan fields for assigning jobs |
| selectallfields | select all scan fields |
| assignjob     | asign job to selected fields |

#### Mark and find
| **cmd**       | **description**   |
| ------------- | ----------------- |
| maf + addxyza | insert position to mark and find list |
| maf + delete | delete mark and find list |
| maf + load | load mark and find list from xml |
| maf + save | save mark and find list to xml |
| maf + toselected | assign mark and find list to given well |
| maf + toall | assign mark and find list to all wells |
