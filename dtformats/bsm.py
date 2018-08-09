# -*- coding: utf-8 -*-
"""Basic Security Module (BSM) event auditing files."""

from __future__ import unicode_literals

from dtformats import data_format
from dtformats import errors


class BSMEventAuditingFile(data_format.BinaryDataFile):
  """BSM event auditing file."""

  _DEFINITION_FILE = 'bsm.yaml'

  _EVENT_TYPES = {
      0: 'indir system call',
      1: 'exit(2)',
      2: 'fork(2)',
      3: 'open(2) - attr only',
      4: 'creat(2)',
      5: 'link(2)',
      6: 'unlink(2)',
      7: 'exec(2)',
      8: 'chdir(2)',
      9: 'mknod(2)',
      10: 'chmod(2)',
      11: 'chown(2)',
      12: 'umount(2) - old version',
      13: 'junk',
      14: 'access(2)',
      15: 'kill(2)',
      16: 'stat(2)',
      17: 'lstat(2)',
      18: 'acct(2)',
      19: 'mctl(2)',
      20: 'reboot(2)',
      21: 'symlink(2)',
      22: 'readlink(2)',
      23: 'execve(2)',
      24: 'chroot(2)',
      25: 'vfork(2)',
      26: 'setgroups(2)',
      27: 'setpgrp(2)',
      28: 'swapon(2)',
      29: 'sethostname(2)',
      30: 'fcntl(2)',
      31: 'setpriority(2)',
      32: 'connect(2)',
      33: 'accept(2)',
      34: 'bind(2)',
      35: 'setsockopt(2)',
      36: 'vtrace(2)',
      37: 'settimeofday(2)',
      38: 'fchown(2)',
      39: 'fchmod(2)',
      40: 'setreuid(2)',
      41: 'setregid(2)',
      42: 'rename(2)',
      43: 'truncate(2)',
      44: 'ftruncate(2)',
      45: 'flock(2)',
      46: 'shutdown(2)',
      47: 'mkdir(2)',
      48: 'rmdir(2)',
      49: 'utimes(2)',
      50: 'adjtime(2)',
      51: 'setrlimit(2)',
      52: 'killpg(2)',
      53: 'nfs_svc(2)',
      54: 'statfs(2)',
      55: 'fstatfs(2)',
      56: 'unmount(2)',
      57: 'async_daemon(2)',
      58: 'nfs_getfh(2)',
      59: 'setdomainname(2)',
      60: 'quotactl(2)',
      61: 'exportfs(2)',
      62: 'mount(2)',
      63: 'semsys(2)',
      64: 'msgsys(2)',
      65: 'shmsys(2)',
      66: 'bsmsys(2)',
      67: 'rfssys(2)',
      68: 'fchdir(2)',
      69: 'fchroot(2)',
      70: 'vpixsys(2)',
      71: 'pathconf(2)',
      72: 'open(2) - read',
      73: 'open(2) - read,creat',
      74: 'open(2) - read,trunc',
      75: 'open(2) - read,creat,trunc',
      76: 'open(2) - write',
      77: 'open(2) - write,creat',
      78: 'open(2) - write,trunc',
      79: 'open(2) - write,creat,trunc',
      80: 'open(2) - read,write',
      81: 'open(2) - read,write,creat',
      82: 'open(2) - read,write,trunc',
      83: 'open(2) - read,write,creat,trunc',
      84: 'msgctl(2) - illegal command',
      85: 'msgctl(2) - IPC_RMID command',
      86: 'msgctl(2) - IPC_SET command',
      87: 'msgctl(2) - IPC_STAT command',
      88: 'msgget(2)',
      89: 'msgrcv(2)',
      90: 'msgsnd(2)',
      91: 'shmctl(2) - illegal command',
      92: 'shmctl(2) - IPC_RMID command',
      93: 'shmctl(2) - IPC_SET command',
      94: 'shmctl(2) - IPC_STAT command',
      95: 'shmget(2)',
      96: 'shmat(2)',
      97: 'shmdt(2)',
      98: 'semctl(2) - illegal command',
      99: 'semctl(2) - IPC_RMID command',
      100: 'semctl(2) - IPC_SET command',
      101: 'semctl(2) - IPC_STAT command',
      102: 'semctl(2) - GETNCNT command',
      103: 'semctl(2) - GETPID command',
      104: 'semctl(2) - GETVAL command',
      105: 'semctl(2) - GETALL command',
      106: 'semctl(2) - GETZCNT command',
      107: 'semctl(2) - SETVAL command',
      108: 'semctl(2) - SETALL command',
      109: 'semget(2)',
      110: 'semop(2)',
      111: 'process dumped core',
      112: 'close(2)',
      113: 'system booted',
      114: 'async_daemon(2) exited',
      115: 'nfssvc(2) exited',
      128: 'writel(2)',
      129: 'writevl(2)',
      130: 'getauid(2)',
      131: 'setauid(2)',
      132: 'getaudit(2)',
      133: 'setaudit(2)',
      134: 'getuseraudit(2)',
      135: 'setuseraudit(2)',
      136: 'auditsvc(2)',
      137: 'audituser(2)',
      138: 'auditon(2)',
      139: 'auditon(2) - GETTERMID command',
      140: 'auditon(2) - SETTERMID command',
      141: 'auditon(2) - GPOLICY command',
      142: 'auditon(2) - SPOLICY command',
      143: 'auditon(2) - GESTATE command',
      144: 'auditon(2) - SESTATE command',
      145: 'auditon(2) - GQCTRL command',
      146: 'auditon(2) - SQCTRL command',
      147: 'getkernstate(2)',
      148: 'setkernstate(2)',
      149: 'getportaudit(2)',
      150: 'auditstat(2)',
      151: 'revoke(2)',
      152: 'Solaris AUE_MAC',
      153: 'enter prom',
      154: 'exit prom',
      155: 'Solaris AUE_IFLOAT',
      156: 'Solaris AUE_PFLOAT',
      157: 'Solaris AUE_UPRIV',
      158: 'ioctl(2)',
      173: 'one-sided session record',
      174: 'msggetl(2)',
      175: 'msgrcvl(2)',
      176: 'msgsndl(2)',
      177: 'semgetl(2)',
      178: 'shmgetl(2)',
      183: 'socket(2)',
      184: 'sendto(2)',
      185: 'pipe(2)',
      186: 'socketpair(2)',
      187: 'send(2)',
      188: 'sendmsg(2)',
      189: 'recv(2)',
      190: 'recvmsg(2)',
      191: 'recvfrom(2)',
      192: 'read(2)',
      193: 'getdents(2)',
      194: 'lseek(2)',
      195: 'write(2)',
      196: 'writev(2)',
      197: 'nfs server',
      198: 'readv(2)',
      199: 'Solaris old stat(2)',
      200: 'setuid(2)',
      201: 'old stime(2)',
      202: 'old utime(2)',
      203: 'old nice(2)',
      204: 'Solaris old setpgrp(2)',
      205: 'setgid(2)',
      206: 'readl(2)',
      207: 'readvl(2)',
      208: 'fstat(2)',
      209: 'dup2(2)',
      210: 'mmap(2)',
      211: 'audit(2)',
      212: 'Solaris priocntlsys(2)',
      213: 'munmap(2)',
      214: 'setegid(2)',
      215: 'seteuid(2)',
      216: 'putmsg(2)',
      217: 'getmsg(2)',
      218: 'putpmsg(2)',
      219: 'getpmsg(2)',
      220: 'audit system calls place holder',
      221: 'auditon(2) - get kernel mask',
      222: 'auditon(2) - set kernel mask',
      223: 'auditon(2) - get cwd',
      224: 'auditon(2) - get car',
      225: 'auditon(2) - get audit statistics',
      226: 'auditon(2) - reset audit statistics',
      227: 'auditon(2) - set mask per uid',
      228: 'auditon(2) - set mask per session ID',
      229: 'auditon(2) - get audit state',
      230: 'auditon(2) - set audit state',
      231: 'auditon(2) - get event class',
      232: 'auditon(2) - set event class',
      233: 'utssys(2) - fusers',
      234: 'statvfs(2)',
      235: 'xstat(2)',
      236: 'lxstat(2)',
      237: 'lchown(2)',
      238: 'memcntl(2)',
      239: 'sysinfo(2)',
      240: 'xmknod(2)',
      241: 'fork1(2)',
      242: 'modctl(2) system call place holder',
      243: 'modctl(2) - load module',
      244: 'modctl(2) - unload module',
      245: 'modctl(2) - configure module',
      246: 'modctl(2) - bind module',
      247: 'getmsg-accept',
      248: 'putmsg-connect',
      249: 'putmsg-send',
      250: 'getmsg-receive',
      251: 'acl(2) - SETACL comand',
      252: 'facl(2) - SETACL command',
      253: 'doorfs(2) - system call place holder',
      254: 'doorfs(2) - DOOR_CALL',
      255: 'doorfs(2) - DOOR_RETURN',
      256: 'doorfs(2) - DOOR_CREATE',
      257: 'doorfs(2) - DOOR_REVOKE',
      258: 'doorfs(2) - DOOR_INFO',
      259: 'doorfs(2) - DOOR_CRED',
      260: 'doorfs(2) - DOOR_BIND',
      261: 'doorfs(2) - DOOR_UNBIND',
      262: 'p_online(2)',
      263: 'processor_bind(2)',
      264: 'inst_sync(2)',
      265: 'configure socket',
      266: 'setaudit_addr(2)',
      267: 'getaudit_addr(2)',
      268: 'Solaris umount(2)',
      269: 'fsat(2) - place holder',
      270: 'openat(2) - read',
      271: 'openat(2) - read,creat',
      272: 'openat(2) - read,trunc',
      273: 'openat(2) - read,creat,trunc',
      274: 'openat(2) - write',
      275: 'openat(2) - write,creat',
      276: 'openat(2) - write,trunc',
      277: 'openat(2) - write,creat,trunc',
      278: 'openat(2) - read,write',
      279: 'openat(2) - read,write,create',
      280: 'openat(2) - read,write,trunc',
      281: 'openat(2) - read,write,creat,trunc',
      282: 'renameat(2)',
      283: 'fstatat(2)',
      284: 'fchownat(2)',
      285: 'futimesat(2)',
      286: 'unlinkat(2)',
      287: 'clock_settime(2)',
      288: 'ntp_adjtime(2)',
      289: 'setppriv(2)',
      290: 'modctl(2) - configure device policy',
      291: 'modctl(2) - configure additional privilege',
      292: 'kernel cryptographic framework',
      293: 'configure kernel SSL',
      294: 'brandsys(2)',
      295: 'Add IPsec policy rule',
      296: 'Delete IPsec policy rule',
      297: 'Clone IPsec policy',
      298: 'Flip IPsec policy',
      299: 'Flush IPsec policy rules',
      300: 'Update IPsec algorithms',
      301: 'portfs',
      302: 'ptrace(2)',
      303: 'chflags(2)',
      304: 'fchflags(2)',
      305: 'profil(2)',
      306: 'ktrace(2)',
      307: 'setlogin(2)',
      308: 'reboot(2)',
      309: 'revoke(2)',
      310: 'umask(2)',
      311: 'mprotect(2)',
      312: 'setpriority(2)',
      313: 'settimeofday(2)',
      314: 'flock(2)',
      315: 'mkfifo(2)',
      316: 'poll(2)',
      317: 'socketpair(2)',
      318: 'futimes(2)',
      319: 'setsid(2)',
      320: 'setprivexec(2)',
      321: 'nfssvc(2)',
      322: 'getfh(2)',
      323: 'quotactl(2)',
      324: 'add_profil()',
      325: 'kdebug_trace()',
      326: 'fstat(2)',
      327: 'fpathconf(2)',
      328: 'getdirentries(2)',
      329: 'truncate(2)',
      330: 'ftruncate(2)',
      331: 'sysctl(3)',
      332: 'mlock(2)',
      333: 'munlock(2)',
      334: 'undelete(2)',
      335: 'getattrlist()',
      336: 'setattrlist()',
      337: 'getdirentriesattr()',
      338: 'exchangedata()',
      339: 'searchfs()',
      340: 'minherit(2)',
      341: 'semconfig()',
      342: 'sem_open(2)',
      343: 'sem_close(2)',
      344: 'sem_unlink(2)',
      345: 'shm_open(2)',
      346: 'shm_unlink(2)',
      347: 'load_shared_file()',
      348: 'reset_shared_file()',
      349: 'new_system_share_regions()',
      350: 'pthread_kill(2)',
      351: 'pthread_sigmask(2)',
      352: 'auditctl(2)',
      353: 'rfork(2)',
      354: 'lchmod(2)',
      355: 'swapoff(2)',
      356: 'init_process()',
      357: 'map_fd()',
      358: 'task_for_pid()',
      359: 'pid_for_task()',
      360: 'sysctl() - non-admin',
      361: 'copyfile()',
      43001: 'getfsstat(2)',
      43002: 'ptrace(2)',
      43003: 'chflags(2)',
      43004: 'fchflags(2)',
      43005: 'profil(2)',
      43006: 'ktrace(2)',
      43007: 'setlogin(2)',
      43008: 'revoke(2)',
      43009: 'umask(2)',
      43010: 'mprotect(2)',
      43011: 'mkfifo(2)',
      43012: 'poll(2)',
      43013: 'futimes(2)',
      43014: 'setsid(2)',
      43015: 'setprivexec(2)',
      43016: 'add_profil()',
      43017: 'kdebug_trace()',
      43018: 'fstat(2)',
      43019: 'fpathconf(2)',
      43020: 'getdirentries(2)',
      43021: 'sysctl(3)',
      43022: 'mlock(2)',
      43023: 'munlock(2)',
      43024: 'undelete(2)',
      43025: 'getattrlist()',
      43026: 'setattrlist()',
      43027: 'getdirentriesattr()',
      43028: 'exchangedata()',
      43029: 'searchfs()',
      43030: 'minherit(2)',
      43031: 'semconfig()',
      43032: 'sem_open(2)',
      43033: 'sem_close(2)',
      43034: 'sem_unlink(2)',
      43035: 'shm_open(2)',
      43036: 'shm_unlink(2)',
      43037: 'load_shared_file()',
      43038: 'reset_shared_file()',
      43039: 'new_system_share_regions()',
      43040: 'pthread_kill(2)',
      43041: 'pthread_sigmask(2)',
      43042: 'auditctl(2)',
      43043: 'rfork(2)',
      43044: 'lchmod(2)',
      43045: 'swapoff(2)',
      43046: 'init_process()',
      43047: 'map_fd()',
      43048: 'task_for_pid()',
      43049: 'pid_for_task()',
      43050: 'sysctl() - non-admin',
      43051: 'copyfile(2)',
      43052: 'lutimes(2)',
      43053: 'lchflags(2)',
      43054: 'sendfile(2)',
      43055: 'uselib(2)',
      43056: 'getresuid(2)',
      43057: 'setresuid(2)',
      43058: 'getresgid(2)',
      43059: 'setresgid(2)',
      43060: 'wait4(2)',
      43061: 'lgetfh(2)',
      43062: 'fhstatfs(2)',
      43063: 'fhopen(2)',
      43064: 'fhstat(2)',
      43065: 'jail(2)',
      43066: 'eaccess(2)',
      43067: 'kqueue(2)',
      43068: 'kevent(2)',
      43069: 'fsync(2)',
      43070: 'nmount(2)',
      43071: 'bdflush(2)',
      43072: 'setfsuid(2)',
      43073: 'setfsgid(2)',
      43074: 'personality(2)',
      43075: 'getscheduler(2)',
      43076: 'setscheduler(2)',
      43077: 'prctl(2)',
      43078: 'getcwd(2)',
      43079: 'capget(2)',
      43080: 'capset(2)',
      43081: 'pivot_root(2)',
      43082: 'rtprio(2)',
      43083: 'sched_getparam(2)',
      43084: 'sched_setparam(2)',
      43085: 'sched_get_priority_max(2)',
      43086: 'sched_get_priority_min(2)',
      43087: 'sched_rr_get_interval(2)',
      43088: 'acl_get_file(2)',
      43089: 'acl_set_file(2)',
      43090: 'acl_get_fd(2)',
      43091: 'acl_set_fd(2)',
      43092: 'acl_delete_file(2)',
      43093: 'acl_delete_fd(2)',
      43094: 'acl_aclcheck_file(2)',
      43095: 'acl_aclcheck_fd(2)',
      43096: 'acl_get_link(2)',
      43097: 'acl_set_link(2)',
      43098: 'acl_delete_link(2)',
      43099: 'acl_aclcheck_link(2)',
      43100: 'sysarch(2)',
      43101: 'extattrctl(2)',
      43102: 'extattr_get_file(2)',
      43103: 'extattr_set_file(2)',
      43104: 'extattr_list_file(2)',
      43105: 'extattr_delete_file(2)',
      43106: 'extattr_get_fd(2)',
      43107: 'extattr_set_fd(2)',
      43108: 'extattr_list_fd(2)',
      43109: 'extattr_delete_fd(2)',
      43110: 'extattr_get_link(2)',
      43111: 'extattr_set_link(2)',
      43112: 'extattr_list_link(2)',
      43113: 'extattr_delete_link(2)',
      43114: 'kenv(8)',
      43115: 'jail_attach(2)',
      43116: 'sysctl(3)',
      43117: 'linux ioperm',
      43118: 'readdir(3)',
      43119: 'linux iopl',
      43120: 'linux vm86',
      43121: 'mac_get_proc(2)',
      43122: 'mac_set_proc(2)',
      43123: 'mac_get_fd(2)',
      43124: 'mac_get_file(2)',
      43125: 'mac_set_fd(2)',
      43126: 'mac_set_file(2)',
      43127: 'mac_syscall(2)',
      43128: 'mac_get_pid(2)',
      43129: 'mac_get_link(2)',
      43130: 'mac_set_link(2)',
      43131: 'mac_execve(2)',
      43132: 'getpath_fromfd(2)',
      43133: 'getpath_fromaddr(2)',
      43134: 'mq_open(2)',
      43135: 'mq_setattr(2)',
      43136: 'mq_timedreceive(2)',
      43137: 'mq_timedsend(2)',
      43138: 'mq_notify(2)',
      43139: 'mq_unlink(2)',
      43140: 'listen(2)',
      43141: 'mlockall(2)',
      43142: 'munlockall(2)',
      43143: 'closefrom(2)',
      43144: 'fexecve(2)',
      43145: 'faccessat(2)',
      43146: 'fchmodat(2)',
      43147: 'linkat(2)',
      43148: 'mkdirat(2)',
      43149: 'mkfifoat(2)',
      43150: 'mknodat(2)',
      43151: 'readlinkat(2)',
      43152: 'symlinkat(2)',
      43153: 'mac_getfsstat(2)',
      43154: 'mac_get_mount(2)',
      43155: 'mac_get_lcid(2)',
      43156: 'mac_get_lctx(2)',
      43157: 'mac_set_lctx(2)',
      43158: 'mac_mount(2)',
      43159: 'getlcid(2)',
      43160: 'setlcid(2)',
      43161: 'taskname_for_pid()',
      43162: 'access_extended(2)',
      43163: 'chmod_extended(2)',
      43164: 'fchmod_extended(2)',
      43165: 'fstat_extended(2)',
      43166: 'lstat_extended(2)',
      43167: 'mkdir_extended(2)',
      43168: 'mkfifo_extended(2)',
      43169: 'open_extended(2) - attr only',
      43170: 'open_extended(2) - read',
      43171: 'open_extended(2) - read,creat',
      43172: 'open_extended(2) - read,trunc',
      43173: 'open_extended(2) - read,creat,trunc',
      43174: 'open_extended(2) - write',
      43175: 'open_extended(2) - write,creat',
      43176: 'open_extended(2) - write,trunc',
      43177: 'open_extended(2) - write,creat,trunc',
      43178: 'open_extended(2) - read,write',
      43179: 'open_extended(2) - read,write,creat',
      43180: 'open_extended(2) - read,write,trunc',
      43181: 'open_extended(2) - read,write,creat,trunc',
      43182: 'stat_extended(2)',
      43183: 'umask_extended(2)',
      43184: 'openat(2) - attr only',
      43185: 'posix_openpt(2)',
      43186: 'cap_new(2)',
      43187: 'cap_getrights(2)',
      43188: 'cap_enter(2)',
      43189: 'cap_getmode(2)',
      43190: 'posix_spawn(2)',
      43191: 'fsgetpath(2)',
      43192: 'pread(2)',
      43193: 'pwrite(2)',
      43194: 'fsctl()',
      43195: 'ffsctl()',
      43196: 'lpathconf(2)',
      43197: 'pdfork(2)',
      43198: 'pdkill(2)',
      43199: 'pdgetpid(2)',
      43200: 'pdwait(2)',
      44901: 'session start',
      44902: 'session update',
      44903: 'session end',
      44904: 'session close',
      6144: 'at-create atjob',
      6145: 'at-delete atjob (at or atrm)',
      6146: 'at-permission',
      6147: 'cron-invoke',
      6148: 'crontab-crontab created',
      6149: 'crontab-crontab deleted',
      6150: 'crontab-permission',
      6151: 'inetd connection',
      6152: 'login - local',
      6153: 'logout - local',
      6154: 'login - telnet',
      6155: 'login - rlogin',
      6156: 'mount',
      6157: 'unmount',
      6158: 'rsh access',
      6159: 'su(1)',
      6160: 'system halt',
      6161: 'system reboot',
      6162: 'rexecd',
      6163: 'passwd',
      6164: 'rexd',
      6165: 'ftp access',
      6166: 'init',
      6167: 'uadmin',
      6168: 'system shutdown',
      6170: 'crontab-modify',
      6171: 'ftp logout',
      6172: 'login - ssh',
      6173: 'role login',
      6180: ' profile command',
      6181: 'add filesystem',
      6182: 'delete filesystem',
      6183: 'modify filesystem',
      6200: 'allocate-device success',
      6201: 'allocate-device failure',
      6202: 'deallocate-device success',
      6203: 'deallocate-device failure',
      6204: 'allocate-list devices success',
      6205: 'allocate-list devices failure',
      6207: 'create user',
      6208: 'modify user',
      6209: 'delete user',
      6210: 'disable user',
      6211: 'enable user',
      6212: 'newgrp login',
      6213: 'admin login',
      6214: 'authenticated kadmind request',
      6215: 'unauthenticated kadmind req',
      6216: 'kdc authentication svc request',
      6217: 'kdc tkt-grant svc request',
      6218: 'kdc tgs 2ndtkt mismtch',
      6219: 'kdc tgs issue alt tgt',
      6300: 'sudo(1)',
      6501: 'modify password',
      6511: 'create group',
      6512: 'delete group',
      6513: 'modify group',
      6514: 'add to group',
      6515: 'remove from group',
      6521: 'revoke object priv',
      6600: 'loginwindow login',
      6601: 'loginwindow logout',
      7000: 'user authentication',
      7001: 'SecSrvr connection setup',
      7002: 'SecSrvr AuthEngine',
      7003: 'SecSrvr authinternal mech',
      32800: 'OpenSSH login',
      45000: 'audit startup',
      45001: 'audit shutdown',
      45014: 'modify password',
      45015: 'create group',
      45016: 'delete group',
      45017: 'modify group',
      45018: 'add to group',
      45019: 'remove from group',
      45020: 'revoke object priv',
      45021: 'loginwindow login',
      45022: 'loginwindow logout',
      45023: 'user authentication',
      45024: 'SecSrvr connection setup',
      45025: 'SecSrvr AuthEngine',
      45026: 'SecSrvr authinternal mech',
      45027: 'Calife',
      45028: 'sudo(1)',
      45029: 'audit crash recovery',
      45030: 'SecSrvr AuthMechanism',
      45031: 'Security Assessment'}

  _TOKEN_TYPES = {
      0x00: 'AUT_INVALID',
      0x11: 'AUT_OTHER_FILE32',
      0x12: 'AUT_OHEADER',
      0x13: 'AUT_TRAILER',
      0x14: 'AUT_HEADER32',
      0x15: 'AUT_HEADER32_EX',
      0x21: 'AUT_DATA',
      0x22: 'AUT_IPC',
      0x23: 'AUT_PATH',
      0x24: 'AUT_SUBJECT32',
      0x25: 'AUT_XATPATH',
      0x26: 'AUT_PROCESS32',
      0x27: 'AUT_RETURN32',
      0x28: 'AUT_TEXT',
      0x29: 'AUT_OPAQUE',
      0x2a: 'AUT_IN_ADDR',
      0x2b: 'AUT_IP',
      0x2c: 'AUT_IPORT',
      0x2d: 'AUT_ARG32',
      0x2e: 'AUT_SOCKET',
      0x2f: 'AUT_SEQ',
      0x30: 'AUT_ACL',
      0x31: 'AUT_ATTR',
      0x32: 'AUT_IPC_PERM',
      0x33: 'AUT_LABEL',
      0x34: 'AUT_GROUPS',
      0x35: 'AUT_ACE',
      0x36: 'AUT_SLABEL',
      0x37: 'AUT_CLEAR',
      0x38: 'AUT_PRIV',
      0x39: 'AUT_UPRIV',
      0x3a: 'AUT_LIAISON',
      0x3b: 'AUT_NEWGROUPS',
      0x3c: 'AUT_EXEC_ARGS',
      0x3d: 'AUT_EXEC_ENV',
      0x3e: 'AUT_ATTR32',
      0x3f: 'AUT_UNAUTH',
      0x40: 'AUT_XATOM',
      0x41: 'AUT_XOBJ',
      0x42: 'AUT_XPROTO',
      0x43: 'AUT_XSELECT',
      0x44: 'AUT_XCOLORMAP',
      0x45: 'AUT_XCURSOR',
      0x46: 'AUT_XFONT',
      0x47: 'AUT_XGC',
      0x48: 'AUT_XPIXMAP',
      0x49: 'AUT_XPROPERTY',
      0x4a: 'AUT_XWINDOW',
      0x4b: 'AUT_XCLIENT',
      0x51: 'AUT_CMD',
      0x52: 'AUT_EXIT',
      0x60: 'AUT_ZONENAME',
      0x70: 'AUT_HOST',
      0x71: 'AUT_ARG64',
      0x72: 'AUT_RETURN64',
      0x73: 'AUT_ATTR64',
      0x74: 'AUT_HEADER64',
      0x75: 'AUT_SUBJECT64',
      0x76: 'AUT_SERVER64',
      0x77: 'AUT_PROCESS64',
      0x78: 'AUT_OTHER_FILE64',
      0x79: 'AUT_HEADER64_EX',
      0x7a: 'AUT_SUBJECT32_EX',
      0x7b: 'AUT_PROCESS32_EX',
      0x7c: 'AUT_SUBJECT64_EX',
      0x7d: 'AUT_PROCESS64_EX',
      0x7e: 'AUT_IN_ADDR_EX',
      0x7f: 'AUT_SOCKET_EX',
      0x80: 'AUT_SOCKINET32',
      0x81: 'AUT_SOCKINET128',
      0x82: 'AUT_SOCKUNIX'}

  # Token types with unknown data format:
  # 0x12: AUT_OHEADER
  # TODO: complete implementation of bsm_token_data_exec_args
  _DATA_TYPE_MAP_PER_TOKEN_TYPE = {
      0x11: 'bsm_token_data_other_file32',
      0x13: 'bsm_token_data_trailer',
      0x14: 'bsm_token_data_header32',
      0x15: 'bsm_token_data_header32_ex',
      0x21: 'bsm_token_data_data',
      0x22: 'bsm_token_data_ipc',
      0x23: 'bsm_token_data_path',
      0x24: 'bsm_token_data_subject32',
      0x26: 'bsm_token_data_subject32',
      0x27: 'bsm_token_data_return32',
      0x28: 'bsm_token_data_text',
      0x29: 'bsm_token_data_opaque',
      0x2a: 'bsm_token_data_in_addr',
      0x2b: 'bsm_token_data_ip',
      0x2c: 'bsm_token_data_iport',
      0x2d: 'bsm_token_data_arg32',
      0x2f: 'bsm_token_data_seq',
      0x32: 'bsm_token_data_ipc_perm',
      0x34: 'bsm_token_data_groups',
      0x3b: 'bsm_token_data_groups',
      0x3c: 'bsm_token_data_exec_args',
      0x3d: 'bsm_token_data_exec_args',
      0x3e: 'bsm_token_data_attr32',
      0x52: 'bsm_token_data_exit',
      0x60: 'bsm_token_data_zonename',
      0x71: 'bsm_token_data_arg64',
      0x72: 'bsm_token_data_return64',
      0x73: 'bsm_token_data_attr64',
      0x74: 'bsm_token_data_header64',
      0x75: 'bsm_token_data_subject64',
      0x77: 'bsm_token_data_subject64',
      0x79: 'bsm_token_data_header64_ex',
      0x7a: 'bsm_token_data_subject32_ex',
      0x7b: 'bsm_token_data_subject32_ex',
      0x7c: 'bsm_token_data_subject64_ex',
      0x7d: 'bsm_token_data_subject64_ex',
      0x7e: 'bsm_token_data_in_addr_ex',
      0x7f: 'bsm_token_data_socket_ex',
      0x80: 'bsm_token_data_sockinet32',
      0x81: 'bsm_token_data_sockinet64',
      0x82: 'bsm_token_data_sockunix',
  }
  #   0x25: 'AUT_XATPATH',
  #   0x2e: 'AUT_SOCKET',
  #   0x30: 'AUT_ACL',
  #   0x31: 'AUT_ATTR',
  #   0x33: 'AUT_LABEL',
  #   0x34: 'AUT_GROUPS',
  #   0x35: 'AUT_ACE',
  #   0x36: 'AUT_SLABEL',
  #   0x38: 'AUT_PRIV',
  #   0x39: 'AUT_UPRIV',
  #   0x3a: 'AUT_LIAISON',
  #   0x3b: 'AUT_NEWGROUPS',
  #   0x3c: 'AUT_EXEC_ARGS',
  #   0x3d: 'AUT_EXEC_ENV',
  #   0x3f: 'AUT_UNAUTH',
  #   0x40: 'AUT_XATOM',
  #   0x41: 'AUT_XOBJ',
  #   0x42: 'AUT_XPROTO',
  #   0x43: 'AUT_XSELECT',
  #   0x44: 'AUT_XCOLORMAP',
  #   0x45: 'AUT_XCURSOR',
  #   0x46: 'AUT_XFONT',
  #   0x47: 'AUT_XGC',
  #   0x48: 'AUT_XPIXMAP',
  #   0x49: 'AUT_XPROPERTY',
  #   0x4a: 'AUT_XWINDOW',
  #   0x4b: 'AUT_XCLIENT',
  #   0x51: 'AUT_CMD',
  #   0x52: 'AUT_EXIT',
  #   0x70: 'AUT_HOST',
  #   0x76: 'AUT_SERVER64',
  #   0x78: 'AUT_OTHER_FILE64',

  _DESCRIPTION_PER_TOKEN_TYPE = {
      0x11: 'token data other_file32',
      0x13: 'token data trailer',
      0x14: 'token data header32',
      0x15: 'token data header32_ex',
      0x21: 'token data data',
      0x22: 'token data ipc',
      0x23: 'token data path',
      0x24: 'token data subject32',
      0x26: 'token data process32',
      0x27: 'token data return32',
      0x28: 'token data text',
      0x29: 'token data opaque',
      0x2a: 'token data in_addr',
      0x2b: 'token data ip',
      0x2c: 'token data iport',
      0x2d: 'token data arg32',
      0x2f: 'token data seq',
      0x32: 'token data ipc_perm',
      0x34: 'token data groups',
      0x3b: 'token data newgroups',
      0x3c: 'token data exec_args',
      0x3d: 'token data exec_env',
      0x3e: 'token data attr32',
      0x60: 'token data zonename',
      0x71: 'token data arg64',
      0x72: 'token data return64',
      0x73: 'token data attr64',
      0x74: 'token data header64',
      0x75: 'token data subject64',
      0x77: 'token data process64',
      0x79: 'token data header64_ex',
      0x7a: 'token data subject32_ex',
      0x7b: 'token data process32_ex',
      0x7c: 'token data subject64_ex',
      0x7d: 'token data process64_ex',
      0x7e: 'token data in_addr_ex',
      0x7f: 'token data socket_ex',
      0x80: 'token data sockinet32',
      0x81: 'token data sockinet64',
      0x82: 'token data sockunix',
  }

  _HEADER_TOKEN_TYPES = frozenset([0x14, 0x15, 0x74, 0x79])

  _TRAILER_TOKEN_TYPE = 0x13

  _TRAILER_TOKEN_SIGNATURE = 0xb105

  # AUT_ARG32 or AUT_ARG64 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_ARG = [
      ('argument_index', 'Argument index', '_FormatIntegerAsDecimal'),
      ('argument_name', 'Argument name', '_FormatIntegerAsHexadecimal8'),
      ('argument_value_size', 'Argument value size', '_FormatIntegerAsDecimal'),
      ('argument_value', 'Argument value', '_FormatString')]

  # AUT_ATTR32 or AUT_ATTR64 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_ATTR = [
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('file_mode', 'File mode', '_FormatIntegerAsHexadecimal4'),
      ('user_identifier', 'User identifier', '_FormatIntegerAsDecimal'),
      ('group_identifier', 'Group identifier', '_FormatIntegerAsDecimal'),
      ('file_system_identifier', 'File system identifier',
       '_FormatIntegerAsHexadecimal8'),
      ('file_identifier', 'File identifier', '_FormatIntegerAsHexadecimal8'),
      ('device', 'Device', '_FormatIntegerAsHexadecimal8')]

  # AUT_DATA token data debug information.
  # TODO: improve reading data
  _DEBUG_INFO_TOKEN_DATA_DATA = [
      ('data_format', 'Data format', '_FormatIntegerAsHexadecimal2'),
      ('element_data_type', 'Element data type',
       '_FormatIntegerAsHexadecimal2'),
      ('number_of_elements', 'Number of elements', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  # AUT_EXIT, AUT_RETURN32, AUT_RETURN64 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_EXIT = [
      ('status', 'Status', '_FormatIntegerAsHexadecimal8'),
      ('return_value', 'Return value', '_FormatIntegerAsHexadecimal8')]

  # AUT_HEADER32, AUT_HEADER64 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_HEADER = [
      ('record_size', 'Record size', '_FormatIntegerAsDecimal'),
      ('format_version', 'Format version', '_FormatIntegerAsDecimal'),
      ('event_type', 'Event type', '_FormatIntegerAsEventType'),
      ('modifier', 'Modifier', '_FormatIntegerAsHexadecimal4'),
      ('timestamp', 'Timestamp', '_FormatIntegerAsPosixTime'),
      ('microseconds', 'Microseconds', '_FormatIntegerAsDecimal')]

  # AUT_HEADER32_EX, AUT_HEADER64_EX token data debug information.
  _DEBUG_INFO_TOKEN_DATA_HEADER_EX = [
      ('record_size', 'Record size', '_FormatIntegerAsDecimal'),
      ('format_version', 'Format version', '_FormatIntegerAsDecimal'),
      ('event_type', 'Event type', '_FormatIntegerAsEventType'),
      ('modifier', 'Modifier', '_FormatIntegerAsHexadecimal4'),
      ('net_type', 'Net type', '_FormatIntegerAsNetType'),
      ('ip_address', 'IP address', '_FormatArrayOfIntegersAsIPAddress'),
      ('timestamp', 'Timestamp', '_FormatIntegerAsPosixTime'),
      ('microseconds', 'Microseconds', '_FormatIntegerAsDecimal')]

  # AUT_IN_ADDR token data debug information.
  _DEBUG_INFO_TOKEN_DATA_IN_ADDR = [
      ('ip_address', 'IP address', '_FormatArrayOfIntegersAsIPv4Address')]

  # AUT_IN_ADDR_EX token data debug information.
  _DEBUG_INFO_TOKEN_DATA_IN_ADDR_EX = [
      ('net_type', 'Net type', '_FormatIntegerAsNetType'),
      ('ip_address', 'IP address', '_FormatArrayOfIntegersAsIPAddress')]

  # AUT_IP token data debug information.
  # TODO: add remaining IPv4 header information.
  _DEBUG_INFO_TOKEN_DATA_IP = [
      ('source_ip_address', 'Source IP address',
       '_FormatArrayOfIntegersAsIPv4Address'),
      ('destination_ip_address', 'Destination IP address',
       '_FormatArrayOfIntegersAsIPv4Address')]

  # AUT_IPC token data debug information.
  _DEBUG_INFO_TOKEN_DATA_IPC = [
      ('object_type', 'Object type', '_FormatIntegerAsHexadecimal2'),
      ('object_identifier', 'Object identifier',
       '_FormatIntegerAsHexadecimal8')]

  # AUT_IPORT token data debug information.
  _DEBUG_INFO_TOKEN_DATA_IPORT = [
      ('port_number', 'Port number', '_FormatIntegerAsDecimal')]

  # AUT_OPAQUE token data debug information.
  _DEBUG_INFO_TOKEN_DATA_OPAQUE = [
      ('data_size', 'Data size', '_FormatIntegerAsDecimal'),
      ('data', 'Data', '_FormatDataInHexadecimal')]

  # AUT_OTHER_FILE32 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_OTHER_FILE32 = [
      ('timestamp', 'Timestamp', '_FormatIntegerAsPosixTime'),
      ('microseconds', 'Microseconds', '_FormatIntegerAsDecimal'),
      ('name_size', 'Name size', '_FormatIntegerAsDecimal'),
      ('name', 'Name', '_FormatString')]

  # AUT_PATH token data debug information.
  _DEBUG_INFO_TOKEN_DATA_PATH = [
      ('path_size', 'Path size', '_FormatIntegerAsDecimal'),
      ('path', 'Path', '_FormatString')]

  # AUT_SEQ token data debug information.
  _DEBUG_INFO_TOKEN_DATA_SEQ = [
      ('sequence_number', 'Sequence number', '_FormatIntegerAsDecimal')]

  # AUT_SOCKET_EX token data debug information.
  _DEBUG_INFO_TOKEN_DATA_SOCKET_EX = [
      ('socket_domain', 'Socket domain', '_FormatIntegerAsHexadecimal4'),
      ('socket_type', 'Socket type', '_FormatIntegerAsHexadecimal4'),
      ('net_type', 'Net type', '_FormatIntegerAsNetType'),
      ('local_port', 'Local port', '_FormatIntegerAsDecimal'),
      ('local_ip_address', 'Local IP address',
       '_FormatArrayOfIntegersAsIPAddress'),
      ('remote_port', 'Remote port', '_FormatIntegerAsDecimal'),
      ('remote_ip_address', 'Remote IP address',
       '_FormatArrayOfIntegersAsIPAddress')]

  # AUT_SOCKINET32 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_SOCKINET32 = [
      ('socket_family', 'Socket family', '_FormatIntegerAsHexadecimal4'),
      ('local_port', 'Local port', '_FormatIntegerAsDecimal'),
      ('local_ip_address', 'Local IP address',
       '_FormatArrayOfIntegersAsIPv4Address')]

  # AUT_SOCKINET64 token data debug information.
  _DEBUG_INFO_TOKEN_DATA_SOCKINET64 = [
      ('socket_family', 'Socket family', '_FormatIntegerAsHexadecimal4'),
      ('local_port', 'Local port', '_FormatIntegerAsDecimal'),
      ('local_ip_address', 'Local IP address',
       '_FormatArrayOfIntegersAsIPv6Address')]

  # AUT_SOCKUNIX token data debug information.
  _DEBUG_INFO_TOKEN_DATA_SOCKUNIX = [
      ('socket_family', 'Socket family', '_FormatIntegerAsHexadecimal4'),
      ('socket_path', 'Socket path', None)]

  # AUT_SUBJECT32, AUT_SUBJECT64, AUT_PROCESS32 and AUT_PROCESS64 token data
  # debug information.
  _DEBUG_INFO_TOKEN_DATA_SUBJECT = [
      ('audit_user_identifier', 'Audit user identifier',
       '_FormatIntegerAsDecimal'),
      ('effective_user_identifier', 'Effective user identifier',
       '_FormatIntegerAsDecimal'),
      ('effective_group_identifier', 'Effective group identifier',
       '_FormatIntegerAsDecimal'),
      ('real_user_identifier', 'Real user identifier',
       '_FormatIntegerAsDecimal'),
      ('real_group_identifier', 'Real group identifier',
       '_FormatIntegerAsDecimal'),
      ('process_identifier', 'Process identifier', '_FormatIntegerAsDecimal'),
      ('session_identifier', 'Session identifier', '_FormatIntegerAsDecimal'),
      ('terminal_port', 'Terminal port', '_FormatIntegerAsDecimal'),
      ('ip_address', 'IP address', '_FormatArrayOfIntegersAsIPv4Address')]

  # AUT_SUBJECT32_EX, AUT_SUBJECT64_EX, AUT_PROCESS32_EX and AUT_PROCESS64_EX
  # token data debug information.
  _DEBUG_INFO_TOKEN_DATA_SUBJECT_EX = [
      ('audit_user_identifier', 'Audit user identifier',
       '_FormatIntegerAsDecimal'),
      ('effective_user_identifier', 'Effective user identifier',
       '_FormatIntegerAsDecimal'),
      ('effective_group_identifier', 'Effective group identifier',
       '_FormatIntegerAsDecimal'),
      ('real_user_identifier', 'Real user identifier',
       '_FormatIntegerAsDecimal'),
      ('real_group_identifier', 'Real group identifier',
       '_FormatIntegerAsDecimal'),
      ('process_identifier', 'Process identifier', '_FormatIntegerAsDecimal'),
      ('session_identifier', 'Session identifier', '_FormatIntegerAsDecimal'),
      ('terminal_port', 'Terminal port', '_FormatIntegerAsDecimal'),
      ('net_type', 'Net type', '_FormatIntegerAsNetType'),
      ('ip_address', 'IP address', '_FormatArrayOfIntegersAsIPAddress')]

  # AUT_TEXT token data debug information.
  _DEBUG_INFO_TOKEN_DATA_TEXT = [
      ('text_size', 'Text size', '_FormatIntegerAsDecimal'),
      ('text', 'Text', '_FormatString')]

  # AUT_TRAILER token data debug information.
  _DEBUG_INFO_TOKEN_DATA_TRAILER = [
      ('signature', 'Signature', '_FormatIntegerAsHexadecimal4'),
      ('record_size', 'Record size', '_FormatIntegerAsDecimal')]

  # AUT_ZONENAME token data debug information.
  _DEBUG_INFO_TOKEN_DATA_ZONENAME = [
      ('name_size', 'Name size', '_FormatIntegerAsDecimal'),
      ('name', 'Name', '_FormatString')]

  # TODO: implement and add debug info for token type 0x32
  # TODO: implement and add debug info for token type 0x34 and 0x3b
  # TODO: implement and add debug info for token type 0x3c and 0x3d
  _DEBUG_INFO_TOKEN_DATA = {
      0x11: _DEBUG_INFO_TOKEN_DATA_OTHER_FILE32,
      0x13: _DEBUG_INFO_TOKEN_DATA_TRAILER,
      0x14: _DEBUG_INFO_TOKEN_DATA_HEADER,
      0x15: _DEBUG_INFO_TOKEN_DATA_HEADER_EX,
      0x21: _DEBUG_INFO_TOKEN_DATA_DATA,
      0x22: _DEBUG_INFO_TOKEN_DATA_IPC,
      0x23: _DEBUG_INFO_TOKEN_DATA_PATH,
      0x24: _DEBUG_INFO_TOKEN_DATA_SUBJECT,
      0x26: _DEBUG_INFO_TOKEN_DATA_SUBJECT,
      0x27: _DEBUG_INFO_TOKEN_DATA_EXIT,
      0x28: _DEBUG_INFO_TOKEN_DATA_TEXT,
      0x29: _DEBUG_INFO_TOKEN_DATA_OPAQUE,
      0x2a: _DEBUG_INFO_TOKEN_DATA_IN_ADDR,
      0x2b: _DEBUG_INFO_TOKEN_DATA_IP,
      0x2c: _DEBUG_INFO_TOKEN_DATA_IPORT,
      0x2d: _DEBUG_INFO_TOKEN_DATA_ARG,
      0x2f: _DEBUG_INFO_TOKEN_DATA_SEQ,
      0x3e: _DEBUG_INFO_TOKEN_DATA_ATTR,
      0x52: _DEBUG_INFO_TOKEN_DATA_EXIT,
      0x60: _DEBUG_INFO_TOKEN_DATA_ZONENAME,
      0x71: _DEBUG_INFO_TOKEN_DATA_ARG,
      0x72: _DEBUG_INFO_TOKEN_DATA_EXIT,
      0x73: _DEBUG_INFO_TOKEN_DATA_ATTR,
      0x74: _DEBUG_INFO_TOKEN_DATA_HEADER,
      0x75: _DEBUG_INFO_TOKEN_DATA_SUBJECT,
      0x77: _DEBUG_INFO_TOKEN_DATA_SUBJECT,
      0x79: _DEBUG_INFO_TOKEN_DATA_HEADER_EX,
      0x7a: _DEBUG_INFO_TOKEN_DATA_SUBJECT_EX,
      0x7b: _DEBUG_INFO_TOKEN_DATA_SUBJECT_EX,
      0x7c: _DEBUG_INFO_TOKEN_DATA_SUBJECT_EX,
      0x7d: _DEBUG_INFO_TOKEN_DATA_SUBJECT_EX,
      0x7e: _DEBUG_INFO_TOKEN_DATA_IN_ADDR_EX,
      0x7f: _DEBUG_INFO_TOKEN_DATA_SOCKET_EX,
      0x80: _DEBUG_INFO_TOKEN_DATA_SOCKINET32,
      0x81: _DEBUG_INFO_TOKEN_DATA_SOCKINET64,
      0x82: _DEBUG_INFO_TOKEN_DATA_SOCKUNIX,
  }

  def _FormatArrayOfIntegersAsIPAddress(self, array_of_integers):
    """Formats an array of integers as an IP address.

    Args:
      array_of_integers (list[int]): array of integers.

    Returns:
      str: array of integers formatted as an IP address or None if the number
          of integers in the sequence is not supported.
    """
    number_of_integers = len(array_of_integers)

    if number_of_integers == 4:
      return self._FormatArrayOfIntegersAsIPv4Address(array_of_integers)
    elif number_of_integers == 16:
      return self._FormatArrayOfIntegersAsIPv6Address(array_of_integers)

    return None

  def _FormatIntegerAsEventType(self, integer):
    """Formats an integer as an event type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an event type .
    """
    event_type_string = self._EVENT_TYPES.get(integer, 'UNKNOWN')
    return '0x{0:04x} ({1:s})'.format(integer, event_type_string)

  def _FormatIntegerAsNetType(self, integer):
    """Formats an integer as a net type.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a net type .
    """
    if integer not in (4, 16):
      raise errors.ParseError('Unsupported net type: {0:d}'.format(integer))

    # TODO: print net type as descriptive string.
    return self._FormatIntegerAsDecimal(integer)

  def _FormatString(self, string):
    """Formats a string.

    Args:
      string (str): string.

    Returns:
      str: formatted string.
    """
    return string.rstrip('\x00')

  def _ReadRecord(self, file_object, file_offset):
    """Reads an event record.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the token relative to the start of
          the file-like object.

    Raises:
      ParseError: if the event record cannot be read.
    """
    token_type, token_data = self._ReadToken(file_object, file_offset)

    if self._debug:
      debug_information = self._DEBUG_INFO_TOKEN_DATA.get(token_type, None)
      if debug_information:
        self._DebugPrintStructureObject(token_data, debug_information)

    if token_type not in self._HEADER_TOKEN_TYPES:
      raise errors.ParseError(
          'Unsupported header token type: 0x{0:02x}'.format(token_type))

    if token_data.format_version != 11:
      raise errors.ParseError('Unsupported format version type: {0:d}'.format(
          token_data.format_version))

    header_record_size = token_data.record_size
    record_end_offset = file_offset + header_record_size
    while file_offset < record_end_offset:
      token_type, token_data = self._ReadToken(file_object, file_offset)
      if not token_data:
        raise errors.ParseError('Unsupported token type: 0x{0:02x}'.format(
            token_type))

      # TODO: add callback for validation (trailer) and read of more complex
      # structures.

      file_offset = file_object.tell()

      if self._debug:
        debug_information = self._DEBUG_INFO_TOKEN_DATA.get(token_type, None)
        if debug_information:
          self._DebugPrintStructureObject(token_data, debug_information)

      if token_type == self._TRAILER_TOKEN_TYPE:
        break

    if token_data.signature != self._TRAILER_TOKEN_SIGNATURE:
      raise errors.ParseError('Unsupported signature in trailer token.')

    if token_data.record_size != header_record_size:
      raise errors.ParseError(
          'Mismatch of event record size between header and trailer token.')

  def _ReadToken(self, file_object, file_offset):
    """Reads a token.

    Args:
      file_object (file): file-like object.
      file_offset (int): offset of the token relative to the start of
          the file-like object.

    Returns:
      tuple[int, object]: token type and token data or None if the token
          type is not supported.
    """
    data_type_map = self._GetDataTypeMap('uint8')

    token_type, _ = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map, 'token type')

    if self._debug:
      token_type_string = self._TOKEN_TYPES.get(token_type, 'UNKNOWN')
      value_string = '0x{0:02x} ({1:s})'.format(token_type, token_type_string)
      self._DebugPrintValue('Token type', value_string)

    token_data = None
    data_type_map_name = self._DATA_TYPE_MAP_PER_TOKEN_TYPE.get(
        token_type, None)
    if data_type_map_name:
      data_type_map = self._GetDataTypeMap(data_type_map_name)

      description = self._DESCRIPTION_PER_TOKEN_TYPE.get(token_type, '')
      token_data, _ = self._ReadStructureFromFileObject(
          file_object, file_offset + 1, data_type_map, description)

    return token_type, token_data

  def ReadFileObject(self, file_object):
    """Reads a BSM event auditing file.

    Args:
      file_object (file): file-like object.

    Raises:
      ParseError: if the file cannot be read.
    """
    file_offset = file_object.tell()
    while file_offset < self._file_size:
      self._ReadRecord(file_object, file_offset)
      file_offset = file_object.tell()
