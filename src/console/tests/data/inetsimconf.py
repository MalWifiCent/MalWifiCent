#!/usr/bin/python3

options = {
    "#service_bind_address": "10.10.10.2",
    "#dns_default_ip": "10.10.10.2",
    "start_service": [
        "dns",
        "http",
        "https",
        "smtp",
        "smtps",
        "pop3",
        "pop3s",
        "ftp",
        "ftps",
        "tftp",
        "irc",
        "ntp",
        "finger",
        "ident",
        "syslog",
        "time_tcp",
        "time_udp",
        "daytime_tcp",
        "daytime_udp",
        "echo_tcp",
        "echo_udp",
        "discard_tcp",
        "discard_udp",
        "quotd_tcp",
        "quotd_udp",
        "chargen_tcp",
        "chargen_udp",
        "dummy_tcp",
        "dummy_udp"
    ],
    "http_fakefile": [
        "txt	sample.txt	text/plain",
        "htm	sample.html	text/html",
        "html	sample.html	text/html",
        "php	sample.html	text/html",
        "gif	sample.gif	image/gif",
        "jpg	sample.jpg	image/jpeg",
        "jpeg	sample.jpg	image/jpeg",
        "png	sample.png	image/png",
        "bmp	sample.bmp	image/x-ms-bmp",
        "ico	favicon.ico	image/x-icon",
        "exe	sample_gui.exe	x-msdos-program",
        "com	sample_gui.exe	x-msdos-program"
    ],
    "https_fakefile": [
    	"txt	sample.txt	text/plain",
        "htm	sample.html	text/html",
        "html	sample.html	text/html",
        "php	sample.html	text/html",
        "gif	sample.gif	image/gif",
        "jpg	sample.jpg	image/jpeg",
        "jpeg	sample.jpg	image/jpeg",
        "png	sample.png	image/png",
        "bmp	sample.bmp	image/x-ms-bmp",
        "ico	favicon.ico	image/x-icon",
        "exe	sample_gui.exe	x-msdos-program",
        "com	sample_gui.exe	x-msdos-program"
    ],
    "smtp_service_extension": [
		"VRFY",
		"EXPN",
		"HELP",
		"8BITMIME",
		"SIZE 102400000",
		"ENHANCEDSTATUSCODES",
		"AUTH PLAIN LOGIN ANONYMOUS CRAM-MD5 CRAM-SHA1",
		"DSN",
		"ETRN",
		"STARTTLS"
    ],
    "smtps_service_extension": [
		"VRFY",
		"EXPN",
		"HELP",
		"8BITMIME",
		"SIZE 102400000",
		"ENHANCEDSTATUSCODES",
		"AUTH PLAIN LOGIN ANONYMOUS CRAM-MD5 CRAM-SHA1",
		"DSN",
		"ETRN"
    ],
    "pop3_capability": [
        "TOP",
		"USER",
		"SASL PLAIN LOGIN ANONYMOUS CRAM-MD5 CRAM-SHA1",
		"UIDL",
		"IMPLEMENTATION \"INetSim POP3 server\"",
		"STLS"
    ],
    "pop3s_capability": [
        "TOP",
    	"USER",
    	"SASL PLAIN LOGIN ANONYMOUS CRAM-MD5 CRAM-SHA1",
    	"UIDL",
    	"IMPLEMENTATION \"INetSim POP3s server\""
    ],
    "tftp_option": [
        "BLKSIZE 512 65464",
		"TIMEOUT 5 60",
		"TSIZE 10485760"
    ]
}