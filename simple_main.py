import ConfigParser
import os
import tempfile
import Netlist_to_Z3_latency_nor2
import argparse

parser = argparse.ArgumentParser(
    description='This script synthesis verilog module and create\
                 Z3 constraint file ')
parser.add_argument('--input', default="",
                    help='Z3 Contraints file')
parser.add_argument('--config', default="simple_conf.cfg",
                    help='Configuration file for tools')
parser.add_argument('--clean', default="False",
                    help='To clean all temporary file')
parser.add_argument('--output', default="main",
                    help='Output Filename (.smagic appended by default)')
args = parser.parse_args()
print args.clean, bool(args.clean)

tempfile.tempdir = os.path.join(os.getcwd(), "tmp")
if not os.path.isdir(tempfile.tempdir):
    os.mkdir(tempfile.tempdir)


def main():
    # Read configuration parameters
    config = ConfigParser.ConfigParser()
    config.readfp(open(args.config))
    input_path = config.get('input_output', 'input_path')
    input_path = args.input if len(args.input) else input_path
    input_format = config.get('input_output', 'input_format')
    abc_dir_path = config.get('abc', 'abc_dir_path')
    Z3_path = config.get('Z3', 'Z3_path')
    output_path = config.get('input_output', 'output_path')

    abc_exe_path = os.path.join(abc_dir_path, "abc")
    abc_rc_path = os.path.join(abc_dir_path, "abc.rc")

    # Create abc script
    abc_script = file('abc_script_template.abc', 'rb').read()
    abc_script = abc_script.replace('abc_rc_path', abc_rc_path)
    abc_script = abc_script.replace('input.blif', input_path)
    if input_format == 'verilog':
        abc_script = abc_script.replace('read_blif', 'read_verilog')
    abc_script = abc_script.replace('lib.genlib', 'mcnc1_nor2.genlib')
    abc_output_path = os.path.join(tempfile.tempdir, "outputNorInv.v")
    abc_script = abc_script.replace('output.v', abc_output_path)
    print "abc_output_path - ", abc_output_path

    # Run abc script
    abc_script_path = os.path.join(tempfile.tempdir, "abc_script_path")
    open(abc_script_path, "wb").write(abc_script)
    cmd = '%s -f "%s"' % (abc_exe_path, abc_script_path)
    print "cmd>>", cmd
    os.system(cmd)

    # Create constraints file (smt2 format)
    print "abc_output_path", abc_output_path
    Z3_input = Netlist_to_Z3_latency_nor2.netlist_to_z3(abc_output_path)
    print Z3_input
    # Run Z3
    cmd = '%s -smt2 %s > %s' % (Z3_path, Z3_input, output_path)
    print "cmd>>", cmd
    os.system(cmd)

    # Clean files
    if bool(args.clean):
        os.remove(abc_script_path)
        os.remove(abc_output_path)
        os.remove(Z3_input)
        print "Cleaning temporary files"


if __name__ == "__main__":
    main()
