for f in *.csv; do
    FILENAME=$f
    FILEBASE=`basename ${FILENAME} .csv`
    OUTDIR=plot/
    PING_OUTPUT=${OUTDIR}${FILEBASE}.png
    LOSS_OUTPUT=${OUTDIR}${FILEBASE}_loss.png
    COMP_OUTPUT=${OUTDIR}${FILEBASE}_comp.png

    echo $FILENAME
    m4 -DINPUT_FILENAME="${FILENAME}" \
       -DOUTPUT_MIN_MAX_AVG_FILENAME="${PING_OUTPUT}" \
       -DOUTPUT_LOSS_FILENAME="${LOSS_OUTPUT}" \
       gnuplot/ping-loss.plt | gnuplot

    m4 -DINPUT_FILENAME="${FILENAME}" \
       -DOUTPUT_MIN_MAX_AVG_COMP_FILENAME="${COMP_OUTPUT}" \
       gnuplot/ping-loss-comp.plt | gnuplot
done;

