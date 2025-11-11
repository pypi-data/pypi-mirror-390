# geesc_helpers
Funções helpers no python pros projetos do geesc

# Uso básico
``` {python}
from geesc_helpers import dropbox_helpers as dh

dbx = dh.auth(".env")

file_read = dh.try_download(dbx, "/dropbox/path/file.csv", "./local/path/file.csv")
df = pd.read_csv(file_read)
```

