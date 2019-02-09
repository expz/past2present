# Past2Present

Transform English sentences so that past tense becomes present tense.

This project has two parts.

1. Transform sentences using Apache Beam locally or alternatively using Google Dataflow (Google's version of Beam) in the cloud.

    This has an example of running a job on Apache Beam/Google Dataflow using NLP libraries `spacy` and `benepar`. Not all classes are serializable, and this has an example workaround of creating custom serializable classes.

2. Transform sentences using Spark by running on Google Dataproc (Google's version of Spark) in the cloud. [INCOMPLETE]

## How it works

See the documentation in the subfolders. Run it on a document, and it will parse it into sentences and write them in the form:
```
< There was a girl.
> There is a girl.
```
