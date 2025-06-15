import sys
from peer import Peer

def main():
    if len(sys.argv) != 6:
        print("Uso: python main_peer.py <peerId> <meu_ip> <minha_porta> <tracker_ip> <tracker_porta>")
        sys.exit(1)

    peerId = sys.argv[1]
    ip = sys.argv[2]
    port = int(sys.argv[3])
    trackerIp = sys.argv[4]
    trackerPort = int(sys.argv[5])

    peer = Peer(peerId, ip, port, trackerIp, trackerPort)
    peer.start()

if __name__ == "__main__":
    main()