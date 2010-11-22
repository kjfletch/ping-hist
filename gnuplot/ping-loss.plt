set terminal png
set datafile separator ","
set grid
set xdata time
set timefmt "%Y/%m/%d %H:%M:%S"
set format x "%d/%m %H:%M:%S"

# Global
set xtics 8 rotate by 90
set xlabel "Time" offset 0,-1

# Min, Max & Avg
set output "OUTPUT_MIN_MAX_AVG_FILENAME()"
set title "Ping (Min, Max, Avg)"
set ylabel "Ping Time (ms)"

plot "INPUT_FILENAME()" using 1:2 with lines title "Min", \
     "INPUT_FILENAME()" using 1:3 with lines title "Max", \
     "INPUT_FILENAME()" using 1:4 with lines title "Avg"

# Loss
set output "OUTPUT_LOSS_FILENAME()"
set title "Packet Loss"
set ylabel "Packet Loss (%)"
plot "INPUT_FILENAME()" using 1:5 with lines title "Loss"