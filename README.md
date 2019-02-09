# Past2Present

Transform past to present in English sentences so that past tense becomes present tense and all other tenses stay the same. The transformation is accomplished using standard NLP libraries together with some intricate reasoning based on patterns in empirical data. Accuracy is demonstrated using a test suite. Mixed tenses joined by conjunction are not supported. ("I read yesterday and today read the same book.")

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
