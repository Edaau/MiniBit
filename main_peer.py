from peer.peer import Peer
import sys

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Uso: python main_peer.py <ID> <IP> <PORTA> <TRACKER_IP> <TRACKER_PORTA>")
        sys.exit(1)

    peerId = sys.argv[1]
    ip = sys.argv[2]
    porta = int(sys.argv[3])
    trackerIp = sys.argv[4]
    trackerPorta = int(sys.argv[5])

    peer = Peer(peerId, ip, porta, trackerIp, trackerPorta)
    peer.start()