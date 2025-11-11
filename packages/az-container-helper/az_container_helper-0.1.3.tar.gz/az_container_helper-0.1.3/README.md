# az-container-helper

Helper classes and methods for using Azure services from inside a local Docker container.

Why another helper package for azure? Well, I found none that addresses the issue 
that it is not possible to access Azure Services from inside a local Docker container, see

- [[FEATURE REQ] DefaultAzureCredential for local docker testing](https://github.com/Azure/azure-sdk-for-net/issues/19167)

This is unfortunate, because it makes running your Python app inside a local container (e.g. for testing) impossible, 
if it uses Azure Services. The workarounds from the github issue only work, if you install the azure cli tools inside 
your container, which will not only increase the container size by a huge amount, but the cli tools are also strictly 
unnecessary when running your container on the Azure cloud. 

Therefor this package offers some minimal wrapper classes and utils around the default Python Azure SDK, so you can use 
Azure services in your Python app also from inside a local container. 

## Usage

### Retrieving credentials

To retrieve credentials for your app you can use a wrapper function in your Python app

    from az_container_helper import get_credentials
    
    credentials = get_credentials()

It will first try to read an existing access token from the ACCESS_TOKEN env variable.
If no existing token is found it will fall back to standard DefaultAzureCredential workflow.

To make use of that wrapper when running in a local docker container first generate an access token 
for your azure service (e.g. for a key vault) using the az cli tools and export it as ACCESS_TOKEN env variable.

    az login
    export ACCESS_TOKEN=$(az account get-access-token --resource https://vault.azure.net --output tsv)

Then you can run your app inside a local docker container and inject the token as env variable in the container

    docker run -e ACCESS_TOKEN=$ACCESS_TOKEN your-image

### Retrieving secrets from an Azure KeyVault

To conveniently access secret from an Azure KeyVault, this package offers a wrapper class.
The usage is quite simple. Here is this example we retrieve an api key from the Azure Key Vault
and use it to initialize an OpenAI client.

    from pathlib import Path
    from az_container_helper.keyvault import KeyVault
    from openai import AzureOpenAI

    kv_url = "https://<your-keyvault-name>.vault.azure.net"
    secrets_path = Path.cwd() / ".secrets"

    kv = KeyVault(kv_url, secrets_path = secrets_path)

    apikey = kv.get_secret("<name-of-secret>")

    openai_client = AzureOpenAI(api_key=apikey.get_secret_valu()...)
    
Our KeyVault class makes use of the `get_credentials()` function. So to connect to the KeyVault from your local 
container you can inject an ACCESS_TOKEN as shown above. 

However in case you cannot create an ACCESS_TOKEN locally (e.g. because you are not allowed to install az cli tools on
your developers machine) you simply can't access the KeyVault from your local machine. In that case our KeyVault class
will try to read secrets from a `.secrets` file, so this file acts an alternative local KeyVault. The format of the file
is simply

    name_of_secret=value_of_secret
    name_of_secret_2=value_of_secret_2
    ...

This file can simply be copied into your local DockerContainer in the working directory of the application. 
With that you can run your app inside a local container even without any local access to the Azure KeyVault.

> [!WARNING]
> Never commit the .secrets file into any versioning system and don't put it into your production container. 






