# dokku-wrapper

Wrapper em Python para gerenciar aplicações Dokku.

## Instalação

```bash

pip install dokku-wrapper
```

## Uso

```python
from dokku_wrapper.dokku import Dokku

dokku = Dokku() 
dokku.apps.create("meu-app")
```