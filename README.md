# leskraft_terminal
Сначала установить нужный софт:
```
sudo apt-get install -y git zip unzip vim mc tmux wget htop python3-pyqt5
```
задать пароль root на всякий случай:
```
sudo passwd root
```
настройки терминала в файле env.py

## Установка cups (сервера печати):
```
sudo apt-get install cups avahi-daemon avahi-discover
```
```
sudo adduser pi lpadmin /// добавить права
```
```
sudo vim /etc/cups/cupsd.conf
```
### В конфиге надо:
```
Listen localhost:631 ///эту строку комментируем
Port 631 ///эту строку добавляем****

# Restrict access to the server...
<Location />
  Order allow,deny
  Allow @Local ///эту строку добавляем
</Location>
 
# Restrict access to the admin pages...
<Location /admin>
  Order allow,deny
  Allow @Local ///эту строку добавляем
</Location>
 
# Restrict access to configuration files...
<Location /admin/conf>
  AuthType Default
  Require user @SYSTEM
  Order allow,deny
  Allow @Local ///эту строку добавляем
</Location>
```

Затем перезапустить службу:
```
sudo service cups restart
```
Если все сделано правильно, то веб-интерфейс CUPS станет доступен по адресу http://ip-адрес-raspberry-pi:631 из браузера.

## Автозапуск:
файл start.sh если нет, надо создать
```
sudo vim /home/pi/lkterminal/start.sh
```
содержимое файла:
```
#!/bin/bash

tmux kill-session -t robbi
if [ -z $TMUX ]; then
	tmux new-session -s robbi -d -n lkterminal -c '/home/pi/lkterminal/'
	tmux send-keys -t robbi:lkterminal 'sudo python3 /home/pi/lkterminal/main.py' Enter
	tmux new-window -t robbi -n dev -c '/home/pi/'
fi
```

Файл надо сделать исполняемым
```
sudo chmod +x /home/pi/lkterminal/start.sh
```

создать папку:
```
mkdir /home/pi/.config/autostart
```
Создать файл:
```
sudo vim /home/pi/.config/autostart/lkterminal.desktop
```
Содержимое файла:
```
[Desktop Entry]
Version=1.0
Name=lkterminal
Comment=lk
Exec=/home/pi/lkterminal/start.sh
Path=/home/pi/lkterminal
Terminal=false
StartupNotify=true
Type=Application
Categories=Utility;Application;
```
Добавить автоподключение к сессии по SSH:
```
sudo vim /home/.bashrc
```
в конце файла добавить:
```
tmux attach -t robbi:dev
```

перезагрузить:
```
sudo reboot
```

## p.s.
Если не видит COM-устройств, надо выполнить:
```
python3 /utility/com_ports.py
```
Оно покажет подключенные COM-устройства и их PID или отобразит ошибку, если не установлены нужные зависимости

Если не видит принтер, то проверить имя принтера в:
```
sudo vim /home/pi/lkterminal/env.py
```
Посмотреть доступные сетевые принтеры:
```
python3 /utility/print.py #
```
Имя нужного надо вписать в env.py
Если скрипт выдаст ошибку: установить CUPS, нужные зависимости
