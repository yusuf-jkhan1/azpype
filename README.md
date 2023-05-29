# Azpype 

Azpype is intended to primarily be an easy-to-use lightweight native Python interface to the already excellent AzCopy command line tool.

The secondary aim is for it to extend the functionality with some additional scaffolding and functionality such as

#### *Python enhanced logging*
-- INFO HERE --

#### *Config driven defaults*
-- INFO HERE --

#### *Out-of-the-box and custom Validation Checks*
-- INFO HERE --

---
## Installation

> 📢 _**Important:** For both convenience and the purpose of behaving as a python native library; installing azpype will additionally download the platform appropriate precompiled [azcopy](https://github.com/Azure/azure-storage-azcopy/releases) binary (**v10.18.1**) and store it under
`~/.azpype/`. This will be bundled in as part of the package distributuion and not as a separate installation script._

Install via pip  
```
pip install azpype
```

---

## 📝 Housekeeping TODOs

- 📘 Add back in unittests for other modules
- 📚 Update readme with better articulated out line of 'why'
- 📖 Add Usage section
- 📖 Add instructions on how to create the application service principal, grant it permissions and create the client secret.
- ⏱️ Update readme with timed examples of Azpype/AzCopy along with azure-blob-storage synchronous and async
- 📘 Add example notebooks

---

##  Authentication

Currently, Azpype only accepts authenticating via Application Service Principal set via the following Azcopy environment variables:

- `AZCOPY_TENANT_ID`
- `AZCOPY_SPA_APPLICATION_ID`
- `AZCOPY_SPA_CLIENT_SECRET`
- `AZCOPY_AUTO_LOGIN_TYPE`

These can be injected/overriden at runtime into the python process via
```python
import os
os.environ["AZCOPY_TENANT_ID"] = <TenantID>
# ...
```

Please follow good practices when handling these environment variables and client credentials. 

Going forward Azpype aims to use a default precedence order for authentication, starting with MSI, then SPA, then SAS. Ideally using, or following the pattern of `DefaultAzureCredential()`. 

---

## 🚧 In-Development: FS Monitor 

I'd love to get some feedback on this feature but my thought is for azpype to be as simple as possible I may create an 'agent' mode for it which takes advantage of the [watchdog](https://github.com/gorakhargosh/watchdog) package. Agent mode will allow Azpype to be deployed as a long-running background process, triggering actions based on file system events. For instance, poll every 5 minutes and run `Copy()` when a new file is detected. Then user code can do the appropriate stage clearing/archiving etc.

> 🚧 _**Status:** Not yet in development_

---

## 🧪 Benchmark Grid Search 

Currently, Azcopy provides a useful [benchmarking utility](https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-bench) which helps determine optimal concurrency for a given network, machine (assuming default settings of auto tuning to cores), number of files and size per file.

The Benchmark grid search feature - will leverage this and create small grid search through various combinations of file count and file size, outputting plots/data to reflect the expected range of performance for Azcopy in that execution environment.

> 🚧 _**Status:** Not yet in development_