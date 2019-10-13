
#ifndef CONN_H
#define CONN_H


#define MEMCACHED_PORT 11211

#include <net/if.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include "config.h"

#define QUEUE_SIZE 1000000
#define INCR_FIX_QUEUE_SIZE 1000

struct worker;

struct conn {
  int sock;
  int port;	
  int uid;
  int protocol;

  int head;
  int tail;
  int n_requests;

  int incr_fix_queue_tail;
  int incr_fix_queue_head;


  //Circular queue
  struct request* request_queue[QUEUE_SIZE];
  int current_request_id;

  struct request* incr_fix_queue[INCR_FIX_QUEUE_SIZE];

  //Observing-only reference
  struct worker *worker;
};

struct conn* createConnection(const char* ip_address, int port, int protocol, int naggles);
int openTcpSocket(const char* ipAddress, int port);
int openUdpSocket(const char* ipAddress, int port);

#endif
