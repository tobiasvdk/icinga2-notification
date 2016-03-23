#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
An email notification script for Icinga 2
'''

import argparse
from datetime import datetime, timedelta
from os import environ, path
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib

__author__ = 'Tobias von der Krone'
__copyright__ = ''
__license__ = 'GPL 3'
__version__ = '0.1.0'
__maintainer__ = 'Tobias von der Krone'
__email__ = 'tobias@vonderkrone.info'
__status__ = 'Development'

SMTP_HOST = 'localhost'
ICINGAWEB2_URL = 'https://icinga2/icingaweb2'

def perfdata_table(perfdata):
    '''
    generate html table for performance data
    '''

    html = '<table><thead><tr>'
    html += '<td>Metric</td><td>Value</td><td>Warning</td><td>Critical</td><td>Minimum</td><td>Maximum</td>'
    html += '</tr></thead><tbody>'
    if perfdata:
        result = re.findall(r'\s?(.+?=\S+)', perfdata)
        for data in result:
            metric, perf = data.split('=')
            values = perf.split(';')
            uom_match = re.search(r'[^0-9]*$', values[0])
            if uom_match:
                uom = uom_match.group(0)
            else:
                uom = None
            # the following values are optional
            try:
                warn = values[1]
            except IndexError:
                warn = ''
            try:
                crit = values[2]
            except IndexError:
                crit = ''
            try:
                minimum = values[3]
            except IndexError:
                minimum = ''
            try:
                maximum = values[4]
            except IndexError:
                maximum = ''
            # create html row
            html += '<tr><td>{metric} {uom}</td><td>{val}</td><td>{warn}</td><td>{crit}</td><td>{minimum}</td><td>{maximum}</td></tr>'.format(
                metric=metric.replace('"', '').replace("'", ''),
                uom='({})'.format(uom) if uom else '',
                val=values[0],
                warn=warn,
                crit=crit,
                minimum=minimum,
                maximum=maximum,
            )

    html += '</tbody></table>'

    return html

def main():
    '''
    main function
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', '--object-type',
        help='object type, either "Service" or "Host"',
        dest='object_type'
    )
    parser.add_argument(
        '-s', '--sender',
        help='email of the sender',
        dest='sender'
    )
    parser.add_argument(
        '-r', '--recipient',
        help='email of the recipient',
        dest='recipient'
    )
    args = parser.parse_args()

    notification_type = environ.get('NOTIFICATIONTYPE')
    host_name = environ.get('HOSTNAME')
    host_address = environ.get('HOSTADDRESS')
    last_check_datetime = datetime.utcfromtimestamp(float(environ.get('LASTCHECK')))
    last_check = last_check_datetime.strftime('%F %H:%M:%S %Z')
    last_state = environ.get('LASTSTATE')
    last_state_type = environ.get('LASTSTATETYPE')
    subject = '{} - {}'.format(notification_type, host_name)
    if notification_type == 'ACKNOWLEDGEMENT':
        comment = environ.get('NOTIFICATIONCOMMENT')
        author = environ.get('NOTIFICATIONAUTHORNAME')
    if 'SERVICENAME' in environ:
        service_name = environ.get('SERVICENAME')
        service_displayname = environ.get('SERVICEDISPLAYNAME')
        state = environ.get('SERVICESTATE')
        state_type = environ.get('SERVICESTATETYPE')
        output = environ.get('SERVICEOUTPUT')
        duration = environ.get('SERVICEDURATION')
        perfdata = environ.get('SERVICEPERFDATA')
        details_url = '{icingaweb2_url}/monitoring/service/show?host={hostname}&service={servicename}'.format(
            icingaweb2_url=ICINGAWEB2_URL,
            hostname=host_name,
            servicename=service_name
        )
        ack_url = '{icingaweb2_url}/monitoring/service/acknowledge-problem?host={hostname}&service={servicename}'.format(
            icingaweb2_url=ICINGAWEB2_URL,
            hostname=host_name,
            servicename=service_name
        )
        subject += '/{}'.format(service_displayname)
    else:
        state = environ.get('HOSTSTATE')
        state_type = environ.get('HOSTSTATETYPE')
        output = environ.get('HOSTOUTPUT')
        duration = environ.get('HOSTDURATION')
        perfdata = environ.get('HOSTPERFDATA')
        details_url = '{icingaweb2_url}/monitoring/host/show?host={hostname}'.format(
            icingaweb2_url=ICINGAWEB2_URL,
            hostname=host_name
        )
        ack_url = '{icingaweb2_url}/monitoring/host/acknowledge-problem?host={hostname}'.format(
            icingaweb2_url=ICINGAWEB2_URL,
            hostname=host_name
        )
    problem_time_datetime = datetime.utcnow() - timedelta(seconds=int(duration))
    problem_time = problem_time_datetime.strftime('%F %H:%M:%S %Z')
    duration = timedelta(seconds=int(duration))
    subject += ' is {}'.format(state)

    # start
    text = '''
***** Icinga 2 Notification *****

Notification Type: {notification_type}

Host:              {hostname} ({hostaddress})
'''.format(
        notification_type=notification_type,
        hostname=host_name,
        hostaddress=host_address)

    html = '''
<html>
<head>
<title>Icinga 2 Notification</title>
</head>
<body>
<h1><img src='cid:icinga2_logo' alt='Icinga 2'> Notification</h1>
<table>
<tr><td>Notification Type:</td><td>{notification_type}</td></tr>
<tr><td>&nbsp;</td><td></td></tr>
<tr><td>Host:</td><td>{hostname} ({hostaddress})</td></tr>
'''.format(
        notification_type=notification_type,
        hostname=host_name,
        hostaddress=host_address
    )

    if args.object_type == 'Service':
        text += '''
Service:           {}
'''.format(service_displayname)
        html += '''
<tr><td>Service:</td><td>{}</td></tr>
'''.format(service_displayname)

    text += '''
State:             {state} ({state_type})
Last State:        {last_state} ({last_state_type})
Check Output:      {output}
Performance Data:  {perfdata}

'''.format(
        state=state,
        state_type=state_type,
        last_state=last_state,
        last_state_type=last_state_type,
        output=output,
        perfdata=perfdata if perfdata else '-'
    )
    html += '''
<tr><td>State:</td><td>{state} ({state_type})</td></tr>
<tr><td>Last State:</td><td>{last_state} ({last_state_type})</td></tr>
<tr><td>Check Output:</td><td>{output}</td></tr>
<tr><td>Performance Data:</td><td>{perfdata}</td></tr>
<tr><td>&nbsp;</td><td></td></tr>
'''.format(
        state=state,
        state_type=state_type,
        last_state=last_state,
        last_state_type=last_state_type,
        output=output,
        perfdata=perfdata_table(perfdata) if perfdata else '-'
    )

    text += '''
Last Check:        {last_check}
Duration:          {duration} hours (since {problem_time})
'''.format(
        last_check=last_check,
        duration=str(duration),
        problem_time=problem_time
    )
    html += '''
<tr><td>Last Check:</td><td>{last_check}</td></tr>
<tr><td>Duration:</td><td>{duration} hours (since {problem_time})</td></tr>
'''.format(
        last_check=last_check,
        duration=str(duration),
        problem_time=problem_time
    )

    if notification_type == 'ACKNOWLEDGEMENT':
        text += '''
Comment:           {comment}
Author:            {author}
'''.format(
        comment=comment,
        author=author
    )
        html += '''
<tr><td>Comment:</td><td>{comment}</td></tr>
<tr><td>Author:</td><td>{author}</td></tr>
'''.format(
        comment=comment,
        author=author
    )

    text += '''
Show Details:      {details_url}
'''.format(details_url=details_url)

    html += '''
<tr><td>&nbsp;</td><td></td></tr>
<tr><td>Actions:</td><td><a href="{details_url}">Show Details</a>'''.format(
        details_url=details_url
    )

    if notification_type not in ['RECOVERY', 'DOWNTIME', 'FLAPPINGSTART', 'FLAPPINGEND']:
        text += '''
Acknowledge:       {ack_url}
'''.format(ack_url=ack_url)
        html += ', <a href="{ack_url}">Acknowledge</a>'.format(
        ack_url=ack_url
    )

    html += '''</td></tr>
</table>
</body>
</html>
'''

    # read log data
    img_filename = '/usr/share/icingaweb2/public/img/logo_icinga.png'
    img_data = open(img_filename, 'rb').read()
    # create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = args.sender
    msg['To'] = args.recipient
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    mime_img = MIMEImage(img_data, name=path.basename(img_filename))
    mime_img.add_header('Content-ID', '<icinga2_logo>')
    msg.attach(mime_img)

    # send email for testing
    s = smtplib.SMTP(SMTP_HOST)
    s.sendmail(args.sender, args.recipient, msg.as_string())
    s.quit()

if __name__ == '__main__':
    main()
