#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <errno.h>
#include <net/if.h>

#define PORT 80
#define TIMEOUT_SEC 1

// Common CCTV HTTP headers or server strings
const char *cctv_signatures[] = {
    "Dahua", "Hikvision", "IP Camera", "Surveillance", "Axis", "Vivotek", "Provision", "Uniview"
};
#define SIGNATURES_COUNT (sizeof(cctv_signatures)/sizeof(cctv_signatures[0]))

// Simple HTTP GET request
const char *http_get = "GET / HTTP/1.0\r\n\r\n";

// Scan a single IP for CCTV signature
int scan_ip(const char *ip) {
    struct sockaddr_in addr;
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return 0;

    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    // Set timeout
    struct timeval timeout;
    timeout.tv_sec = TIMEOUT_SEC;
    timeout.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(sock);
        return 0;
    }

    send(sock, http_get, strlen(http_get), 0);

    char buffer[1024];
    int len = recv(sock, buffer, sizeof(buffer)-1, 0);
    close(sock);

    if (len <= 0) return 0;
    buffer[len] = '\0';

    for (int i = 0; i < SIGNATURES_COUNT; ++i) {
        if (strstr(buffer, cctv_signatures[i])) {
            return 1;
        }
    }
    return 0;
}

// Get local IP and subnet mask
int get_local_ip(char *ip, char *mask) {
    struct ifaddrs *ifaddr, *ifa;
    if (getifaddrs(&ifaddr) == -1) return -1;

    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr &&
            ifa->ifa_addr->sa_family == AF_INET &&
            !(ifa->ifa_flags & IFF_LOOPBACK)) {
            struct sockaddr_in *sa = (struct sockaddr_in *)ifa->ifa_addr;
            struct sockaddr_in *nm = (struct sockaddr_in *)ifa->ifa_netmask;
            strcpy(ip, inet_ntoa(sa->sin_addr));
            strcpy(mask, inet_ntoa(nm->sin_addr));
            freeifaddrs(ifaddr);
            return 0;
        }
    }
    freeifaddrs(ifaddr);
    return -1;
}

// Convert IP string to uint32
uint32_t ip_to_uint(const char *ip) {
    struct in_addr addr;
    inet_pton(AF_INET, ip, &addr);
    return ntohl(addr.s_addr);
}

// Convert uint32 to IP string
void uint_to_ip(uint32_t ip, char *buf) {
    struct in_addr addr;
    addr.s_addr = htonl(ip);
    strcpy(buf, inet_ntoa(addr));
}

int main() {
    char local_ip[INET_ADDRSTRLEN], netmask[INET_ADDRSTRLEN];
    if (get_local_ip(local_ip, netmask) != 0) {
        fprintf(stderr, "Could not get local IP\n");
        return 1;
    }

    uint32_t ip = ip_to_uint(local_ip);
    uint32_t mask = ip_to_uint(netmask);
    uint32_t network = ip & mask;
    uint32_t broadcast = network | (~mask);

    printf("Scanning network: %s/%s\n", local_ip, netmask);

    char scan_ip_str[INET_ADDRSTRLEN];
    for (uint32_t scan_ip_uint = network + 1; scan_ip_uint < broadcast; ++scan_ip_uint) {
        uint_to_ip(scan_ip_uint, scan_ip_str);
        if (scan_ip_uint == ip) continue; // skip own IP
        if (scan_ip(scan_ip_str)) {
            printf("CCTV Camera found at IP: %s\n", scan_ip_str);
        }
    }
    return 0;
}