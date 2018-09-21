# SIMPLE-MAGIC
SIMPLE MAGIC: Synthesis and In-memory MaPping of Logic Execution for Memristor Aided loGIC

## Dependencies
In order to use SIMPLE-MAGIC, you will need a Linux machine with:
1. Python 2.7
2. [Z3](https://github.com/Z3Prover/z3): Run the following commands to install it:
```sh
git clone --recursive https://github.com/Z3Prover/z3.git
cd z3
python scripts/mk_make.py --python
cd build
make
make install
```
3. [ABC Synthesis Tool](https://bitbucket.org/alanmi/abc)
4. The following Python packages (for graphic description of the solution):
- tk
```sh
apt-get install python-tk
```
- matplotlib
```sh
apt-get install python-matplotlib
```
- [OpenCV](http://docs.opencv.org/2.4/doc/tutorials/introduction/linux_install/linux_install.html)

## Manual
1. Configure: in the file simple_conf.cfg you will find the following content:
```ini
[input_output]
input_path=cm138a.blif
; input_format can get one of the values: verilog, blif
input_format=blif
output_path=cm138a_output

[abc]
abc_dir_path=/home/adi/abc/alanmi-abc-eac02745facf

[Z3]
Z3_path=/usr/bin/z3

```
Change the parameters according to your needs.

2. Run:
```sh
python simple_main.py
```
3. Parse:
When Z3 finishes running and output_path is created, run:
```sh
python convert_gates_2_array.py -f output_path
```
The memory array will be printed, for example:
![Alt text](images/full_adder_table.png?raw=true "Title")

In addition, two images will be created:
- Graphic description of the logic execution in the memory. The table drawn in this image represents the memory array. Each circle is a gate port (input or output). Inputs are denoted with the letters A-C and outputs are denoted with E. the number following the letter identifies the gate. Each clock cycle is marked with a different color.
![Alt text](images/full_adder_1bit_nor2_Z3output_table.png?raw=true "Title")
- Clock cycle legend.

![Alt text](images/full_adder_1bit_nor2_Z3output_legend.png?raw=true "Title2") 


## Executing using docker 

Project consist of two docker Images

* dockerfiles/DockerfileCV (name = simple-magic-cv) - with OpenCV3 (Required for OpenCV based visualisation Only)

* dockerfiles/Dockerfile (name = simple-magic)  - Lightweight without OpenCV


simple-magic-cv and simple-magic are derived from OpenCV3+Pytho2.7 and Ubuntu18:04 Images respectively. It has verified installation of ABC Synthesis Tool + Z3 Solver. Pull docker images using following commands.

```ini
docker pull goreganesh007/simple-magic-cv
docker pull goreganesh007/simple-magic
```

**Note** : To modify docker image, refer Readme file in dockerfiles folder

Once you download images execute following commands to create command shortcuts. It will create two shotcut commnad 
* smagiccv - Execute commands in goreganesh007/simple-magic-cv
* smagic - Execute commands in goreganesh007/simple-magic

```ini
#To create alias of docker command (smagic) Read comments in the file to learn more
dockerfiles\windowsSource.bat # for windows 
source linuxSource.sh # for linux
```

You can use shotcuts as - *smagic <command_to_run_>*  or *smagiccv <command_to_run_>* 

For example: 

Note : No need to configure simple_conf.cfg default cconfiguration will work fine
```ini
smagic python simple_main.py  # Will create final netlist file 

smagiccv python convert_gates_2_array.py -f <SynthesizedNetlistName> # Will create OpenCV3 visualisation image 
```

## Visualising crossbar computation using SVGs - **MagicPrinter.py**

Basic idea is create SVG file of crossbar configuration for each clock, 
and then use browser \( index.html \) to browse through each clock sequencially. 

Input to the script is *.smagic file which lists all the dummy assembly instructions to run in cross bar. Specification of file is as follows 

### **smagic file Specification**
### **Directives**
```ini
.GRID <Rows> <Cols>
```
.GRID directive initiliases cross bar with defined rows and columns 

### **Instructions**
Each cell is defined as **R**<-RowNo->**C**<-CellNo->
```ini
#Instruction Template
#<INPUT|OUTPUT> <CellName>
#<NOT|NOR> <OUTPUTCell> <ListofInputCells>

# Define Input in R1C1
INPUT R1C1

# Define OUTPUT in R1C4
OUTPUT R1C4

# R1C3 = Not R1C2
NOT R1C3 R1C2

# R1C3 = R1C2 NOR R1C1
NOR R1C3 R1C2 R1C1

#You can also write multiple instructions per row 
#It represents Multiple computations in same clock cycle 
NOR R1C3 R1C2 R1C1 | NOR R2C3 R2C2 R2C1 | ...

# Optionally you can also mention tag for only output cell
NOR R1C3(I1) R1C2 R1C1
```

To render example code, run following command 

```ini
smagic python MagicPrinter.py --input MagicPrinterExample.smagic
```

Open index.html file in borwser and use right and left arrow to navigate

![Alt text](images/example_code_view.png?raw=true "Title2") 


## Creating smagic (dummy assembly) file from SMT file - **CompileToSmagic.py**

This script accepts Z3 constraint file and outputs smagic file indicating computation in each clock 

```ini
smagic python CompileToSmagic.py --input < Input_SMT_Filename > --output < Output_smagic_filename >
```

**Example**
```ini
# Default input file : outputNorInv.v_python_Z3input.txt
# Default output file : main.smagic
smagic python CompileToSmagic.py
```