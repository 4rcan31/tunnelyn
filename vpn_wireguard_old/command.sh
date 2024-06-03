  docker run -d \
  --name=wg-easy \
  -e LANG=es \
  -e WG_HOST="34.125.40.228" \
  -e PASSWORD="admin" \
  -e WG_DEFAULT_DNS=8.8.8.8 \
  -e WG_ALLOWED_IPS=10.8.0.0/24 \
  -e WG_PERSISTENT_KEEPALIVE=25 \
  -e PORT=51821 \
  -e WG_PORT=51820 \
  -v ~/.wg-easy:/etc/wireguard \
  -p 51820:51820/udp \
  -p 51821:51821/tcp \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --sysctl="net.ipv4.ip_forward=1" \
  --restart unless-stopped \
  ghcr.io/wg-easy/wg-easy