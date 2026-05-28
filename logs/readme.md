# Deploy Updated Docker Image

## Pull Latest Docker Image

```bash
sudo docker pull ghcr.io/amruth123-ai/delta-ws-bot:latest
```

---

## Stop Existing Container

```bash
sudo docker stop delta-bot
```

---

## Remove Existing Container

```bash
sudo docker rm delta-bot
```

---

## Run Updated Container

```bash
sudo docker run -d \
--name delta-bot \
--restart unless-stopped \
--env-file .env \
ghcr.io/amruth123-ai/delta-ws-bot:latest
```

---

## Check Container Logs

```bash
sudo docker logs -f delta-bot
```