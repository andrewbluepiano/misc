#!/bin/bash
# Author: Andrew Afonso
# Description: A tcp or udp port scanner for IP ranges using /dev/tcp and /dev/udp
#
# port_scanner	tcp/udp	start_ip	  stop_ip			  port
# port_scanner 	tcp 	  192.168.4.3	192.168.4.100	80
# $0			      $1		  $2			    $3				    $4

# Help message
usage_info() {
	echo "$1"
	echo "----- Usage Info -----"
	echo "Used to do a port scan for a tcp or udp port over a"
	echo "range of IP addresses using /dev/udp or /dev/tcp as"
	echo "appropriate. Broadcast address @ 255 will be excluded."
	echo ""
	echo "- Basic syntax:"
	echo "\$ ./port_scanner.sh [tcp/udp] start_ip end_ip port"
	echo ""
	echo "- Example:"
	echo "\$ ./port_scanner.sh tcp 192.168.1.1 192.168.1.100 80"
	echo "---------------------"
	echo ""
	exit
}

# Just for my sanity
done_found() {
	echo "Easter Egg!"
	exit
}

# Check that there are 4 command line parameters passed
if [ $# -ne 4 ]; then
	usage_info "Invalid arguement count"
fi

# Set the path to the dev device to use for port scanning
if [ $1 = "tcp" ]; then
	path="/dev/tcp"
elif [ $1 = "udp" ]; then
	path="/dev/udp"
else
	usage_info "Invalid protocol selected ('tcp' or 'udp' expected)"
fi

# Split up IP's into octet arrays
IFS='.' read -ra srt_split <<< "$2"
IFS='.' read -ra end_split <<< "$3"

# Set to 0 when we know the IP's are good
keep_checking=1

# IP range checks
for a in {0..3}; do
	# Check for over 255
	if [ ${srt_split[a]} -gt 255 ] || [ ${end_split[a]} -gt 255 ]; then
		echo "Invalid IP range: Octet greater than 255"
		exit
	fi
	
	# Check for under 0
	if [ ${srt_split[a]} -lt 0 ] || [ ${end_split[a]} -lt 0 ]; then
		echo "Invalid IP range: Octet less than 0"
		exit
	fi
	
	# Checks for 1st IP < 2nd IP
	if [ $keep_checking = 1 ]; then
		if [ ${srt_split[a]} -gt ${end_split[a]} ]; then
			echo "Invalid IP range: Start IP greater than end"
			exit
		fi
		# If an octet is one higher in the end IP then the start IP, then start < end
		if [ ${end_split[a]} -gt ${srt_split[a]} ]; then
			keep_checking=0
		fi
	fi
done

# Port checking
if [ $4 -gt 65535 ]; then
	echo "Invalid Port: $4 greater than 65535"
	exit
elif [ $4 -lt 0 ]; then
	echo "Invalid Port: $4 less than 0"
	exit
else
	port=$4
fi

# The main loop.
while [ "${srt_split[*]}" != "${end_split[*]}" ]; do
	
	# Combine IP array to single string
	ip=$(printf ".%s" "${srt_split[@]}")
	ip=${ip:1}

	# Send to /dev/null to supress expected error messages related to timeout
	echo "nothing" >$path/${ip}/${port} & sleep 1; kill $! 2> /dev/null
	exit_code=$?
	if [ $exit_code = 1 ]; then
		echo >$path/${ip}/${port} &&
		echo "${ip}:${port} is open" ||
		echo "${ip}:${port} is closed"
	elif [ $exit_code = 0 ]; then
		echo "${ip}:${port} didn't respond"
	fi
	
	# IP incrementer
	if [ ${srt_split[3]} = 254 ]; then 	# If fourth (last) octet is 254
		# Increment fourth (last) octet to 255
		srt_split[3]=$((srt_split[3]+1))
		if [ "${srt_split[*]}" == "${end_split[*]}" ]; then
			done_found
		elif [ ${srt_split[2]} = 254 ]; then # If the address with 255 is not the end address and the third octet is 254
			# Increment third octet to 255
			srt_split[2]=$((srt_split[2]+1))
			if [ "${srt_split[*]}" == "${end_split[*]}" ]; then
				done_found
			elif [ ${srt_split[1]} = 254 ]; then # If second octet is 254
				# Increment second octet to 255
				srt_split[1]=$((srt_split[1]+1))
				if [ "${srt_split[*]}" == "${end_split[*]}" ]; then
					done_found
				elif [ ${srt_split[0]} = 254 ]; then # If first octet is 254
					# Increment first octet to 255
					srt_split[0]=$((srt_split[0]+1))
					if [ "${srt_split[*]}" == "${end_split[*]}" ]; then
						# End ip was 255.255.255.255
						done_found
					else
						# Exit. Fail. Because this means we are at 255.255.255.255
						exit
					fi
				else
					# Reset second, third, and fourth octet
					srt_split[1]=0
					srt_split[2]=0
					srt_split[3]=0
					
					# Increment first octet for carried 1
					srt_split[0]=$((srt_split[0]+1))
				fi
			else
				# Reset third and fourth octet
				srt_split[2]=0
				srt_split[3]=0
				
				# Increment second octet for carried 1
				srt_split[1]=$((srt_split[1]+1))
			fi
		else
			# Reset fourth octet
			srt_split[3]=0
			
			# Increment third octet for carried 1
			srt_split[2]=$((srt_split[2]+1))
		fi
	else
		# When just incrementing the last octet by 1 and last octet isnt 254
		srt_split[3]=$((srt_split[3]+1))
	fi
	# End IP incrementer
	
done 2> /dev/null  # To supress expected error messages related to timeout

exit
