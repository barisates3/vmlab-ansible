# vmlab-ansible

vmlab projesinin Ansible rolleri ve playbook'lari.
AWX bu depoyu proje kaynagi olarak kullanir.

## Roller

| Rol | Gorev |
|---|---|
| common | Temel sunucu hazirligi, paketler, zaman dilimi, guvenlik duvari |
| docker | Docker Engine ve Compose eklentisi |
| postgresql | PostgreSQL sunucusu, veritabani ve kullanici olusturma |
| nginx | Nginx web sunucusu ve site yapilandirmasi |
| redis | Redis sunucusu |
| lemp | Nginx + PostgreSQL + PHP yigini (nginx ve postgresql rollerine bagimli) |
| node_exporter | Prometheus izleme ajani |

## Degiskenler

Her rolun `defaults/main.yml` dosyasinda varsayilan degerleri vardir.
AWX'te Survey ile calistirma aninda degistirilebilir.

Ornek (postgresql):

| Degisken | Varsayilan |
|---|---|
| postgres_db | appdb |
| postgres_user | appuser |
| postgres_port | 5432 |

## Envanter

- `inventory/hosts.ini` — statik envanter (yerel test icin)
- `inventory/dynamic/libvirt_inventory.py` — libvirt uzerindeki
  calisan makineleri otomatik bulan dinamik envanter

## Koleksiyonlar

`collections/requirements.yml` dosyasinda tanimlidir. AWX proje
senkronizasyonu sirasinda otomatik yuklenir.

## Kullanim

```bash
ansible-playbook playbooks/nginx.yml
ansible-playbook -i inventory/dynamic/libvirt_inventory.py playbooks/docker.yml --limit web01
```
