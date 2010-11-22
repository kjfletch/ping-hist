from subprocess import Popen, PIPE
import sys, getopt, os, shlex

input_files = []

def main():
    parse_opts(sys.argv[1:])

    for input_file in input_files:
        if not os.path.isfile(input_file):
            print 'Error: file "%s" does not exist.' % (input_file)
            sys.exit(-1)
        
        valid, data, lowestping, highestping, lowestloss, highestloss = scan_data(input_file)

        if not valid:
            print 'Warning: file "%s" has invalid data.' % (input_file)
            continue

        if len(data) <= 1:
            print 'Warning: not enough data in file "%s" to plot.' % (input_file)
            continue

        base, ext = os.path.splitext(input_file)
        output_file = base + '.png'

        plot_loss = highestloss != lowestloss

        plot_data = get_plot_data(input_file, output_file, plot_loss)
        plot_cmd = shlex.split('gnuplot')
        plot = Popen(plot_cmd, stdin=PIPE)
        plot.communicate(plot_data)

def parse_opts(argv):
    """Parse command line options and store values in global vars."""

    global input_files

    opts, input_files = getopt.getopt(argv, 'h', ['help'])

    for o, a in opts:
        if o in ('--help', '-h'):
            usage(2)

        print 'Unknown argument: %s' % (o)
        usage(2)
        
    if len(input_files) == 0:
        print 'No input files specified.'
        usage(2)

def usage(retcode=None):
    print """
%s [options] <input-file> [input-file ...]
""" % (sys.argv[0])

    if retcode != None:
        sys.exit(retcode)

def scan_data(input_file):
    data = []
    valid = True
    lowping = None
    highping = None
    lowloss = None
    highloss = None

    f = open(input_file, 'r')

    for line in f:
        linesplit = line.strip().split(',')
        linesplit = [x for x in linesplit if x != '']

        if len(linesplit) != 5:
            valid = False
            break

        data.append(linesplit)

        try:
            date,pmin,pmax,pavg,ploss = linesplit
            pmin, pmax, pavg, ploss = [float(x) for x in (pmin, pmax, pavg, ploss)]

            if lowping == None or pmin < lowping:
                lowping = pmin
            if highping == None or pmax > highping:
                highping = pmax
            if lowloss == None or ploss < lowloss:
                lowloss = ploss
            if highloss == None or ploss > highloss:
                highloss = ploss
        except:
            valid = False
            break
        
    f.close()
    valid = valid and lowping != None and highping != None and  lowloss != None and highloss != None
    return valid, data, lowping, highping, lowloss, highloss

def get_plot_data(input_filename, output_filename, plot_loss=True):
    if plot_loss:
        data = plot_data_raw
    else:
        data = plot_data_no_loss_raw

    data = data.replace('__OUTPUT_FILENAME__', output_filename)
    data = data.replace('__INPUT_FILENAME__', input_filename)

    return data

plot_data_raw = """
# Multiplot
set terminal png
set output "__OUTPUT_FILENAME__"
set datafile separator ","
set grid
set timefmt "%Y/%m/%d %H:%M:%S"
set xtics rotate by 90
set lmargin 10
set rmargin 2
set xdata time
set xlabel "Time" offset 0,-1
set multiplot

# Loss
set origin 0.0,0.0
set size 1,0.5
set ylabel "Packet Loss (%)"
set format x "%d/%m %H:%M:%S"
plot "__INPUT_FILENAME__" using 1:5 with lines title "Loss"

# Min, Max & Avg
set origin 0.0,0.5
set size 1,0.5
unset xlabel
set format x ""
set ylabel "Ping Time (ms)"

plot "__INPUT_FILENAME__" using 1:3 with lines title "Max", \\
     "__INPUT_FILENAME__" using 1:4 with lines title "Avg", \\
     "__INPUT_FILENAME__" using 1:2 with lines title "Min"
"""

plot_data_no_loss_raw = """
set terminal png
set output "__OUTPUT_FILENAME__"
set datafile separator ","
set grid
set timefmt "%Y/%m/%d %H:%M:%S"
set xtics rotate by 90
set xdata time
set xlabel "Time" offset 0,-1
set format x "%d/%m %H:%M:%S"

# Min, Max & Avg
set ylabel "Ping Time (ms)"

plot "__INPUT_FILENAME__" using 1:3 with lines title "Max", \\
     "__INPUT_FILENAME__" using 1:4 with lines title "Avg", \\
     "__INPUT_FILENAME__" using 1:2 with lines title "Min"
"""

if __name__ == '__main__':
    main()
