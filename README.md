# YAHAHA

### Cloud Computing Team Project ![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)

YAHAHA is a secondary E-market platform for students to circulate things on campus. Whereas currently students have to buy a lot of things, such as furniture, books when coming to new campus, YAHAHA lets students bypass the frustration of picking out inexpensive furniture with good quality that is the right for them. 

Our secondary E-market platform is based on [AWS web services](https://aws.amazon.com/) together with [common market transaction dataset](https://github.com/Hermionee/yahaha/blob/master/Recommender/Market_Basket_Optimisation.csv) which lists several transactions each containing real items user bought together, so it will not only help students find cheap items but also help recommend relevant items.  

In particular, the platform has a login page which authorizes the identity of the students. After that, student can input the keyword of his/her wanted item and get a series of results. Then students can negotiate the price with the seller for a certain item if he/she determines to buy. After chekcing out, the buyer will receive an e-mail showing the e-mail address of the seller to set up a pickup location. Finally, the platform has an NLP assistant which can help student buyer to decide if there are relevant items on sale on our platform. When there are no relevant items on sale, we will record the buyer's phone number and when some one uploads the item, the perspective buyer will receive an SMS telling him/her that the item is available. When there are items avaible, we will tell the buyer the website address of the item so user can just click it and see the details.

## Run: <br />
```
The project was shut down at the end of 2018. We are trying to incorporate more functions. But the 'Recommender' function is isolate from the web services and is done prior to the implementation of the system. It consisted of three association rule mining algorithm: apriori, eclat and FPgrowth, which all aim to find the associated frequent itemsets with high confidence.

To run the algorithms, download the 'Recommender' folder. Enter the directory in your terminal. The algorithms are all writtern in python3. Use python (or python3) command:(take eclat.py for example)

python eclat.py <input data file path> --output <output file path> -s <min_support_value> -c <min_confidence_value> -f rule

The input data file format is in horizontal format, namely for each row, the transaction and bought items are recorded:
------------------------------------------------------------
Transactions |                          Items               
------------------------------------------------------------
    t1       | a, b, c
------------------------------------------------------------
    t2       | a
------------------------------------------------------------
    t3       | a, b, d
------------------------------------------------------------
    t4       | b, c
------------------------------------------------------------
```
js files are not available here because it contains API key information.
***Technologies and tools used: AWS Cognito, Rekognition, ElasticSearch, Lex, VPC, SQS, SNS, DynamoDB, HTML, CSS, S3, Javascript
