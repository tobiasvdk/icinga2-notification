# icinga2-notification
notification script or Icinga 2


Use the following NotificationCommands:

    object NotificationCommand "service-mail-notification" {
        import "plugin-notification-command"
    
        command = [ SysconfDir + "/icinga2/scripts/pb-mail-notification.py",
            "-s", FromEmail,
            "-r", "$user.email$",
            "-t", "Service" ]
    
        env = {
            "NOTIFICATIONTYPE" = "$notification.type$"
            "SERVICENAME" = "$service.name$"
            "SERVICEDISPLAYNAME" = "$service.display_name$"
            "HOSTNAME" = "$host.name$"
            "HOSTADDRESS" = "$address$"
            "HOSTDISPLAYNAME" = "$host.display_name$"
            "SERVICESTATE" = "$service.state$"
            "SERVICESTATETYPE" = "$service.state_type$"
            "SERVICEDURATION" = "$service.duration_sec$"
            "SERVICEPERFDATA" = "$service.perfdata$"
            "LASTCHECK" = "$service.last_check$"
            "LASTSTATE" = "$service.last_state$"
            "LASTSTATETYPE" = "$service.last_state_type$"
            "SERVICEOUTPUT" = "$service.output$"
            "NOTIFICATIONAUTHORNAME" = "$notification.author$"
            "NOTIFICATIONCOMMENT" = "$notification.comment$"
        }
    }
    
    object NotificationCommand "host-mail-notification" {
        import "plugin-notification-command"
    
        command = [ SysconfDir + "/icinga2/scripts/pb-mail-notification.py",
            "-s", FromEmail,
            "-r", "$user.email$",
            "-t", "Host" ]
    
        env = {
            "NOTIFICATIONTYPE" = "$notification.type$"
            "HOSTNAME" = "$host.name$"
            "HOSTDISPLAYNAME" = "$host.display_name$"
            "HOSTADDRESS" = "$address$"
            "HOSTSTATE" = "$host.state$"
            "HOSTSTATETYPE" = "$host.state_type$"
            "HOSTDURATION" = "$host.duration_sec$"
            "HOSTPERFDATA" = "$host.perfdata$"
            "LASTCHECK" = "$host.last_check$"
            "LASTSTATE" = "$host.last_state$"
            "LASTSTATETYPE" = "$host.last_state_type$"
            "HOSTOUTPUT" = "$host.output$"
            "NOTIFICATIONAUTHORNAME" = "$notification.author$"
            "NOTIFICATIONCOMMENT" = "$notification.comment$"
        }
    }

