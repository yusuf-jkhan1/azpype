# Azpype 

> NOTE: This is still a very early stage project. Public interfaces and large parts of the implmentation are still subject to change.

Azpype is intended to primarily be an easy-to-use lightweight native Python interface to the already excellent AzCopy command line tool.

The secondary aim is for it to extend the functionality with some additional scaffolding and functionality such as

#### *Python enhanced logging*
-- INFO HERE --

#### *Config driven defaults*
-- INFO HERE --

#### *Out-of-the-box and custom Validation Checks*
-- INFO HERE --

---
## Installation & Init

Currently supports x86_64, and Apple Silicon

> 📢 _**Important:** For both convenience and the purpose of behaving as a python native library; installing azpype will additionally download the platform appropriate precompiled [azcopy](https://github.com/Azure/azure-storage-azcopy/releases) binary (**v10.18.1**) and store it under
`~/.azpype/`. This will be bundled in as part of the package distributuion and not as a separate installation script._

Install via pip  
```
pip install azpype
```

No separate init step is required. The AzCopy binary and a baseline config template ship with the package.
On first use, azpype will create `~/.azpype/copy_config.yaml` from the bundled template if it doesn't exist.

---
## Usage

### Setup for Authentication
Currently azpype supports application service principal based and shared access signature (SAS) token authentication. 


### Service Principal
The recommended method is to use application service principals. To do so create/register the app in Azure and then grant it the appropriate RBAC permissions in any Blob Storage accounts you intend to use. 
Ensure that the host that runs Azpype has access to the following environment variables via the host or process environment.
-  `AZCOPY_TENANT_ID`
- `AZCOPY_SPA_APPLICATION_ID`
- `AZCOPY_SPA_CLIENT_SECRET`
- `AZCOPY_AUTO_LOGIN_TYPE`

#### Examples of setting the environment variables
Setting and environment variable in python:
```python
import os

#These are dummy values of course
os.environ["AZCOPY_TENANT_ID"] = "12d3fba3-efac-1234-a1b2-3f4cafbcb123"
os.environ["AZCOPY_SPA_APPLICATION_ID"] = "e1234c36-bc1e-4f23-ace7-cb088c04c123"
os.environ["AZCOPY_SPA_CLIENT_SECRET"] = "cAl1Q~2mdABUUSCD2KEZzaF150P0jXAqKs2ANdMS"
#This needs to be set so that interactive login is not needed
os.environ["AZCOPY_AUTO_LOGIN_TYPE"]= "SPN" #SPN=Service Principal
```

Setting environment variables in python via .env:
```python
#pip install python-dotenv #if needed
import os
from dotenv import load_dotenv
load_dotenv('.env')


#This assumes you have an .env file in your working directory with an entry like:  
#AZCOPY_TENANT_ID="12d3fba3-efac-1234-a1b2-3f4cafbcb123"
tenant_id = os.getenv('AZCOPY_TENANT_ID')
#etc
```
OR Set environment variable via shell (MacOS & Linux)
```shell
export AZCOPY_TENANT_ID=""12d3fba3-efac-1234-a1b2-3f4cafbcb123"
```
OR Set environment variable via shell (Windows)
```shell
setx AZCOPY_TENANT_ID ""12d3fba3-efac-1234-a1b2-3f4cafbcb123"
```

#### Shared Access Signature (SAS) Token

For shared access signature use the `sas_token` parameter in the `Copy()` command and supply the sas token excluding the leading '?'

### Configuration

When installed, azpype includes a configuration template. On first run, a `~/.azpype/copy_config.yaml` file will be created if missing. These are default key-values that are options/arguments to the `Copy` command.
For example the yaml could have values like this:
```yaml
# Overwrite the conflicting files and blobs at the destination if this flag is set to true.
# Possible values include 'true', 'false', 'prompt', and 'ifSourceNewer'.
# Default: 'true'
overwrite: 'ifSourceNewer'

# Create an MD5 hash of each file, and save the hash as the Content-MD5 property of the destination blob or file.
# Only available when uploading.
# Default: None
put-md5: NULL
```
This would translate to the passing the azcopy cli `--put-md5` and `--overwrite 'ifSourceNewer`. These are passed to azpype as kwargs which are then appropriately parsed to construct the final command.

### Copy

Perhaps the most important interface and the primary workhorse command.

Basic Usage

```python
from azpype.commands.copy import Copy

#Syntax
#Copy('file-system-source','blob-storage-destination', **kwargs).execute()

azure_storage_account = "my_storage_account"
blob_container="my_container"
optional_container_path=""

destination = f"https://{azure_storage_account}.blob.core.windows.net/{blob_container}/{optional_container_path}"

source = "./test_payload"

Copy(source, destination).execute()
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