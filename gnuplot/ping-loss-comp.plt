# Multiplot
set terminal png
set output "OUTPUT_MIN_MAX_AVG_COMP_FILENAME()"
set datafile separator ","
set grid
set timefmt "%Y/%m/%d %H:%M:%S"
set xtics 8 rotate by 90
set mxtics 8
set lmargin 10
set rmargin 2
set xdata time
set xlabel "Time" offset 0,-1
set multiplot

# Loss
set size 1,0.5
set origin 0.0,0.0
set ylabel "Packet Loss (%)"
set format x "%d/%m %H:%M:%S"
plot "INPUT_FILENAME()" using 1:5 with lines title "Loss"

# Min, Max & Avg
set origin 0.0,0.5
set size 1,0.5
unset xlabel
set format x ""
set ylabel "Ping Time (ms)"

plot "INPUT_FILENAME()" using 1:2 with lines title "Min", \
     "INPUT_FILENAME()" using 1:3 with lines title "Max", \
     "INPUT_FILENAME()" using 1:4 with lines title "Avg"

