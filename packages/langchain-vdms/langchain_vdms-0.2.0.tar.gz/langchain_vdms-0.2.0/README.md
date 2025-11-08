# Langchain VDMS

![GitHub License](https://img.shields.io/github/license/IntelLabs/langchain-vdms)

This package contains the [VDMS](https://github.com/IntelLabs/vdms) integration package for LangChain:

- [langchain-vdms](https://pypi.org/project/langchain-vdms/) - An integration between LangChain and VDMS which enables retrievers and vector search for AI applications.

## Installation

```bash
pip install -U langchain-vdms
```

<!-- And you should configure credentials by setting the following environment variables:

* TODO: fill this out -->


## VDMS vector database

The ``VDMS`` class exposes the VDMS vector store.

```python
from langchain_vdms import VDMS
```
<br>

The ``VDMS_Client`` function connects to VDMS server using VDMS client.

```python
from langchain_vdms.vectorstores import VDMS_Client
```
<br>

The ``VDMS_Utils`` class exposes a utility with helpful functions related to VDMS.

```python
from langchain_vdms.vectorstores import VDMS_Utils
```

## Example Usage
This example initiates the VDMS vector store and uses the VDMS Client to connect to a VDMS server on `localhost` using port `55555`.
```python
from langchain_vdms.vectorstores import VDMS, VDMS_Client

embeddings = ... # use a LangChain Embeddings class

vectorstore_client = VDMS_Client("localhost", 55555)
vectorstore = VDMS(
    client=vectorstore_client,
    collection_name="foo",
    embedding=embeddings,
    engine="FaissFlat",
    distance_strategy="L2",
)
```
See additional usage [here](https://python.langchain.com/docs/integrations/vectorstores/vdms/).


## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](/CONTRIBUTING.md) for guidelines.


## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.
