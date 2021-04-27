#!/usr/bin/env python3

import boto3
import sys
import time
import datetime
import html

if len(sys.argv) < 2:
    print("Need a prefix filter, and/or max hour ago (default 3h ago)")
    sys.exit(1)

prefix = sys.argv[1]

hours = 3
if len(sys.argv) > 2:
    hours = int(sys.argv[2])

time_ago = hours * 60 * 60 * 1000
min_time = int(time.time() * 1000 - time_ago)

logs = boto3.client('logs')

groups = logs.describe_log_groups(logGroupNamePrefix=prefix)['logGroups']
groups += logs.describe_log_groups(logGroupNamePrefix='/aws/lambda/' + prefix)['logGroups']
groups += logs.describe_log_groups(logGroupNamePrefix='/aws/rds/cluster/' + prefix)['logGroups']

print(f'Found {len(groups)} groups')

log_group_streams = []
for group in groups:
    print(f"### {group['logGroupName']} ###")
    log_streams = \
        logs.describe_log_streams(logGroupName=group['logGroupName'], orderBy='LastEventTime', descending=True,
                                  limit=1)[
            'logStreams']
    for log_stream in log_streams:
        if 'lastEventTimestamp' in log_stream and log_stream['lastEventTimestamp'] < min_time:
            continue
        log_group_streams.append([group['logGroupName'], log_stream['logStreamName']])
        break

print(f'Found {len(log_group_streams)} streams')

events = []
cpt = 0
for g_s in log_group_streams:
    cpt += 1
    print(f'{cpt}/{len(log_group_streams)}')
    tmp_events = logs.filter_log_events(logGroupName=g_s[0], logStreamNames=[g_s[1]], startTime=min_time, limit=200)[
        'events']
    for event in tmp_events:
        events.append([g_s[0], event['timestamp'], event['message']])

print(f'Found {len(events)} events')

sorted_events = sorted(events, key=lambda tup: tup[1], reverse=True)

f = open('logs.html', 'w')
f.write("""
	<html><header>
		<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/jquery.dataTables.css">
		<script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.js"></script>
		<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.js"></script>
	</header><body><table id="logs"><thead><tr><th>LogGroup</th><th>Timestamp</th><th>Message</th></tr></thead><tbody>
	""")

for event in sorted_events:
    ts = datetime.datetime.fromtimestamp(event[1] / 1000.0)
    f.write(f"<tr><td>{html.escape(event[0])}</td><td>{ts}</td><td>{html.escape(event[2])}</td></tr>")

f.write("""</tbody></table>
	<script>
		$(document).ready(function() {
		    $('#logs').DataTable({"pageLength": 200, "order": [[ 1, 'desc' ]]});
		});
	</script>
	</body></html>""")
f.close();
