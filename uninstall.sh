#!/bin/bash
echo "Desinstalando HMI..."
sudo systemctl stop hmi_data.service
sudo systemctl disable hmi_data.service
systemctl --user stop hmi-web.service
systemctl --user disable hmi-web.service
sudo rm -f /etc/systemd/system/hmi_data.service
rm -f ~/.config/systemd/user/hmi-web.service
echo "HMI desinstalado."