# Evidencia fliaš

Projekt sa venuje evidencií plynových fliaš na KEF FMFI. V rôznych laboratóriach sú
potrebné rôzne druhy plynov. Keďže nie sú zriadené centrálne rozvody plynu, v jednotlivých
laboratóriach sú umiestnené fľaše s plynmi podľa potreby.

KEF potrebuje mať prehľad o polohe jednotlivých fliaš s jednoduchým vyhľadávaním a kompletnou históriou.
Doteraz bola na tento účel využívaná Excelovská tabuľka.

Zároveň KEF chce sledovať spotrebu plynov. Každá používaná fľaša má pripojený manometer, ktorý zobrazuje
aktuálny tlak vo fľaši. Existujú elektronické manometre, ktoré sa dajú odčítavať automaticky, tie sú však
veľmi drahé. Preto systém dovoľuje používateľom ručne zadávať aktuálny tlak, prípadne automaticky detekovať
tlak z fotky manometra.

## Demo video

[Video je zavesené tu](https://drive.google.com/file/d/1UAMW7wRqG9RmjetQ6Mymzxy6X5kxr3f8/view?usp=sharing)

## Dokumentácia

- [Katalóg požiadaviek](./docs/katalog.pdf)
- [Návrh](./docs/navrh.pdf)
- [Testovacie scenáre](./docs/testing.pdf)

## Inštalácia

Prerekvizity:

- Python (aspoň) 3.9
- Poetry (`pip install poetry`)

Po naklonovaní repozitára treba nainštalovať potrebné Python balíky. Projekt používa nástroj Poetry,
ktorý zjednodušuje správu balíkov a virtuálnych prostredí (venv).

```shell
poetry install
```

Následne potrebujeme nakonfigurovať aplikáciu pomocou súboru `.env`. Na vývoj stačí skopírovať obsah `.env.example`,
pre produkčné prostredie viď. návrh, časť 2.1.1.

### Vývojové prostredie

Ak chceme spustiť vývojové prostredie, stačí nám spustiť migrácie databázy a vstavaný development server:

```shell
poetry shell    # <- vstúpime do Poetry venv-u
python manage.py migrate
python manage.py runserver
```

Teraz vieme navštíviť systém na adrese `localhost:8000`.

### Produkčné prostredie

Ak chceme spustiť produkčné prostredie, potrebujeme spustiť migrácie a prípravu statických súborov (JS, CSS...):

```shell
poetry shell    # <- vstúpime do Poetry venv-u
python manage.py migrate
python manage.py collectstatic --no-input
```

Následne potrebujeme spustiť aplikačný server, ktorý bude systém spúšťať. Na výber máme z niekoľkých možností,
v podstate záleží na preferencií systémového administrátora, ktorý bude systém nasadzovať.

#### Gunicorn

[Gunicorn](https://gunicorn.org) je jeden s Pythonových aplikačných serverov. Spustí Django aplikáciu na
nejakom porte *(je možné použiť aj UNIX socket)*. Na tomto porte beží HTTP server, na ktorom Django obsluhuje
požiadavky. Gunicorn ako taký nie je moc vhodný na vystavenie do voľného internetu (očakáva, že klienti sú
pomerne slušní). Preto sa štandardne pred neho nasadzuje reverzná proxy.

Tento príkaz spustí 2 workerov na porte 8000:

```shell
poetry shell    # <- vstúpime do Poetry venv-u
gunicorn -b 127.0.0.1:8000 -w 2 flase.wsgi
```

Ak chceme celú cestu k `gunicorn`, aby sme nemuseli robiť `poetry shell` (napr. zo systemd servicu), cesta k
venvu sa dá zistiť pomocou `poetry env info`.

Proxy konfigurácia pre Apache by bola potom:

```
ProxyPass / http://127.0.0.1:8000/
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https"     # <- sem dať hodnotu podľa toho, či ide o http alebo https VirtualHost
```

Pre nginx:

```
location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;

    proxy_redirect off;
    proxy_pass http://127.0.0.1:8000;
}
```

Pre jednoduchosť sa v repozitári nachádza aj `Dockerfile`, ktorý obsahuje všetko potrebné pre spustenie projektu pod Gunicorn-om.

[Viac informácií tu](https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/gunicorn/)

#### mod_wsgi

Existuje ešte [mod_wsgi](https://modwsgi.readthedocs.io/en/develop/), ktorý vie spúšťať Django priamo z Apachu.

[Viac informácií tu](https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/modwsgi/)
