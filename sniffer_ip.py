#!/usr/bin/python
#coding=utf-8

import socket
from os import system

system('title ip sniffer')
system('color 2')

# the public network interface
HOST = socket.gethostbyname(socket.gethostname())

# create a raw socket and bind it to the public interface
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
s.bind((HOST, 0))

# Include IP headers
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# receive all packages
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

count = 0
# receive a package
while 1:
	print "============start========================"
	packet = s.recvfrom(65565)
	if packet <> "":
	    count += 1
	print count
	packet = packet[0]
	ip_header = packet[0:20]
	print "raw data:%s"%ip_header
	version = (int(ord(ip_header[0])) & 0xF0) >>4
	print "version:%s"%version
	ihl = (int(ord(ip_header[0])) & 0x0F)  << 2   #IHL
	print "ip header length:%s Bytes."%ihl
	serviceType = hex(int(ord(ip_header[1])))
	print  "Type of Service:%s"%serviceType
	totalLen = (int(ord(ip_header[2])<<8))+(int(ord(ip_header[3])))
	print "total lenth:%s Bytes."%totalLen
	Identification = (int( ord(ip_header[4])) >> 8) + (int( ord(ip_header[5])))
	print "Identification:%s"%Identification
	flags = (int(ord(ip_header[6])) & 0xE0) >> 5
	print "flags:%s"%flags
	fragOff = ((int(ord(ip_header[6])) &0x1F) <<8) +  int(ord(ip_header[7]))
	print "fragOff:%s"%fragOff
	ttl = int(ord(ip_header[8]))
	print "ttl:%s"%ttl
	protocol = int(ord(ip_header[9]))
	print "protocol:%s"%protocol
	checkSum = int(ord(ip_header[10])<<8)+int(ord(ip_header[11]))
	print "checkSum :%s"%checkSum
	srcaddr = "%d.%d.%d.%d" % (int(ord(packet[12])),int(ord(packet[13])),int(ord(packet[14])), int(ord(packet[15])))
	print srcaddr
	dstaddr = "%d.%d.%d.%d" % (int(ord(packet[16])),int(ord(packet[17])),int(ord(packet[18])), int(ord(packet[19])))
	print dstaddr


# disabled promiscuous mode
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


