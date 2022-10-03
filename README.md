# product_taxonomy

[UNDER DEVELOPMENT] - this project is still on early stage of development

Matches a product description to user defined taxonomy (or google taxonomy). 

v0.1 (Current):
- Use simple text match. User specify categories and queries in file. Algo use some weightening to searh for the best category.


Why I was interested in this problem:
- Many pretrained Neural Network model require long text in product description field. In my case product was described in very short sentences, more like information that you see in shop receipts.
- I didn't want and didn't have time to train neural network on my data. Ideally I was interested to start from smth more simple like labeling categories based on "bayesian probability".
- Without neural nets dependencies it is possible in future to move project to pyspark.
- I didn't have any labeled data. So I needed to start from basic text-matching algos to build sample for later model training. 
- Most taxonomy matchers which use text search are not well performance optimized. I am using caching and vector computations whenever is possible.
- Idea was to give user 'yaml' like config which would have all queries required to split products categories. Categories used in google_taxonomy were very detailed for me.



This project is inspired by this repositories:
https://github.com/BernhardWenzel/google-taxonomy-matcher