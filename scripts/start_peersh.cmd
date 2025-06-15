@echo off
echo Iniciando Peers...

set PYTHONPATH=..

start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 1 192.168.0.62 9001 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 2 192.168.0.62 9002 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 3 192.168.0.62 9003 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 4 192.168.0.62 9004 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 5 192.168.0.62 9005 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 6 192.168.0.62 9006 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 7 192.168.0.62 9007 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 8 192.168.0.62 9008 192.168.0.62 8000
start cmd /k python "D:\downloads google\SD\MiniBit\peer\Peer.py" 9 192.168.0.62 9009 192.168.0.62 8000

pause
