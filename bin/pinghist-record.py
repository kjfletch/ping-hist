from subprocess import Popen, PIPE
from datetime import datetime
from datetime import timedelta, datetime
from time import sleep
import getopt, sys, re, shlex

## Setup the Defaults
targets = []
packet_count = 30
repeat_end = 1
repeat_end_date = None
repeat_loop = False
repeat_freq = timedelta(0,0,0,0,15)
windows_ping = False # TODO: need to turn this to True programatically
span_re = re.compile('^(\d+):(\d+):(\d+)$', re.IGNORECASE)
hms_re = re.compile('^(\d+)([hms])$', re.IGNORECASE)
endnum_re = re.compile('^(\d+)$')

def main():
    """Ping targets, loop if specified on command line."""
    global repeat_end

    parse_opts(sys.argv[1:])

    while True:
      start_time = datetime.now()

      if repeat_end_date and start_time > repeat_end_date and not repeat_loop:
        # We've hit the end of the loop task through the end time/date
        # being specified.
        break

      for target in targets:
          doping(target)

      if not repeat_end_date and not repeat_loop:
        repeat_end -= 1
        if repeat_end <= 0:
          # We've hit the end of the loop task through defined number of
          # iterations exceeded.
          break

      st = repeat_freq - (start_time - datetime.now())
      st = (st.microseconds + (st.seconds + st.days * 24 * 3600) * 10**6) / 10**6
      sleep(st)

def timedelta_from_argv(argv):
    """Return a timedelta from string in various formats."""
    thetime = None

    match = span_re.match(argv)
    if match:
      thetime = timedelta(0,int(match.group(3)), 0, 0, int(match.group(2)), int(match.group(1)))
      return thetime

    match = hms_re.match(argv)
    if match:
      number = int(match.group(1))
      letter = match.group(2)
      if letter is 's':
        thetime = timedelta(0, number)
      elif letter is 'm':
        thetime = timedelta(0, 0, 0, 0, number)
      elif letter is 'h':
        thetime = timedelta(0, 0, 0, 0, 0, number)

    return thetime

def parse_opts(argv):
    """Parse command line options and store values in global vars."""
    global targets, packet_count, repeat_end, repeat_end_date, repeat_loop, repeat_freq

    opts, targets = getopt.getopt(argv, 'he:f:c:', ['help', 'every=', 'for=', 'packet-count='])

    for o, a in opts:
      if o in ('-h', '--help'):
          usage(2)
          continue

      if o in ('-e', '--every'):
        freqdelta = timedelta_from_argv(a)
        if freqdelta:
          repeat_freq = freqdelta
          continue

        print 'Bad frequency setting: %s' % (a)
        usage(2)

      if o in ('-f', '--for'):
        if a == 'loop' or a == 'ever':
          repeat_loop = True
          continue

        match = endnum_re.match(a)
        if match:
          repeat_end = int(match.group(1))
          continue

        enddelta = timedelta_from_argv(a)
        if enddelta:
          repeat_end_date = datetime.now() + enddelta
          continue

        print 'Bad end setting: %s' % (a)
        usage(2)

      if o in ('-c', '--packet-count'):
        if re.match('^\d+$', a):
          packet_count = int(a)
          continue

        print 'Bad packet count: %s' % (a)
        usage(2)

      ## If we haven't broken out the loop we have a bad arg.
      print 'Unknown argument: %s' % (o)
      usage(2)

    if len(targets) == 0:
      print 'No targets defined.'
      usage(2)

def usage(retcode=None):
    """Print the usage of the application. Exit with given return code
    if specified."""
    print """
%s [options] <target> [target ...]
  options:
    -e <delay>
    --every=<delay>
      Pause for <delay> between ping loop cycles. Delay can be specified
      in one of the following ways:
       - timespan in format HH:MM:SS, example: 01:45:00 for an hour and 45 minutes.
       - hours in the format <n>h, example: 11h for 11 hours.
       - minutes in the format <n>m, example: 10m for 10 minutes.
       - seconds in the format <n>s, example: 90s for 90 seconds. 

      Default: 15 minutes (00:15:00, 15m, etc).

    -f <duration>
    --for=<duration>
      Duration to continue the ping loop. This can be specified by:
       - The number of cycles <n> to loop for.
       - The keyword 'loop' to loop forever.
       - A timespan specified in the following ways:
         * timespan in format HH:MM:SS, example: 01:45:00 for an hour and 45 minutes.
         * hours in the format <n>h, example: 11h for 11 hours.
         * minutes in the format <n>m, example: 10m for 10 minutes.
         * seconds in the format <n>s, example: 90s for 90 seconds.

      Default: 1 (1 iteration of the ping loop).

    -c <count>
    --packet-count=<count>
      Number of packets to send in each ping.

      Default: 30

    -h
    --help
      Display this help.

    target (targets)
      Targets to ping, example: www.bbc.co.uk.
""" % (sys.argv[0])
    
    if retcode != None:
        sys.exit(retcode)

def target_uri(target, thetime):
    """Create a filesystem safe URI from a given string."""
    time_string = thetime.strftime('%Y-%m-%d')
    return '%s-ping-%s' % (time_string, re.sub('[^a-zA-Z0-9]', '_', target))

def doping(target):
    """Ping a single target and store the results in files."""
    ping_time = datetime.now()
    uri = target_uri(target, ping_time)
    ping_time_string = ping_time.strftime('%Y/%m/%d %H:%M:%S')
    raw_file = uri + '.txt'
    csv_file = uri + '.csv'

    ploss = 100
    pmin, pavg, pmax = 0
    
    if windows_ping:
        pass # TODO: Need to write windows implementation.
    else:
        ping_cmd = shlex.split('ping %s -c %d' % (target, packet_count))
        print 'pinging with command: %s' % (' '.join(ping_cmd))
        ping = Popen(ping_cmd, stdout=PIPE)
        (content, stderr) = ping.communicate()
        match = re.search('\s([0-9.]+)% packet loss', content)
        ploss = match.group(1)
        match = re.search('min/avg/max/mdev = (.+?)/(.+?)/(.+?)/.+? ms', content)
        pmin, pavg, pmax = match.groups()

    raw = open(raw_file, 'a')
    raw.writelines('\n'.join([ping_time_string, content, '']))
    raw.close()

    csv = open(csv_file, 'a')
    csv.write(','.join([ping_time_string, pmin, pmax, pavg, ploss, '\n']))
    csv.close()

if __name__ == "__main__":
    main()
